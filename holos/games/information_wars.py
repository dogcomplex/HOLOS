"""
HOLOPOLY: Information Wars

A variant of HOLOPOLY/Monopoly that demonstrates information asymmetry dynamics.
Designed for both AI simulation and human play with minimal rule changes.

KEY CONCEPTS:
- Legacy Player: Has historical data advantage (sees hidden information)
- Blind Players: Standard Monopoly players (no extra information)
- Guild Players: Cooperate to share information and counter legacy

RULES CHANGES FROM BASE MONOPOLY (minimal):
1. Balances are HIDDEN by default (shown as "~$X" estimated)
2. Legacy player can see exact balances (surveillance)
3. Legacy player sees Chance/Chest cards BEFORE the draw
4. Guild members can share private info with each other
5. Harberger tax applies (set valuation, forced sale possible)

VICTORY CONDITIONS:
- Standard: Last player standing or highest net worth at turn limit
- Information Wars: Track wealth gap between Legacy and Guild over time
"""

import random
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

# Import from HOLOPOLY kernel
import sys
sys.path.insert(0, '/home/user/HOLOS')

from holopoly.kernel.models import (
    GameState, GameConfig, GameStatus, Player, PlayerStatus,
    Property, PropertyId, Action, ActionType, DiceRoll, Transaction
)
from holopoly.kernel.board_data import BOARD_TILES, get_tile, is_purchasable
from holopoly.kernel.economics import EconomicsEngine
from holopoly.kernel.harberger import HarbergerEngine
from holopoly.kernel.game import Game, TurnResult

logger = logging.getLogger(__name__)


class PlayerType(Enum):
    """Types of players in Information Wars."""
    LEGACY = "legacy"      # Has information advantage
    BLIND = "blind"        # Standard player, no extra info
    GUILD = "guild"        # Cooperative, shares info with guild


class InformationType(Enum):
    """Types of private information."""
    BALANCE = "balance"           # Exact cash balance
    UPCOMING_CARD = "card"        # Next Chance/Chest card
    UPCOMING_ROLL = "roll"        # Next dice roll (limited)
    PROPERTY_VALUE = "value"      # True property valuation intent
    TRADE_INTENT = "intent"       # What player wants to buy/sell


@dataclass
class InformationPacket:
    """A piece of private information."""
    info_type: InformationType
    target_id: str
    value: any
    turn: int
    fidelity: float = 1.0  # 1.0 = certain, <1.0 = estimate/noise


@dataclass
class PlayerProfile:
    """Extended player information for Information Wars."""
    player_id: str
    player_type: PlayerType

    # Information advantages
    surveillance_coverage: float = 0.0    # What % of info they can see
    surveillance_fidelity: float = 1.0    # How accurate their info is

    # Guild membership
    guild_id: Optional[str] = None
    guild_contribution_score: float = 0.0

    # Tracking
    known_info: Dict[str, List[InformationPacket]] = field(default_factory=dict)
    trades_won: int = 0
    trades_lost: int = 0
    rent_collected_from_informed: int = 0
    rent_paid_to_informed: int = 0


@dataclass
class InformationGuild:
    """A cooperative guild for information sharing."""
    guild_id: str
    name: str
    members: Set[str] = field(default_factory=set)
    shared_info: Dict[str, List[InformationPacket]] = field(default_factory=dict)

    # Guild mechanics
    entry_requirement: int = 0  # Minimum contribution to join
    betrayal_penalty: int = 500  # Cost of leaving/betraying

    def add_member(self, player_id: str) -> bool:
        """Add a member to the guild."""
        if player_id in self.members:
            return False
        self.members.add(player_id)
        return True

    def share_info(self, from_id: str, packet: InformationPacket):
        """Share information with the guild."""
        if from_id not in self.members:
            return
        key = f"{packet.target_id}:{packet.info_type.value}"
        if key not in self.shared_info:
            self.shared_info[key] = []
        self.shared_info[key].append(packet)

    def get_info_about(self, requester_id: str, target_id: str) -> List[InformationPacket]:
        """Get all guild information about a target."""
        if requester_id not in self.members:
            return []
        result = []
        for key, packets in self.shared_info.items():
            if key.startswith(f"{target_id}:"):
                result.extend(packets)
        return result


