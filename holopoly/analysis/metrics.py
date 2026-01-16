"""
Metrics and analysis for HOLO-POLY games.
"""

from typing import List, Dict, Any
from collections import defaultdict
import json


class GameMetrics:
    """
    Calculate and analyze game metrics.

    Metrics:
    - Gini coefficient (wealth inequality)
    - Property turnover rate
    - Average valuation trends
    - Archetype performance
    """

    def __init__(self, transactions: List[dict], final_state: dict):
        self.transactions = transactions
        self.final_state = final_state

    def calculate_gini(self, values: List[float]) -> float:
        """
        Calculate Gini coefficient for a list of values.
        0 = perfect equality, 1 = perfect inequality
        """
        if not values or len(values) < 2:
            return 0.0

        values = sorted(values)
        n = len(values)
        total = sum(values)

        if total == 0:
            return 0.0

        # Calculate Gini using the relative mean difference formula
        cumsum = 0
        for i, v in enumerate(values):
            cumsum += (2 * (i + 1) - n - 1) * v

        return cumsum / (n * total)

    def wealth_gini(self) -> float:
        """Calculate Gini coefficient of final wealth distribution."""
        standings = self.final_state.get("standings", [])
        net_worths = [s.get("net_worth", 0) for s in standings]
        return self.calculate_gini(net_worths)

    def property_turnover_rate(self) -> float:
        """
        Calculate how often properties changed hands.
        Higher = more dynamic market.
        """
        purchases = sum(
            1 for tx in self.transactions
            if tx.get("phase") in ("PURCHASE", "HARBERGER_BUY")
        )
        total_turns = self.final_state.get("results", {}).get("turns", 1)

        return purchases / total_turns if total_turns > 0 else 0

    def harberger_buy_rate(self) -> float:
        """Percentage of property changes that were Harberger buys."""
        purchases = [
            tx for tx in self.transactions
            if tx.get("phase") in ("PURCHASE", "HARBERGER_BUY")
        ]

        if not purchases:
            return 0.0

        harberger_buys = sum(
            1 for tx in purchases
            if tx.get("phase") == "HARBERGER_BUY"
        )

        return harberger_buys / len(purchases)

    def archetype_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by archetype."""
        standings = self.final_state.get("standings", [])

        by_archetype = defaultdict(list)
        for standing in standings:
            archetype = standing.get("archetype", "Unknown")
            by_archetype[archetype].append(standing)

        results = {}
        for archetype, players in by_archetype.items():
            net_worths = [p["net_worth"] for p in players]
            results[archetype] = {
                "count": len(players),
                "avg_net_worth": sum(net_worths) / len(net_worths) if net_worths else 0,
                "survived": sum(1 for p in players if p["status"] == "ACTIVE"),
                "bankruptcies": sum(1 for p in players if p["status"] == "BANKRUPT"),
            }

        return results

    def tax_vs_dividend_ratio(self) -> float:
        """Ratio of tax paid to dividends received."""
        tax_paid = sum(
            tx.get("amount", 0) for tx in self.transactions
            if tx.get("phase") == "TAX"
        )
        dividends = sum(
            tx.get("amount", 0) for tx in self.transactions
            if tx.get("phase") == "DIVIDEND"
        )

        return tax_paid / dividends if dividends > 0 else float("inf")

    def valuation_trends(self) -> Dict[str, List[int]]:
        """Track valuation changes over time."""
        valuation_changes = [
            tx for tx in self.transactions
            if tx.get("phase") == "VALUATION_CHANGE"
        ]

        by_turn = defaultdict(list)
        for tx in valuation_changes:
            turn = tx.get("turn", 0)
            details = tx.get("details", {})
            if isinstance(details, str):
                details = json.loads(details)
            new_val = details.get("new_valuation", 0)
            by_turn[turn].append(new_val)

        return dict(by_turn)

    def generate_report(self) -> Dict[str, Any]:
        """Generate a complete metrics report."""
        return {
            "wealth_inequality": {
                "gini": self.wealth_gini(),
            },
            "market_dynamics": {
                "property_turnover_rate": self.property_turnover_rate(),
                "harberger_buy_rate": self.harberger_buy_rate(),
            },
            "economics": {
                "tax_dividend_ratio": self.tax_vs_dividend_ratio(),
            },
            "archetype_performance": self.archetype_performance(),
            "game_summary": {
                "total_turns": self.final_state.get("results", {}).get("turns", 0),
                "winner": self.final_state.get("results", {}).get("winner"),
                "total_transactions": len(self.transactions),
            },
        }


def analyze_game(db, game_id: str) -> Dict[str, Any]:
    """
    Analyze a completed game from the database.

    Args:
        db: Database instance
        game_id: ID of the game to analyze

    Returns:
        Metrics report dict
    """
    transactions = db.get_transactions(game_id)
    stats = db.get_game_stats(game_id)
    game = db.get_game(game_id)

    # Reconstruct final state info
    players = db.get_players(game_id)
    standings = []
    for p in players:
        # Calculate net worth
        props = [
            prop for prop in db.get_properties(game_id)
            if prop.get("owner_id") == p["player_id"]
        ]
        valuation = sum(prop.get("valuation", 0) for prop in props)
        standings.append({
            "id": p["player_id"],
            "archetype": p["archetype"],
            "balance": p["balance"],
            "net_worth": p["balance"] + valuation,
            "properties": len(props),
            "status": p["status"],
        })

    final_state = {
        "results": {
            "turns": game.get("total_turns", 0) if game else 0,
            "winner": game.get("winner_id") if game else None,
        },
        "standings": sorted(standings, key=lambda x: x["net_worth"], reverse=True),
        "stats": stats,
    }

    metrics = GameMetrics(transactions, final_state)
    return metrics.generate_report()
