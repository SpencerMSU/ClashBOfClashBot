#!/usr/bin/env python3
"""
Database migration script to fix schema issues
Adds missing columns and tables to existing database
"""
import asyncio
import aiosqlite
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_database():
    """Migrate database to fix schema issues"""
    # Use default database path
    db_path = os.getenv('DATABASE_PATH', 'clashbot.db')
    logger.info(f"Starting database migration for: {db_path}")
    
    try:
        async with aiosqlite.connect(db_path, timeout=30.0) as db:
            # Enable WAL mode for better concurrency
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA synchronous=NORMAL")
            
            # Check if subscriptions table exists
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if table_exists:
                logger.info("Subscriptions table exists, checking for 'amount' column...")
                
                # Check if amount column exists
                async with db.execute("PRAGMA table_info(subscriptions)") as cursor:
                    columns = await cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if 'amount' not in column_names:
                        logger.info("Adding 'amount' column to subscriptions table...")
                        await db.execute("ALTER TABLE subscriptions ADD COLUMN amount REAL")
                        logger.info("✅ Added 'amount' column")
                    else:
                        logger.info("✅ 'amount' column already exists")
                    
                    if 'currency' not in column_names:
                        logger.info("Adding 'currency' column to subscriptions table...")
                        await db.execute("ALTER TABLE subscriptions ADD COLUMN currency TEXT DEFAULT 'RUB'")
                        logger.info("✅ Added 'currency' column")
                    else:
                        logger.info("✅ 'currency' column already exists")
                    
                    if 'created_at' not in column_names:
                        logger.info("Adding 'created_at' column to subscriptions table...")
                        await db.execute("ALTER TABLE subscriptions ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
                        logger.info("✅ Added 'created_at' column")
                    else:
                        logger.info("✅ 'created_at' column already exists")
                    
                    if 'updated_at' not in column_names:
                        logger.info("Adding 'updated_at' column to subscriptions table...")
                        await db.execute("ALTER TABLE subscriptions ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
                        logger.info("✅ Added 'updated_at' column")
                    else:
                        logger.info("✅ 'updated_at' column already exists")
            else:
                logger.info("Subscriptions table does not exist, creating...")
                await db.execute("""
                    CREATE TABLE subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER NOT NULL UNIQUE,
                        subscription_type TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        is_active INTEGER NOT NULL DEFAULT 1,
                        payment_id TEXT,
                        amount REAL,
                        currency TEXT DEFAULT 'RUB',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("✅ Created subscriptions table")
            
            # Check if building_trackers table exists
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='building_trackers'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if not table_exists:
                logger.info("Creating building_trackers table...")
                await db.execute("""
                    CREATE TABLE building_trackers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER NOT NULL,
                        player_tag TEXT NOT NULL,
                        is_active INTEGER NOT NULL DEFAULT 0,
                        created_at TEXT NOT NULL,
                        last_check TEXT,
                        UNIQUE(telegram_id, player_tag)
                    )
                """)
                logger.info("✅ Created building_trackers table")
            else:
                logger.info("✅ building_trackers table already exists")
            
            # Check if building_snapshots table exists
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='building_snapshots'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if not table_exists:
                logger.info("Creating building_snapshots table...")
                await db.execute("""
                    CREATE TABLE building_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_tag TEXT NOT NULL,
                        snapshot_time TEXT NOT NULL,
                        buildings_data TEXT NOT NULL,
                        UNIQUE(player_tag, snapshot_time)
                    )
                """)
                logger.info("✅ Created building_snapshots table")
            else:
                logger.info("✅ building_snapshots table already exists")
            
            await db.commit()
            logger.info("🎉 Database migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(migrate_database())
    sys.exit(0 if success else 1)