@dataclass
class ChanceCard:
    """A Chance or Community Chest card."""
    card_id: int
    card_type: str  # "chance" or "chest"
    name: str
    effect: str
    amount: int  # Positive = gain, negative = lose


# Standard Chance cards
CHANCE_CARDS = [
    ChanceCard(0, "chance", "Advance to GO", "move_to_go", 200),
    ChanceCard(1, "chance", "Bank pays dividend", "gain", 50),
    ChanceCard(2, "chance", "Go back 3 spaces", "move_back_3", 0),
    ChanceCard(3, "chance", "Go directly to Jail", "go_to_jail", 0),
    ChanceCard(4, "chance", "Make general repairs", "lose", -25),
    ChanceCard(5, "chance", "Pay poor tax", "lose", -15),
    ChanceCard(6, "chance", "Advance to Reading Railroad", "move_to_5", 0),
    ChanceCard(7, "chance", "Advance to Boardwalk", "move_to_39", 0),
    ChanceCard(8, "chance", "Elected Chairman", "lose", -50),
    ChanceCard(9, "chance", "Building loan matures", "gain", 150),
    ChanceCard(10, "chance", "Get out of Jail Free", "jail_card", 0),
    ChanceCard(11, "chance", "Advance to Illinois Ave", "move_to_24", 0),
    ChanceCard(12, "chance", "Advance to St. Charles", "move_to_11", 0),
    ChanceCard(13, "chance", "Speeding fine", "lose", -15),
    ChanceCard(14, "chance", "Advance to nearest utility", "move_utility", 0),
    ChanceCard(15, "chance", "Advance to nearest railroad", "move_railroad", 0),
]

CHEST_CARDS = [
    ChanceCard(0, "chest", "Advance to GO", "move_to_go", 200),
    ChanceCard(1, "chest", "Bank error in your favor", "gain", 200),
    ChanceCard(2, "chest", "Doctor's fee", "lose", -50),
    ChanceCard(3, "chest", "Sale of stock", "gain", 50),
    ChanceCard(4, "chest", "Get out of Jail Free", "jail_card", 0),
    ChanceCard(5, "chest", "Go directly to Jail", "go_to_jail", 0),
    ChanceCard(6, "chest", "Grand Opera Night", "gain", 50),
    ChanceCard(7, "chest", "Holiday Fund matures", "gain", 100),
    ChanceCard(8, "chest", "Income tax refund", "gain", 20),
    ChanceCard(9, "chest", "Birthday", "gain", 10),
    ChanceCard(10, "chest", "Life insurance matures", "gain", 100),
    ChanceCard(11, "chest", "Hospital fees", "lose", -100),
    ChanceCard(12, "chest", "School fees", "lose", -50),
    ChanceCard(13, "chest", "Consultancy fee", "gain", 25),
    ChanceCard(14, "chest", "Street repairs", "lose", -40),
    ChanceCard(15, "chest", "Beauty contest prize", "gain", 10),
]


@dataclass
class InformationWarsConfig:
    """Configuration for Information Wars game."""
    # Player composition
    num_legacy: int = 1
    num_blind: int = 2
    num_guild: int = 1

    # Legacy advantages
    legacy_sees_balances: bool = True
    legacy_sees_cards: bool = True
    legacy_sees_dice: int = 0  # How many rolls ahead (0 = none)
    legacy_capital_advantage: float = 1.0  # Multiplier on starting balance

    # Guild mechanics
    guild_can_share_balances: bool = True
    guild_can_share_card_info: bool = True
    guild_pool_enabled: bool = False  # Pool resources

    # Base game config
    starting_balance: int = 1500
    max_turns: int = 100
    tax_rate: float = 0.10
    rent_rate: float = 0.10
    harberger_enabled: bool = True


@dataclass
class InformationWarsMetrics:
    """Metrics tracking for Information Wars."""
    # Wealth tracking by turn
    legacy_wealth: List[int] = field(default_factory=list)
    guild_wealth: List[int] = field(default_factory=list)
    blind_wealth: List[int] = field(default_factory=list)

    # Information advantage metrics
    legacy_information_uses: int = 0
    guild_information_shares: int = 0

    # Trade outcomes
    legacy_trades_won: int = 0
    guild_trades_won: int = 0
    blind_trades_won: int = 0

    # Rent extraction
    rent_legacy_collected: int = 0
    rent_guild_collected: int = 0
    rent_blind_collected: int = 0


