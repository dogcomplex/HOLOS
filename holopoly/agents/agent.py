"""
Agent implementation for HOLO-POLY.
Each agent wraps an LLM client and makes decisions based on game state.
"""

import json
import logging
from typing import Dict, Any, Optional, List

from .llm_client import LLMClient, load_prompt
from ..kernel.models import Player, Action, ActionType, PropertyId

logger = logging.getLogger(__name__)


class Agent:
    """
    An AI agent that plays HOLO-POLY.

    Uses an LLM to make decisions based on:
    - Current game state (with hidden opponent balances)
    - Archetype personality/strategy
    - Game rules
    """

    def __init__(
        self,
        player_id: str,
        archetype: str,
        llm_client: LLMClient,
        config: dict = None
    ):
        self.player_id = player_id
        self.archetype = archetype
        self.llm_client = llm_client
        self.config = config or {}

        # Load archetype prompt
        self.system_prompt = load_prompt(archetype)

        # Decision history for context
        self.history: List[dict] = []
        self.max_history = self.config.get("max_history", 20)

        logger.info(f"Created agent {player_id} with archetype {archetype}")

    def make_decision(
        self,
        game_view: dict,
        decision_type: str,
        context: dict = None
    ) -> Optional[dict]:
        """
        Make a decision based on game state.

        Args:
            game_view: The filtered game state for this player
            decision_type: Type of decision (BUY_DECISION, MARKET_ACTIONS, etc.)
            context: Additional context for the decision

        Returns:
            Decision dict with action and params
        """
        context = context or {}

        # Build prompt
        prompt = self._build_prompt(game_view, decision_type, context)

        # Get LLM response
        response = self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=self.config.get("temperature", 0.7)
        )

        # Parse response
        decision = self.llm_client.parse_json_response(response)

        if decision:
            # Validate and log
            decision = self._validate_decision(decision, game_view, decision_type)
            self._record_history(game_view, decision_type, decision)

        return decision

    def _build_prompt(
        self,
        game_view: dict,
        decision_type: str,
        context: dict
    ) -> str:
        """Build the prompt for the LLM."""
        # Game rules summary
        rules = self._get_rules_summary(game_view)

        # Current state
        state_summary = self._summarize_state(game_view)

        # Recent history
        history_summary = self._summarize_history()

        # Decision-specific instructions
        if decision_type == "BUY_DECISION":
            instructions = self._get_buy_instructions(context)
        elif decision_type == "MARKET_ACTIONS":
            instructions = self._get_market_instructions(game_view)
        else:
            instructions = "Decide on your next action."

        prompt = f"""
{rules}

CURRENT GAME STATE:
{state_summary}

{history_summary}

DECISION REQUIRED: {decision_type}
{instructions}

Respond with valid JSON only:
{{"action": "ACTION_NAME", "params": {{}}, "reasoning": "brief explanation"}}

Valid actions: ROLL, BUY_PROPERTY, SET_VALUATION, BUILD_HOUSE, HARBERGER_BUY, PASS
"""
        return prompt

    def _get_rules_summary(self, game_view: dict) -> str:
        """Get a summary of the game rules."""
        timing = game_view.get("timing_mode", {})
        return f"""
HOLO-POLY RULES:
- Tax: 10% of your total property valuations ({timing.get('tax', 'on_go')})
- Rent: 10% of property valuation when someone lands on it
- Harberger: Anyone can buy your property at your declared price (forced sale)
- Dividend: Share of tax pot distributed to all players ({timing.get('dividend', 'on_go')})
- Cash is PRIVATE - you don't know opponents' exact balances
- Bankruptcy: Balance < 0 at any point = game over for you
"""

    def _summarize_state(self, game_view: dict) -> str:
        """Summarize the game state for the prompt."""
        me = game_view.get("me", {})
        opponents = game_view.get("opponents", [])

        # My status
        my_props = me.get("portfolio", [])
        total_val = sum(p.get("valuation", 0) for p in my_props)
        my_tax = int(total_val * 0.1)

        summary = f"""
Turn: {game_view.get('turn', 0)}
Community Pot: ${game_view.get('community_pot', 0)}

YOUR STATUS:
- Balance: ${me.get('balance', 0)}
- Position: Tile {me.get('position', 0)} on Board {me.get('board', 0)}
- Properties: {len(my_props)} (Total Valuation: ${total_val}, Tax/GO: ${my_tax})
"""

        if my_props:
            summary += "\nYour Properties:\n"
            for p in my_props:
                summary += f"  - {p.get('name')}: Val=${p.get('valuation', 0)}, Houses={p.get('houses', 0)}\n"

        # Opponents
        summary += f"\nOPPONENTS ({len(opponents)} active):\n"
        for opp in opponents:
            opp_props = opp.get("portfolio", [])
            opp_val = sum(p.get("valuation", 0) for p in opp_props)
            summary += f"  - {opp.get('id')}: {opp.get('status')} | {len(opp_props)} properties (Val: ${opp_val})\n"

        return summary

    def _summarize_history(self) -> str:
        """Summarize recent decision history."""
        if not self.history:
            return ""

        summary = "RECENT HISTORY:\n"
        for h in self.history[-5:]:  # Last 5 decisions
            summary += f"  Turn {h.get('turn', '?')}: {h.get('action', 'PASS')}\n"

        return summary

    def _get_buy_instructions(self, context: dict) -> str:
        """Get instructions for buy decision."""
        property_info = context.get("property", {})
        return f"""
You landed on an UNOWNED property:
- Name: {property_info.get('name', 'Unknown')}
- Face Value: ${property_info.get('face_value', 0)}
- Color Group: {property_info.get('color_group', 'N/A')}

Should you buy it?
- If you buy, you'll pay ${property_info.get('face_value', 0)} to the bank
- Your initial valuation will equal the purchase price
- You'll owe 10% tax on the valuation each GO pass

To buy, respond: {{"action": "BUY_PROPERTY", "reasoning": "..."}}
To pass, respond: {{"action": "PASS", "reasoning": "..."}}
"""

    def _get_market_instructions(self, game_view: dict) -> str:
        """Get instructions for market actions."""
        me = game_view.get("me", {})
        my_props = me.get("portfolio", [])

        instructions = """
MARKET PHASE - Choose ONE action:

1. SET_VALUATION - Change a property's declared value
   {{"action": "SET_VALUATION", "params": {{"property_id": [board, tile], "valuation": 500}}, "reasoning": "..."}}

2. HARBERGER_BUY - Force-buy an opponent's property at their declared price
   {{"action": "HARBERGER_BUY", "params": {{"property_id": [board, tile]}}, "reasoning": "..."}}

3. BUILD_HOUSE - Build a house on a monopoly property
   {{"action": "BUILD_HOUSE", "params": {{"property_id": [board, tile]}}, "reasoning": "..."}}

4. PASS - Take no action
   {{"action": "PASS", "reasoning": "..."}}
"""

        if my_props:
            instructions += "\nYour properties you can modify:\n"
            for p in my_props:
                instructions += f"  - [{p.get('board', 0)}, {p.get('tile', 0)}] {p.get('name')}: Val=${p.get('valuation', 0)}\n"

        return instructions

    def _validate_decision(
        self,
        decision: dict,
        game_view: dict,
        decision_type: str
    ) -> dict:
        """Validate and fix the decision if needed."""
        action = decision.get("action", "PASS").upper()

        # Ensure action is valid
        valid_actions = ["ROLL", "BUY_PROPERTY", "SET_VALUATION",
                        "BUILD_HOUSE", "HARBERGER_BUY", "PASS"]
        if action not in valid_actions:
            logger.warning(f"Invalid action {action}, defaulting to PASS")
            decision["action"] = "PASS"

        # For buy decisions, only allow BUY_PROPERTY or PASS
        if decision_type == "BUY_DECISION":
            if action not in ["BUY_PROPERTY", "PASS"]:
                decision["action"] = "PASS"

        return decision

    def _record_history(
        self,
        game_view: dict,
        decision_type: str,
        decision: dict
    ):
        """Record decision in history."""
        self.history.append({
            "turn": game_view.get("turn", 0),
            "type": decision_type,
            "action": decision.get("action"),
            "params": decision.get("params"),
        })

        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]


class AgentManager:
    """
    Manages all agents in a game.
    Provides the callback interface for the Game class.
    """

    def __init__(self, llm_client: LLMClient, config: dict = None):
        self.llm_client = llm_client
        self.config = config or {}
        self.agents: Dict[str, Agent] = {}

    def create_agent(self, player_id: str, archetype: str) -> Agent:
        """Create and register an agent."""
        agent = Agent(
            player_id=player_id,
            archetype=archetype,
            llm_client=self.llm_client,
            config=self.config
        )
        self.agents[player_id] = agent
        return agent

    def get_decision(
        self,
        player: Player,
        game_view: dict,
        decision_type: str,
        context: dict
    ) -> Optional[dict]:
        """
        Get a decision from the appropriate agent.
        This is the callback used by the Game class.
        """
        if player.id not in self.agents:
            # Create agent on demand
            self.create_agent(player.id, player.archetype)

        agent = self.agents[player.id]
        return agent.make_decision(game_view, decision_type, context)

    def agent_callback(
        self,
        player: Player,
        game_view: dict,
        decision_type: str,
        context: dict
    ) -> Optional[dict]:
        """Callback function to pass to Game class."""
        return self.get_decision(player, game_view, decision_type, context)
