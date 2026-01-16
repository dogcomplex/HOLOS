#!/usr/bin/env python3
"""
HOLO-POLY: A Harberger Tax Monopoly Simulation
Main entry point for running games.
"""

import argparse
import logging
import yaml
import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from kernel.models import GameConfig
from kernel.game import Game
from kernel.board_data import BOARD_TILES, is_purchasable
from agents.llm_client import LLMClient
from agents.agent import AgentManager
from ledger.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("holopoly")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {}

    with open(path) as f:
        return yaml.safe_load(f)


def setup_database(config: GameConfig, db: Database):
    """Initialize database with game setup."""
    # Create game record
    db.create_game(config.game_id, {
        "num_players": config.num_players,
        "num_boards": config.num_boards,
        "tax_timing": config.tax_timing.value,
        "dividend_timing": config.dividend_timing.value,
    })

    # Create players
    for i in range(config.num_players):
        player_id = f"player_{i}"
        archetype = config.archetypes[i % len(config.archetypes)]
        db.create_player(
            config.game_id,
            player_id,
            config.starting_balance,
            archetype
        )

    # Create properties for all boards
    for board_id in range(config.num_boards):
        for tile in BOARD_TILES:
            if is_purchasable(tile.id):
                db.create_property(
                    config.game_id,
                    board_id,
                    tile.id,
                    tile.name,
                    tile.tile_type,
                    tile.color_group,
                    tile.face_value
                )


def run_game(
    config_path: str = "config.yaml",
    db_path: Optional[str] = None,
    verbose: bool = False
) -> dict:
    """
    Run a complete HOLO-POLY game.

    Args:
        config_path: Path to configuration YAML
        db_path: Path to database file (optional)
        verbose: Enable verbose logging

    Returns:
        Game results dict
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    raw_config = load_config(config_path)
    config = GameConfig.from_yaml(raw_config)

    logger.info("=" * 60)
    logger.info("HOLO-POLY Game Starting")
    logger.info("=" * 60)
    logger.info(f"Game ID: {config.game_id}")
    logger.info(f"Players: {config.num_players}")
    logger.info(f"Boards: {config.num_boards}")
    logger.info(f"Tax Timing: {config.tax_timing.value}")
    logger.info(f"Dividend Timing: {config.dividend_timing.value}")
    logger.info(f"LLM Stub Mode: {config.llm_stub_mode}")
    logger.info("=" * 60)

    # Initialize database
    db_path = db_path or raw_config.get("output", {}).get("database_path", "holopoly.db")
    db = Database(db_path)
    setup_database(config, db)

    # Initialize LLM client
    llm_client = LLMClient(
        provider=config.llm_provider,
        model=config.llm_model,
        stub_mode=config.llm_stub_mode,
    )

    # Initialize agent manager
    agent_manager = AgentManager(llm_client)

    # Create agents for each player
    for i in range(config.num_players):
        player_id = f"player_{i}"
        archetype = config.archetypes[i % len(config.archetypes)]
        agent_manager.create_agent(player_id, archetype)

    # Create game with agent callback
    game = Game(
        config=config,
        agent_callback=agent_manager.agent_callback
    )

    # Run game
    logger.info("Starting game loop...")
    results = game.run_game()

    # Save final state
    db.save_game_state(config.game_id, game.state)

    # Log transactions
    for tx in game.transaction_log:
        db.log_transaction(config.game_id, tx)

    # Get stats
    stats = db.get_game_stats(config.game_id)

    # Close database
    db.close()

    # Print results
    logger.info("=" * 60)
    logger.info("GAME OVER")
    logger.info("=" * 60)
    logger.info(f"Turns played: {results['turns']}")
    logger.info(f"Winner: {results['winner']}")
    logger.info(f"Transactions: {results['transactions']}")
    logger.info("")
    logger.info("Final Standings:")
    for i, standing in enumerate(results["standings"], 1):
        logger.info(
            f"  {i}. {standing['id']} ({standing['archetype']}): "
            f"${standing['net_worth']} net worth, "
            f"{standing['properties']} properties, "
            f"Status: {standing['status']}"
        )
    logger.info("")
    logger.info(f"Transaction Stats: {stats['transaction_stats']}")
    logger.info(f"Ownership Changes: {stats['ownership_changes']}")
    logger.info(f"Bankruptcies: {stats['bankruptcies']}")

    # Report token usage
    from agents.llm_client import token_tracker
    usage = token_tracker.get_usage()
    logger.info(f"LLM Token Usage: {usage['total_tokens']:,} tokens in {usage['total_calls']} calls")
    logger.info(f"Token Budget Remaining: {usage['remaining']:,} / {usage['limit']:,}")
    logger.info("=" * 60)

    return {
        "results": results,
        "stats": stats,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HOLO-POLY: Harberger Tax Monopoly Simulation"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "-d", "--database",
        default=None,
        help="Path to database file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    # Override seed if provided
    if args.seed is not None:
        import random
        random.seed(args.seed)

    try:
        results = run_game(
            config_path=args.config,
            db_path=args.database,
            verbose=args.verbose,
        )
        return 0
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Game error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