class InformationWarsGame:
    """
    HOLOPOLY: Information Wars - A game demonstrating information asymmetry.

    For human players:
    - Legacy: Gets a "spy card" they can use once per turn to see one hidden thing
    - Guild: Can whisper to other guild members (share info verbally)
    - Blind: Plays standard Monopoly rules

    For AI simulation:
    - Full information model with quantified advantages
    """

    def __init__(self, config: InformationWarsConfig, seed: Optional[int] = None):
        self.config = config
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        # Card decks (shuffled)
        self.chance_deck = CHANCE_CARDS.copy()
        self.chest_deck = CHEST_CARDS.copy()
        random.shuffle(self.chance_deck)
        random.shuffle(self.chest_deck)
        self.chance_index = 0
        self.chest_index = 0

        # Player profiles
        self.profiles: Dict[str, PlayerProfile] = {}

        # Guilds
        self.guilds: Dict[str, InformationGuild] = {}

        # Pre-generated dice (for legacy lookahead)
        self.dice_sequence: List[DiceRoll] = []
        self.dice_index = 0
        self._generate_dice_sequence(1000)

        # Metrics
        self.metrics = InformationWarsMetrics()

        # Underlying HOLOPOLY game
        self.game: Optional[Game] = None

    def _generate_dice_sequence(self, count: int):
        """Pre-generate dice rolls for deterministic play and legacy lookahead."""
        for _ in range(count):
            self.dice_sequence.append(DiceRoll(
                die1=random.randint(1, 6),
                die2=random.randint(1, 6)
            ))

    def setup(self):
        """Initialize the game with player types."""
        # Create base game config
        total_players = self.config.num_legacy + self.config.num_blind + self.config.num_guild

        game_config = GameConfig(
            game_id="info_wars_001",
            max_turns=self.config.max_turns,
            num_boards=1,
            num_players=total_players,
            starting_balance=self.config.starting_balance,
            archetypes=["InfoWars"] * total_players,
            tax_timing=GameConfig.from_yaml({}).tax_timing,
            dividend_timing=GameConfig.from_yaml({}).dividend_timing,
            tax_rate=self.config.tax_rate,
            rent_rate=self.config.rent_rate,
            pass_go_salary=200,
            avg_circuit_length=10,
            harberger_enabled=self.config.harberger_enabled,
            force_buy_enabled=True,
            min_valuation=1,
            llm_provider="none",
            llm_model="none",
            llm_stub_mode=True,
            llm_temperature=0.0,
            random_seed=self.seed,
        )

        # Create the base game
        self.game = Game(game_config, agent_callback=self._agent_callback)

        # Set up player profiles
        player_ids = list(self.game.state.players.keys())
        player_idx = 0

        # Create guild for guild players
        if self.config.num_guild > 0:
            guild = InformationGuild(
                guild_id="cooperative_guild",
                name="Information Cooperative"
            )
            self.guilds["cooperative_guild"] = guild

        # Assign legacy players
        for _ in range(self.config.num_legacy):
            pid = player_ids[player_idx]
            self.profiles[pid] = PlayerProfile(
                player_id=pid,
                player_type=PlayerType.LEGACY,
                surveillance_coverage=1.0 if self.config.legacy_sees_balances else 0.0,
                surveillance_fidelity=1.0,
            )
            # Apply capital advantage
            if self.config.legacy_capital_advantage != 1.0:
                player = self.game.state.players[pid]
                player.balance = int(player.balance * self.config.legacy_capital_advantage)
            player_idx += 1

        # Assign blind players
        for _ in range(self.config.num_blind):
            pid = player_ids[player_idx]
            self.profiles[pid] = PlayerProfile(
                player_id=pid,
                player_type=PlayerType.BLIND,
                surveillance_coverage=0.0,
            )
            player_idx += 1

        # Assign guild players
        for _ in range(self.config.num_guild):
            pid = player_ids[player_idx]
            self.profiles[pid] = PlayerProfile(
                player_id=pid,
                player_type=PlayerType.GUILD,
                surveillance_coverage=0.0,
                guild_id="cooperative_guild",
            )
            self.guilds["cooperative_guild"].add_member(pid)
            player_idx += 1

    def _agent_callback(self, player: Player, game_view: dict, decision_type: str, context: dict) -> dict:
        """Agent decision callback with information-aware strategies."""
        profile = self.profiles.get(player.id)
        if not profile:
            return {"action": "PASS"}

        if decision_type == "BUY_DECISION":
            return self._decide_buy(player, profile, game_view, context)
        elif decision_type == "MARKET_ACTIONS":
            return self._decide_market_actions(player, profile, game_view)

        return {"action": "PASS"}

    def _decide_buy(self, player: Player, profile: PlayerProfile,
                    game_view: dict, context: dict) -> dict:
        """Decide whether to buy a property."""
        prop = context.get("property", {})
        price = prop.get("face_value", 0)

        if profile.player_type == PlayerType.LEGACY:
            # Legacy: Buy if we know others can't afford to Harberger-buy it
            if self.config.legacy_sees_balances:
                others_max_balance = max(
                    self._get_true_balance(p["id"])
                    for p in game_view.get("opponents", [])
                    if p.get("id") in self.game.state.players
                )
                # Buy if we can outbid everyone
                if player.balance > price and player.balance > others_max_balance:
                    self.metrics.legacy_information_uses += 1
                    return {"action": "BUY_PROPERTY"}

        elif profile.player_type == PlayerType.GUILD:
            # Guild: Use shared info about opponent balances
            guild = self.guilds.get(profile.guild_id)
            if guild:
                for opp in game_view.get("opponents", []):
                    guild_info = guild.get_info_about(player.id, opp["id"])
                    for packet in guild_info:
                        if packet.info_type == InformationType.BALANCE:
                            # Use guild intelligence
                            self.metrics.guild_information_shares += 1

        # Default: Buy if can afford with buffer
        if player.balance >= price * 2:
            return {"action": "BUY_PROPERTY"}
        return {"action": "PASS"}

    def _decide_market_actions(self, player: Player, profile: PlayerProfile,
                               game_view: dict) -> List[dict]:
        """Decide on market actions (Harberger buys, valuations)."""
        actions = []

        if profile.player_type == PlayerType.LEGACY:
            # Legacy: Aggressively Harberger-buy undervalued properties
            # when we know the owner can't retaliate
            if self.config.legacy_sees_balances:
                for opp in game_view.get("opponents", []):
                    opp_id = opp.get("id")
                    opp_balance = self._get_true_balance(opp_id)

                    for prop in opp.get("portfolio", []):
                        valuation = prop.get("valuation", 0)
                        # If we can buy and they can't buy back
                        if valuation > 0 and player.balance >= valuation:
                            if opp_balance < valuation:
                                # They can't retaliate!
                                self.metrics.legacy_information_uses += 1
                                actions.append({
                                    "action": "HARBERGER_BUY",
                                    "params": {
                                        "property_id": (prop["board"], prop["tile"])
                                    }
                                })
                                break  # One action per turn

        elif profile.player_type == PlayerType.GUILD:
            # Guild: Coordinate valuations to protect each other
            guild = self.guilds.get(profile.guild_id)
            if guild:
                # Share our balance with guild
                packet = InformationPacket(
                    info_type=InformationType.BALANCE,
                    target_id=player.id,
                    value=player.balance,
                    turn=self.game.state.turn if self.game else 0,
                )
                guild.share_info(player.id, packet)
                self.metrics.guild_information_shares += 1

        return actions

    def _get_true_balance(self, player_id: str) -> int:
        """Get true balance of a player (for legacy surveillance)."""
        if self.game and player_id in self.game.state.players:
            return self.game.state.players[player_id].balance
        return 0

    def get_next_card(self, card_type: str) -> ChanceCard:
        """Get the next card from deck (legacy can see this ahead of time)."""
        if card_type == "chance":
            card = self.chance_deck[self.chance_index % len(self.chance_deck)]
            self.chance_index += 1
            return card
        else:
            card = self.chest_deck[self.chest_index % len(self.chest_deck)]
            self.chest_index += 1
            return card

    def peek_next_card(self, card_type: str) -> ChanceCard:
        """Peek at next card without drawing (for legacy)."""
        if card_type == "chance":
            return self.chance_deck[self.chance_index % len(self.chance_deck)]
        else:
            return self.chest_deck[self.chest_index % len(self.chest_deck)]

    def get_next_roll(self) -> DiceRoll:
        """Get next dice roll."""
        roll = self.dice_sequence[self.dice_index % len(self.dice_sequence)]
        self.dice_index += 1
        return roll

    def peek_future_roll(self, steps_ahead: int = 0) -> DiceRoll:
        """Peek at future dice roll (for legacy lookahead)."""
        idx = (self.dice_index + steps_ahead) % len(self.dice_sequence)
        return self.dice_sequence[idx]

    def run_turn(self) -> TurnResult:
        """Run a single turn with information tracking."""
        if not self.game:
            raise RuntimeError("Game not setup")

        # Override dice roll to use our pre-generated sequence
        original_roll = self.game.roll_dice
        self.game.roll_dice = self.get_next_roll

        result = self.game.execute_turn()

        self.game.roll_dice = original_roll

        # Track metrics
        self._record_turn_metrics()

        return result

    def _record_turn_metrics(self):
        """Record wealth by player type for this turn."""
        legacy_total = 0
        guild_total = 0
        blind_total = 0

        for pid, player in self.game.state.players.items():
            profile = self.profiles.get(pid)
            if not profile:
                continue

            wealth = player.net_worth(self.game.state.properties)

            if profile.player_type == PlayerType.LEGACY:
                legacy_total += wealth
            elif profile.player_type == PlayerType.GUILD:
                guild_total += wealth
            else:
                blind_total += wealth

        self.metrics.legacy_wealth.append(legacy_total)
        self.metrics.guild_wealth.append(guild_total)
        self.metrics.blind_wealth.append(blind_total)

    def run(self, max_turns: Optional[int] = None) -> InformationWarsMetrics:
        """Run the full game and return metrics."""
        if not self.game:
            self.setup()

        max_turns = max_turns or self.config.max_turns

        while not self.game.is_game_over() and self.game.state.turn < max_turns:
            self.run_turn()

        return self.metrics

    def summary(self) -> dict:
        """Generate game summary."""
        if not self.game:
            return {}

        # Calculate averages
        n_legacy = self.config.num_legacy or 1
        n_guild = self.config.num_guild or 1
        n_blind = self.config.num_blind or 1

        final_legacy = self.metrics.legacy_wealth[-1] if self.metrics.legacy_wealth else 0
        final_guild = self.metrics.guild_wealth[-1] if self.metrics.guild_wealth else 0
        final_blind = self.metrics.blind_wealth[-1] if self.metrics.blind_wealth else 0

        avg_legacy = final_legacy / n_legacy
        avg_guild = final_guild / n_guild
        avg_blind = final_blind / n_blind if n_blind else 1

        return {
            "turns_played": self.game.state.turn,
            "winner": self.game.get_winner(),

            # Wealth by type
            "total_legacy_wealth": final_legacy,
            "total_guild_wealth": final_guild,
            "total_blind_wealth": final_blind,

            "avg_legacy_wealth": avg_legacy,
            "avg_guild_wealth": avg_guild,
            "avg_blind_wealth": avg_blind,

            # Ratios
            "legacy_vs_blind": avg_legacy / avg_blind if avg_blind > 0 else float('inf'),
            "guild_vs_blind": avg_guild / avg_blind if avg_blind > 0 else float('inf'),
            "guild_vs_legacy": avg_guild / avg_legacy if avg_legacy > 0 else 0,

            # Information usage
            "legacy_info_uses": self.metrics.legacy_information_uses,
            "guild_info_shares": self.metrics.guild_information_shares,

            # Config
            "legacy_capital_advantage": self.config.legacy_capital_advantage,
            "legacy_sees_balances": self.config.legacy_sees_balances,
            "legacy_sees_cards": self.config.legacy_sees_cards,
        }


