-- HOLO-POLY Database Schema
-- Supports multi-board universe with N players on M boards

-- Games table (supports multiple concurrent games)
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    config TEXT NOT NULL,              -- JSON blob of game configuration
    status TEXT DEFAULT 'ACTIVE',      -- ACTIVE, COMPLETED, ABORTED
    winner_id TEXT,
    total_turns INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Boards in the universe
CREATE TABLE IF NOT EXISTS boards (
    game_id TEXT NOT NULL,
    board_id INTEGER NOT NULL,
    PRIMARY KEY (game_id, board_id),
    FOREIGN KEY (game_id) REFERENCES games(id)
);

-- Players
CREATE TABLE IF NOT EXISTS players (
    game_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    balance INTEGER NOT NULL,
    current_board INTEGER NOT NULL DEFAULT 0,
    position INTEGER DEFAULT 0,        -- Tile position (0-39)
    status TEXT DEFAULT 'ACTIVE',      -- ACTIVE, BANKRUPT
    archetype TEXT,
    turns_played INTEGER DEFAULT 0,
    PRIMARY KEY (game_id, player_id),
    FOREIGN KEY (game_id) REFERENCES games(id)
);

-- Properties (each identified by game + board + tile)
CREATE TABLE IF NOT EXISTS properties (
    game_id TEXT NOT NULL,
    board_id INTEGER NOT NULL,
    tile_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    tile_type TEXT NOT NULL,           -- property, railroad, utility, tax, chance, chest, go, jail, etc.
    color_group TEXT,                  -- brown, light_blue, pink, orange, red, yellow, green, blue
    face_value INTEGER NOT NULL,       -- Original purchase price
    owner_id TEXT,                     -- NULL if unowned
    valuation INTEGER DEFAULT 0,       -- Harberger self-assessed value
    houses INTEGER DEFAULT 0,          -- 0-4 houses, 5 = hotel
    is_mortgaged INTEGER DEFAULT 0,
    PRIMARY KEY (game_id, board_id, tile_id),
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (game_id, owner_id) REFERENCES players(game_id, player_id)
);

-- Economic state per game
CREATE TABLE IF NOT EXISTS economy (
    game_id TEXT PRIMARY KEY,
    community_pot INTEGER DEFAULT 0,   -- Accumulated taxes for UBI
    total_tax_collected INTEGER DEFAULT 0,
    total_dividends_paid INTEGER DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES games(id)
);

-- Transaction log (immutable audit trail)
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL,
    turn INTEGER NOT NULL,
    phase TEXT,                        -- TAX, RENT, PURCHASE, DIVIDEND, HARBERGER_BUY, etc.
    from_id TEXT,                      -- Player or 'BANK' or 'POT'
    to_id TEXT,                        -- Player or 'BANK' or 'POT'
    amount INTEGER,
    property_board INTEGER,            -- For property transactions
    property_tile INTEGER,             -- For property transactions
    details TEXT,                      -- JSON blob for extra info
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id)
);

-- Turn history (for analysis)
CREATE TABLE IF NOT EXISTS turns (
    game_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    dice_roll TEXT,                    -- JSON: [die1, die2]
    start_position INTEGER,
    end_position INTEGER,
    start_board INTEGER,
    end_board INTEGER,
    passed_go INTEGER DEFAULT 0,
    action_taken TEXT,                 -- JSON blob of action
    llm_response TEXT,                 -- Raw LLM response for debugging
    PRIMARY KEY (game_id, turn_number),
    FOREIGN KEY (game_id) REFERENCES games(id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_properties_owner ON properties(game_id, owner_id);
CREATE INDEX IF NOT EXISTS idx_transactions_game_turn ON transactions(game_id, turn);
CREATE INDEX IF NOT EXISTS idx_players_status ON players(game_id, status);
