"""
LLM Client for HOLO-POLY agents.
Supports Gemini 2.0 Flash with fallback to stub mode for testing.
"""

import os
import json
import logging
import random
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Using stub mode.")


class BaseLLMClient(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        """Generate a response from the LLM."""
        pass

    def parse_json_response(self, response: str) -> Optional[dict]:
        """Extract JSON from LLM response."""
        # Try to find JSON in the response
        response = response.strip()

        # Handle markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()

        # Try to parse as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass

        logger.warning(f"Could not parse JSON from response: {response[:100]}")
        return None


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None
    ):
        if not GEMINI_AVAILABLE:
            raise RuntimeError("google-generativeai package not installed")

        self.model_name = model
        api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        logger.info(f"Initialized Gemini client with model: {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        """Generate a response from Gemini."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1000,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return '{"action": "PASS", "reasoning": "API error"}'


class StubLLMClient(BaseLLMClient):
    """
    Stub LLM client for testing without API.
    Uses rule-based decisions based on archetype.
    """

    def __init__(self, strategy: str = "random"):
        self.strategy = strategy
        logger.info(f"Using stub LLM client with strategy: {strategy}")

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        """Generate a stub response based on context."""
        # Parse the game state from prompt to make somewhat intelligent decisions
        decision = self._make_decision(prompt, system_prompt)
        return json.dumps(decision)

    def _make_decision(self, prompt: str, system_prompt: str) -> dict:
        """Make a decision based on archetype and game state."""
        archetype = self._extract_archetype(system_prompt)

        # Detect decision type from prompt
        if "BUY_DECISION" in prompt or "Option to buy" in prompt.lower():
            return self._decide_buy(prompt, archetype)
        elif "MARKET_ACTIONS" in prompt:
            return self._decide_market(prompt, archetype)
        else:
            return {"action": "PASS", "reasoning": "No action needed"}

    def _extract_archetype(self, system_prompt: str) -> str:
        """Extract archetype from system prompt."""
        system_prompt_lower = system_prompt.lower()
        if "slumlord" in system_prompt_lower:
            return "slumlord"
        elif "squatter" in system_prompt_lower:
            return "squatter"
        elif "flipper" in system_prompt_lower:
            return "flipper"
        elif "developer" in system_prompt_lower:
            return "developer"
        return "default"

    def _decide_buy(self, prompt: str, archetype: str) -> dict:
        """Decide whether to buy a property."""
        # Extract balance and price from prompt if possible
        buy_probability = {
            "slumlord": 0.9,    # Aggressive buyer
            "squatter": 0.1,   # Almost never buys
            "flipper": 0.7,    # Opportunistic
            "developer": 0.6,  # Selective
            "default": 0.5,
        }.get(archetype, 0.5)

        if random.random() < buy_probability:
            return {
                "action": "BUY_PROPERTY",
                "reasoning": f"As a {archetype}, this looks like a good opportunity"
            }
        return {
            "action": "PASS",
            "reasoning": f"As a {archetype}, I'm passing on this one"
        }

    def _decide_market(self, prompt: str, archetype: str) -> dict:
        """Decide on market actions (valuation changes, Harberger buys)."""
        # Simplified: Just occasionally adjust valuations
        if archetype == "slumlord":
            # Tend to raise valuations
            if random.random() < 0.3:
                return {
                    "action": "SET_VALUATION",
                    "params": {"valuation_change": "increase"},
                    "reasoning": "Raising valuations to maximize rent"
                }

        elif archetype == "flipper":
            # Set moderate valuations for resale
            if random.random() < 0.4:
                return {
                    "action": "SET_VALUATION",
                    "params": {"valuation_change": "moderate"},
                    "reasoning": "Setting valuation for quick resale"
                }

        return {"action": "PASS", "reasoning": "No market action this turn"}


class LLMClient:
    """
    Factory class that creates appropriate LLM client.
    Uses Gemini if available, otherwise falls back to stub.
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        stub_mode: bool = False,
        stub_strategy: str = "random"
    ):
        self.stub_mode = stub_mode

        if stub_mode or not GEMINI_AVAILABLE:
            self.client = StubLLMClient(strategy=stub_strategy)
        else:
            try:
                self.client = GeminiClient(model=model)
            except (ValueError, RuntimeError) as e:
                logger.warning(f"Could not initialize Gemini: {e}. Using stub.")
                self.client = StubLLMClient(strategy=stub_strategy)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        """Generate a response."""
        return self.client.generate(prompt, system_prompt, temperature)

    def parse_json_response(self, response: str) -> Optional[dict]:
        """Parse JSON from response."""
        return self.client.parse_json_response(response)


def load_prompt(archetype: str) -> str:
    """Load the prompt file for an archetype."""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_file = prompt_dir / f"{archetype.lower()}.txt"

    if prompt_file.exists():
        return prompt_file.read_text()

    logger.warning(f"Prompt file not found: {prompt_file}")
    return f"You are a {archetype} player in HOLO-POLY."