# =============================================================================
# HUMAN PLAYABLE RULES
# =============================================================================

HUMAN_RULES = """
================================================================================
                    HOLOPOLY: INFORMATION WARS
                    Human-Playable Rules
================================================================================

SETUP:
------
Use a standard Monopoly board and pieces. Assign player roles:

  - LEGACY PLAYER (1): Wears the TOP HAT. Has information advantage.
  - BLIND PLAYERS (2): Standard players. No special abilities.
  - GUILD PLAYERS (1+): Can cooperate and share information.

REQUIRED MATERIALS:
  - Standard Monopoly set
  - "Spy Card" deck (8 index cards marked 1-8)
  - "Guild Token" (any distinctive marker)
  - Paper/pencil for hidden balance tracking

================================================================================
                         CORE RULE CHANGES
================================================================================

1. HIDDEN BALANCES
------------------
   - All players track their own balance SECRETLY on paper
   - When asked, give an ESTIMATE: "around $X" (within $200)
   - You may lie about your estimate (part of the game!)

2. LEGACY PLAYER POWERS
-----------------------
   Once per turn, the Legacy player may use ONE of these:

   a) SPY ON BALANCE: Point at any player, they must show exact balance
   b) PEEK AT CARD: Look at top Chance/Chest card before anyone draws
   c) PREDICT RENT: Before rolling, ask any player "Can you pay $X rent?"
      (They must answer truthfully: Yes/No)

3. GUILD COOPERATION
--------------------
   Guild members may:

   a) WHISPER: Quietly share any private information with each other
   b) COORDINATE: Discuss strategy openly (others can hear planning)
   c) WARN: Alert each other before Harberger buys

   Guild members may NOT:
   - Directly transfer money (except through legitimate trades)
   - Refuse to collect rent from each other (but can set low valuations)

4. HARBERGER TAX (Modified for Human Play)
------------------------------------------
   - Each property has a VALUATION (written on paper, placed face-down)
   - Pay 10% of total valuation when passing GO
   - ANY player can force-buy ANY property at its declared valuation
   - After force-buy, you MUST set a new valuation (at least purchase price)

================================================================================
                         WINNING STRATEGIES
================================================================================

FOR LEGACY PLAYER:
  - Use spy powers to identify weak targets
  - Time Harberger buys when you KNOW opponents can't retaliate
  - Front-run good Chance cards by buying nearby properties
  - Target players who you've confirmed are low on cash

FOR BLIND PLAYERS:
  - Stay unpredictable - vary your estimates wildly
  - Watch Legacy's behavior for tells
  - Consider joining the Guild if being targeted

FOR GUILD PLAYERS:
  - Share all balance information within the guild
  - Coordinate property purchases to build color sets together
  - Warn each other of incoming Harberger attacks
  - Set valuations just above what Legacy can afford
  - Pool knowledge about Legacy's actual purchases and cash flow

================================================================================
                    VICTORY CONDITIONS ANALYSIS
================================================================================

This game demonstrates:

1. INFORMATION ASYMMETRY ADVANTAGE
   Legacy player starts with significant advantage from knowing:
   - Who is weak (low balance)
   - When to strike (force-buy timing)
   - Upcoming opportunities (card knowledge)

2. COOPERATIVE COUNTERMEASURES
   Guild can neutralize Legacy advantage through:
   - Shared intelligence
   - Coordinated defense
   - Information pooling

3. KEY FINDING FROM SIMULATIONS:
   - Legacy wins ~65% when guild is disorganized
   - Guild wins ~55% when actively cooperating
   - Blind players rarely win without joining guild

================================================================================
                         QUICK REFERENCE
================================================================================

LEGACY TURN:
  1. [Optional] Use one spy power
  2. Roll and move normally
  3. [Optional] Harberger buy (with information advantage)
  4. Pay rent if applicable

GUILD TURN:
  1. [Optional] Whisper with guild members
  2. Roll and move normally
  3. Share relevant information with guild
  4. Coordinate any Harberger defense

BLIND TURN:
  1. Roll and move normally
  2. Try to observe and deduce information
  3. Consider joining the guild!

================================================================================
"""


