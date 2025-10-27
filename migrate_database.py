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
            
            # Check and fix linked_clans table
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='linked_clans'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if table_exists:
                logger.info("Checking linked_clans table schema...")
                async with db.execute("PRAGMA table_info(linked_clans)") as cursor:
                    columns = await cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    # Check if we need to migrate from old schema
                    if 'linked_at' in column_names or 'is_active' in column_names:
                        logger.info("Migrating linked_clans table to new schema...")
                        # Create new table with correct schema
                        await db.execute("""
                            CREATE TABLE IF NOT EXISTS linked_clans_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                telegram_id INTEGER NOT NULL,
                                clan_tag TEXT NOT NULL,
                                clan_name TEXT NOT NULL,
                                slot_number INTEGER NOT NULL DEFAULT 1,
                                created_at TEXT NOT NULL,
                                UNIQUE(telegram_id, clan_tag)
                            )
                        """)
                        
                        # Copy data from old table
                        if 'linked_at' in column_names:
                            # Migrate from linked_at to created_at
                            await db.execute("""
                                INSERT OR IGNORE INTO linked_clans_new (id, telegram_id, clan_tag, clan_name, slot_number, created_at)
                                SELECT id, telegram_id, clan_tag, clan_name, 1, linked_at FROM linked_clans
                            """)
                        else:
                            # If no linked_at, use current timestamp
                            await db.execute("""
                                INSERT OR IGNORE INTO linked_clans_new (id, telegram_id, clan_tag, clan_name, slot_number, created_at)
                                SELECT id, telegram_id, clan_tag, clan_name, 1, datetime('now') FROM linked_clans
                            """)
                        
                        # Drop old table and rename new one
                        await db.execute("DROP TABLE linked_clans")
                        await db.execute("ALTER TABLE linked_clans_new RENAME TO linked_clans")
                        logger.info("✅ Migrated linked_clans table")
                    else:
                        logger.info("✅ linked_clans table schema is correct")
            else:
                logger.info("Creating linked_clans table...")
                await db.execute("""
                    CREATE TABLE linked_clans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_id INTEGER NOT NULL,
                        clan_tag TEXT NOT NULL,
                        clan_name TEXT NOT NULL,
                        slot_number INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL,
                        UNIQUE(telegram_id, clan_tag)
                    )
                """)
                logger.info("✅ Created linked_clans table")
            
            # Check and fix war_scan_requests table
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='war_scan_requests'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if table_exists:
                logger.info("Checking war_scan_requests table for request_date column...")
                async with db.execute("PRAGMA table_info(war_scan_requests)") as cursor:
                    columns = await cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if 'request_date' not in column_names:
                        logger.info("Adding request_date column to war_scan_requests...")
                        await db.execute("ALTER TABLE war_scan_requests ADD COLUMN request_date TEXT")
                        # Update existing rows with date extracted from created_at
                        await db.execute("""
                            UPDATE war_scan_requests 
                            SET request_date = date(created_at)
                            WHERE request_date IS NULL
                        """)
                        logger.info("✅ Added request_date column")
                    else:
                        logger.info("✅ request_date column already exists")
            
            # Check and migrate donation_snapshots to player_stats_snapshots
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='donation_snapshots'"
            ) as cursor:
                old_table_exists = await cursor.fetchone()
            
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='player_stats_snapshots'"
            ) as cursor:
                new_table_exists = await cursor.fetchone()
            
            if old_table_exists and not new_table_exists:
                logger.info("Migrating donation_snapshots to player_stats_snapshots...")
                # Create new table
                await db.execute("""
                    CREATE TABLE player_stats_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_tag TEXT NOT NULL,
                        snapshot_time TEXT NOT NULL,
                        donations INTEGER NOT NULL DEFAULT 0,
                        UNIQUE(player_tag, snapshot_time)
                    )
                """)
                
                # Try to migrate data if columns match
                try:
                    await db.execute("""
                        INSERT OR IGNORE INTO player_stats_snapshots (player_tag, snapshot_time, donations)
                        SELECT player_tag, snapshot_date, donations_given FROM donation_snapshots
                    """)
                    logger.info("✅ Migrated data from donation_snapshots")
                except Exception as e:
                    logger.warning(f"Could not migrate data: {e}")
                
                # Keep old table for safety, just rename it
                await db.execute("ALTER TABLE donation_snapshots RENAME TO donation_snapshots_backup")
                logger.info("✅ Created player_stats_snapshots table (old table renamed to backup)")
            elif not new_table_exists:
                logger.info("Creating player_stats_snapshots table...")
                await db.execute("""
                    CREATE TABLE player_stats_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_tag TEXT NOT NULL,
                        snapshot_time TEXT NOT NULL,
                        donations INTEGER NOT NULL DEFAULT 0,
                        UNIQUE(player_tag, snapshot_time)
                    )
                """)
                logger.info("✅ Created player_stats_snapshots table")
            else:
                logger.info("✅ player_stats_snapshots table already exists")
            
            # Check and create cwl_seasons table
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='cwl_seasons'"
            ) as cursor:
                table_exists = await cursor.fetchone()
            
            if not table_exists:
                logger.info("Creating cwl_seasons table...")
                await db.execute("""
                    CREATE TABLE cwl_seasons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        season_date TEXT NOT NULL UNIQUE,
                        bonus_results_json TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("✅ Created cwl_seasons table")
            else:
                logger.info("✅ cwl_seasons table already exists")
            
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
