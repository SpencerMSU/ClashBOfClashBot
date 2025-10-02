# API Error Tracking and Unlimited Clan Scanning

## Overview

This update adds comprehensive error tracking and unlimited clan scanning capabilities to the war importer system.

## New Features

### 1. Unlimited Clan Scanning
- **Previous behavior**: Limited to top 200 clans per location
- **New behavior**: Attempts to scan ALL clans from each location (up to 10,000 per location)
- The importer now makes multiple API calls with pagination to get as many clans as possible

### 2. API Error Tracking
- All API errors (404, 403, timeouts, etc.) are now tracked during scanning
- Errors are saved to `404_api_errors.json` after each scan
- The error file includes:
  - Timestamp of each error
  - Endpoint that failed
  - HTTP status code
  - Error message
  - Errors grouped by clan tag for easy reference

### 3. Error Recovery Script (errors.py)
- New script to automatically rescan clans that had errors
- Loads `404_api_errors.json` and attempts to fetch data again
- Updates the error file with any remaining errors
- Provides detailed statistics on successful rescans

## Usage

### Running the War Importer (Top 10k Clans)
```bash
python3 scanners/war_importer.py
```

### Running the All Clans Importer (ALL Available Clans)
```bash
python3 all_importer.py
```

This will:
1. Scan ALL available clans from 200+ configured locations
2. Import war data to the database
3. Save any API errors to `all_clans_api_errors.json`

### Using the Standard War Importer
The standard war importer in `scanners/` directory scans top 10k clans from 20 main locations.
4. Log detailed progress to `war_importer.log`

### Running the Error Recovery Script
```bash
python3 errors.py
```

This will:
1. Load clans with errors from `404_api_errors.json`
2. Attempt to rescan each clan
3. Import any newly available war data
4. Update `404_api_errors.json` with remaining errors
5. Log detailed progress to `errors_rescan.log`

## Files

### Modified Files
- **coc_api.py**: Added error tracking to the API client
  - `api_errors` list to store all errors
  - `_track_error()` method to record errors
  - `get_errors()` method to retrieve error list
  - `clear_errors()` method to reset error list
  
- **war_importer.py**: Enhanced to scan unlimited clans and save errors
  - Pagination loop to get multiple batches of clans (up to 10,000 per location)
  - `_save_api_errors()` method to export errors to JSON
  - JSON import added

### New Files
- **errors.py**: Error recovery script
  - `ErrorHandler` class for managing error rescans
  - Methods to load, process, and save error data
  - Complete logging and statistics

## Error File Format (404_api_errors.json)

```json
{
  "scan_time": "2024-01-01T12:00:00",
  "total_errors": 42,
  "errors_by_clan": {
    "#CLANTAG1": [
      {
        "timestamp": "2024-01-01T12:00:00",
        "endpoint": "/clans/%23CLANTAG1/warlog",
        "status_code": 404,
        "error_message": "Resource not found"
      }
    ]
  },
  "all_errors": [...]
}
```

## Configuration

No additional configuration is needed. The system uses the existing `COC_API_TOKEN` from `config.py` or `api_tokens.txt`.

## API Limits

The implementation assumes infinite API limits as specified in requirements. If you encounter rate limiting:
1. The error will be tracked in `404_api_errors.json`
2. You can run `errors.py` later to retry
3. Consider adding delays between requests by uncommenting the sleep lines in the code

## Best Practices

1. **Run war_importer.py first**: This creates the initial database and error file
2. **Check 404_api_errors.json**: Review which clans had errors
3. **Run errors.py periodically**: Some errors may be temporary (server issues, maintenance, etc.)
4. **Monitor logs**: Check `war_importer.log` and `errors_rescan.log` for details

## Technical Details

### Pagination Strategy
The importer attempts to fetch up to 10,000 clans per location in batches of 1,000:
- If the API returns fewer than 1,000 clans, it stops (reached the end)
- If the API returns exactly 1,000, it requests the next batch
- This continues until no more clans are available or 10,000 limit is reached

### Error Types Tracked
- **404**: Resource not found (clan doesn't exist or war log is private)
- **403**: Authentication issues (invalid API key)
- **Timeouts**: Network or server timeouts
- **Other errors**: Any other HTTP errors or exceptions

### Database Integration
Both scripts use the existing `DatabaseService` to:
- Check if wars already exist in the database
- Import new war data
- Avoid duplicate imports

## Troubleshooting

**Q: The importer stops after 1000 clans**
A: Check if the API is returning fewer results. The code checks `len(clans) < 1000` to determine if it's the last batch.

**Q: All clans show 404 errors**
A: This might indicate:
- Clans have private war logs
- API authentication issues
- The clan tags are encoded incorrectly

**Q: errors.py shows "File not found"**
A: Run `war_importer.py` first to create the `404_api_errors.json` file.

**Q: Too many API calls**
A: Uncomment the `await asyncio.sleep()` lines in the code to add delays between requests.