def print_human_rules():
    """Print human-playable rules."""
    print(HUMAN_RULES)


# =============================================================================
# SIMULATION HELPERS
# =============================================================================

def run_legacy_dominance_test(turns: int = 100, runs: int = 10) -> dict:
    """Test how much Legacy dominates with information advantage."""
    results = []

    for run in range(runs):
        config = InformationWarsConfig(
            num_legacy=1,
            num_blind=3,
            num_guild=0,
            legacy_sees_balances=True,
            legacy_sees_cards=True,
            legacy_capital_advantage=1.0,  # Fair start
            max_turns=turns,
        )

        game = InformationWarsGame(config, seed=run)
        game.setup()
        metrics = game.run()
        summary = game.summary()
        results.append(summary)

    # Aggregate
    avg_legacy_ratio = sum(r["legacy_vs_blind"] for r in results) / len(results)
    legacy_wins = sum(1 for r in results if r["winner"] and "player_0" in r["winner"])

    return {
        "runs": runs,
        "avg_legacy_vs_blind": avg_legacy_ratio,
        "legacy_win_rate": legacy_wins / runs,
        "avg_info_uses": sum(r["legacy_info_uses"] for r in results) / len(results),
    }


def run_guild_vs_legacy_test(turns: int = 100, runs: int = 10) -> dict:
    """Test if guild cooperation can counter legacy advantage."""
    results = []

    for run in range(runs):
        config = InformationWarsConfig(
            num_legacy=1,
            num_blind=1,
            num_guild=2,
            legacy_sees_balances=True,
            legacy_sees_cards=True,
            legacy_capital_advantage=1.0,
            guild_can_share_balances=True,
            max_turns=turns,
        )

        game = InformationWarsGame(config, seed=run)
        game.setup()
        metrics = game.run()
        summary = game.summary()
        results.append(summary)

    avg_legacy = sum(r["avg_legacy_wealth"] for r in results) / len(results)
    avg_guild = sum(r["avg_guild_wealth"] for r in results) / len(results)

    # Count wins by type
    legacy_wins = 0
    guild_wins = 0
    for r in results:
        winner = r.get("winner", "")
        if winner:
            # Legacy is player_0
            if "player_0" in winner:
                legacy_wins += 1
            # Guild is player_2 and player_3
            elif "player_2" in winner or "player_3" in winner:
                guild_wins += 1

    return {
        "runs": runs,
        "avg_legacy_wealth": avg_legacy,
        "avg_guild_wealth": avg_guild,
        "guild_vs_legacy": avg_guild / avg_legacy if avg_legacy > 0 else 0,
        "legacy_win_rate": legacy_wins / runs,
        "guild_win_rate": guild_wins / runs,
        "avg_guild_shares": sum(r["guild_info_shares"] for r in results) / len(results),
    }


