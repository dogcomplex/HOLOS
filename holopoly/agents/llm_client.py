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

# Global token tracking for failsafe
MAX_TOTAL_TOKENS = 100_000_000  # 100M token limit

class TokenLimitExceeded(Exception):
    """Raised when token limit is exceeded."""
    pass

class TokenTracker:
    """Track total tokens used across all LLM calls."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.total_tokens = 0
            cls._instance.total_calls = 0
        return cls._instance

    def add_tokens(self, input_tokens: int, output_tokens: int):
        """Add tokens to the running total."""
        added = input_tokens + output_tokens
        self.total_tokens += added
        self.total_calls += 1

        if self.total_tokens >= MAX_TOTAL_TOKENS:
            logger.error(f"TOKEN LIMIT EXCEEDED: {self.total_tokens:,} >= {MAX_TOTAL_TOKENS:,}")
            raise TokenLimitExceeded(
                f"Token limit of {MAX_TOTAL_TOKENS:,} exceeded. "
                f"Total used: {self.total_tokens:,} in {self.total_calls} calls."
            )

        if self.total_calls % 100 == 0:
            logger.info(f"Token usage: {self.total_tokens:,} / {MAX_TOTAL_TOKENS:,} ({self.total_calls} calls)")

    def get_usage(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "total_calls": self.total_calls,
            "limit": MAX_TOTAL_TOKENS,
            "remaining": MAX_TOTAL_TOKENS - self.total_tokens,
        }

# Global tracker instance
token_tracker = TokenTracker()

# Try to import requests for REST API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# For now, skip the problematic SDK and use REST API
GEMINI_AVAILABLE = REQUESTS_AVAILABLE


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
    """Client for Google Gemini API using REST API directly."""

    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(
        self,
        model: str = "gemini-3-flash-preview",
        api_key: Optional[str] = None
    ):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests package not installed")

        self.model_name = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        self.api_url = self.GEMINI_API_URL.format(model=model)
        logger.info(f"Initialized Gemini REST client with model: {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        """Generate a response from Gemini using REST API."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 1000,
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Gemini API error {response.status_code}: {response.text[:500]}")
                return '{"action": "PASS", "reasoning": "API error"}'

            data = response.json()

            # Extract text from response
            text = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    text = "".join(p.get("text", "") for p in parts)

            # Track token usage
            usage = data.get("usageMetadata", {})
            input_tokens = usage.get("promptTokenCount", len(full_prompt) // 4)
            output_tokens = usage.get("candidatesTokenCount", len(text) // 4)

            token_tracker.add_tokens(input_tokens, output_tokens)

            return text

        except TokenLimitExceeded:
            raise  # Re-raise token limit errors
        except requests.exceptions.Timeout:
            logger.error("Gemini API timeout")
            return '{"action": "PASS", "reasoning": "API timeout"}'
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
        model: str = "gemini-3-flash-preview",
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
