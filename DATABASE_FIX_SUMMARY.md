# Database Schema Fix - Summary

## Problem
The bot was experiencing two critical errors:
1. **Subscription Menu Error**: `no such column: amount` when accessing the subscription menu
2. **Building Monitor Error**: `no such table: building_trackers` when using the building monitor feature

## Root Cause
The `src/services/database.py` file had duplicate and incomplete database initialization code:
- The `init_db()` method had two different initialization sections (one complete, one incomplete)
- The incomplete section was missing the `amount` and `currency` columns in the subscriptions table
- The incomplete section was missing the `building_trackers` and `building_snapshots` tables entirely
- The incomplete section was missing the `notifications` table

## Solution Applied

### 1. Fixed `database.py`
- **Removed duplicate init_db code** (lines 203-349)
- **Added missing columns to subscriptions table**:
  - `amount REAL` - stores subscription payment amount
  - `currency TEXT DEFAULT 'RUB'` - stores currency code
  - `updated_at TEXT DEFAULT CURRENT_TIMESTAMP` - tracks updates
- **Added missing tables**:
  - `building_trackers` - tracks building upgrade monitoring per user/profile
  - `building_snapshots` - stores snapshots of building states
  - `notifications` - tracks notification preferences

### 2. Created Migration Script
Created `migrate_database.py` to:
- Add missing columns to existing databases
- Create missing tables in existing databases
- Handle safe migration without data loss
- Provide detailed logging of migration process

### 3. Testing
- Created comprehensive test suite (`test_database.py`)
- Verified all database operations work correctly
- Tested subscription creation with amount field
- Tested building tracker creation and retrieval
- All tests pass successfully

## Database Schema Changes

### Subscriptions Table (Fixed)
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    subscription_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    payment_id TEXT,
    amount REAL,                                    -- ADDED
    currency TEXT DEFAULT 'RUB',                    -- ADDED
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP       -- ADDED
);
```

### Building Trackers Table (Added)
```sql
CREATE TABLE building_trackers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    player_tag TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    last_check TEXT,
    UNIQUE(telegram_id, player_tag)
);
```

### Building Snapshots Table (Added)
```sql
CREATE TABLE building_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_tag TEXT NOT NULL,
    snapshot_time TEXT NOT NULL,
    buildings_data TEXT NOT NULL,
    UNIQUE(player_tag, snapshot_time)
);
```

### Notifications Table (Added)
```sql
CREATE TABLE notifications (
    telegram_id INTEGER PRIMARY KEY
);
```

## Files Modified
- `src/services/database.py` - Fixed init_db() method, removed duplicates
- `migrate_database.py` - New migration script for existing databases

## Files Created (Temporary)
- `test_database.py` - Test suite (not committed, excluded by .gitignore)

## How to Apply Fix

### For New Installations
Simply run the bot - the fixed `init_db()` will create the correct schema.

### For Existing Databases
Run the migration script:
```bash
python3 migrate_database.py
```

Or use the existing init script which will also work:
```bash
./init_database.sh
```

## Verification
After applying the fix, both features should work correctly:
- ✅ Subscription menu displays and processes payments with amounts
- ✅ Building monitor tracks and notifies about building upgrades

## Security
- No security vulnerabilities introduced
- CodeQL scan: 0 alerts
- Migration script handles errors gracefully
- No sensitive data exposed in logs