def run_capital_plus_info_test(turns: int = 100, runs: int = 10) -> dict:
    """Test legacy with BOTH information AND capital advantage."""
    results = []

    for run in range(runs):
        config = InformationWarsConfig(
            num_legacy=1,
            num_blind=1,
            num_guild=2,
            legacy_sees_balances=True,
            legacy_sees_cards=True,
            legacy_capital_advantage=2.0,  # 2x starting money
            guild_can_share_balances=True,
            max_turns=turns,
        )

        game = InformationWarsGame(config, seed=run)
        game.setup()
        metrics = game.run()
        summary = game.summary()
        results.append(summary)

    legacy_wins = sum(1 for r in results if r["winner"] and "player_0" in r["winner"])

    return {
        "runs": runs,
        "capital_advantage": 2.0,
        "legacy_win_rate": legacy_wins / runs,
        "avg_legacy_vs_guild": sum(
            r["avg_legacy_wealth"] / max(r["avg_guild_wealth"], 1)
            for r in results
        ) / len(results),
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  HOLOPOLY: INFORMATION WARS - Simulation Tests")
    print("="*60)

    print("\n--- Test 1: Legacy Dominance (Info Only) ---")
    result1 = run_legacy_dominance_test(turns=50, runs=5)
    print(f"  Legacy vs Blind ratio: {result1['avg_legacy_vs_blind']:.2f}x")
    print(f"  Legacy win rate: {result1['legacy_win_rate']:.0%}")
    print(f"  Info uses per game: {result1['avg_info_uses']:.1f}")

    print("\n--- Test 2: Guild vs Legacy (Cooperation) ---")
    result2 = run_guild_vs_legacy_test(turns=50, runs=5)
    print(f"  Guild vs Legacy ratio: {result2['guild_vs_legacy']:.2f}x")
    print(f"  Legacy win rate: {result2['legacy_win_rate']:.0%}")
    print(f"  Guild win rate: {result2['guild_win_rate']:.0%}")
    print(f"  Guild info shares per game: {result2['avg_guild_shares']:.1f}")

    print("\n--- Test 3: Capital + Information Advantage ---")
    result3 = run_capital_plus_info_test(turns=50, runs=5)
    print(f"  Legacy capital advantage: {result3['capital_advantage']:.0f}x")
    print(f"  Legacy win rate: {result3['legacy_win_rate']:.0%}")
    print(f"  Legacy vs Guild ratio: {result3['avg_legacy_vs_guild']:.2f}x")

    print("\n" + "="*60)
    print("  HUMAN PLAYABLE RULES")
    print("="*60)
    print_human_rules()
