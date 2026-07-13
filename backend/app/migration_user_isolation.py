"""Alembic-style migration: add user_id columns for data isolation (Phase 5).

Run with: python backend/app/migration_user_isolation.py
"""
import asyncio
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "stock_monitor.db")

MIGRATIONS = [
    # Add user_id to watchlist_items
    "ALTER TABLE watchlist_items ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
    # Add user_id to alert_rules
    "ALTER TABLE alert_rules ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
    # Add user_id to alert_records
    "ALTER TABLE alert_records ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE",
    # Create backtest_results table
    """CREATE TABLE IF NOT EXISTS backtest_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        stock_code VARCHAR(10) NOT NULL,
        start_date VARCHAR(10) NOT NULL,
        end_date VARCHAR(10) NOT NULL,
        total_return FLOAT,
        win_rate FLOAT,
        max_drawdown FLOAT,
        sharpe_ratio FLOAT,
        trade_count INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    # Indexes for user-scoped queries
    "CREATE INDEX IF NOT EXISTS ix_watchlist_items_user_id ON watchlist_items(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_alert_rules_user_id ON alert_rules(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_alert_records_user_id ON alert_records(user_id)",
    "CREATE INDEX IF NOT EXISTS ix_backtest_results_user_id ON backtest_results(user_id)",
]


def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"[migration] DB not found at {DB_PATH}, skipping (auto-created on startup)")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        for sql in MIGRATIONS:
            try:
                conn.execute(sql)
                print(f"[migration] OK: {sql[:80]}...")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"[migration] SKIP (already applied): {sql[:80]}...")
                else:
                    raise
        conn.commit()
        print("[migration] User isolation migration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
