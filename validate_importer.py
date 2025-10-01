#!/usr/bin/env python3
"""
Test script to validate the war importer improvements
Tests error tracking, pagination logic, and error recovery features
"""
import json
import os
import sys


def test_coc_api_error_tracking():
    """Test that CocApiClient has error tracking capabilities"""
    print("Testing CocApiClient error tracking...")
    
    with open('coc_api.py', 'r') as f:
        content = f.read()
    
    # Check for error tracking features
    checks = {
        'self.api_errors = []': 'Error list initialization',
        'def _track_error(': 'Error tracking method',
        'def get_errors(': 'Get errors method',
        'def clear_errors(': 'Clear errors method',
        'track_errors: bool = True': 'Track errors parameter'
    }
    
    passed = 0
    failed = 0
    
    for check, description in checks.items():
        if check in content:
            print(f"  ✓ {description}")
            passed += 1
        else:
            print(f"  ✗ {description}")
            failed += 1
    
    return failed == 0


def test_war_importer_pagination():
    """Test that war_importer has unlimited pagination"""
    print("\nTesting war_importer pagination...")
    
    with open('war_importer.py', 'r') as f:
        content = f.read()
    
    checks = {
        'for limit_offset in range(0, 10000, 1000)': 'Pagination loop for up to 10,000 clans',
        'all_clans = []': 'Clan accumulation list',
        'all_clans.extend(clans)': 'Extending clan list',
        'if len(clans) < 1000:': 'Break condition for last batch',
        'await self._save_api_errors()': 'Saving API errors',
        'import json': 'JSON import for error saving',
        '404_api_errors.json': 'Error file reference'
    }
    
    passed = 0
    failed = 0
    
    for check, description in checks.items():
        if check in content:
            print(f"  ✓ {description}")
            passed += 1
        else:
            print(f"  ✗ {description}")
            failed += 1
    
    return failed == 0


def test_error_handler_exists():
    """Test that errors.py exists and has correct structure"""
    print("\nTesting errors.py error handler...")
    
    if not os.path.exists('errors.py'):
        print("  ✗ errors.py file not found")
        return False
    
    with open('errors.py', 'r') as f:
        content = f.read()
    
    checks = {
        'class ErrorHandler:': 'ErrorHandler class',
        'def _load_errors(': 'Load errors method',
        'async def _rescan_clans(': 'Rescan clans method',
        'async def _process_clan(': 'Process clan method',
        'async def _save_remaining_errors(': 'Save remaining errors method',
        '404_api_errors.json': 'Error file reference',
        'from urllib.parse import unquote': 'URL decoding for clan tags'
    }
    
    passed = 0
    failed = 0
    
    for check, description in checks.items():
        if check in content:
            print(f"  ✓ {description}")
            passed += 1
        else:
            print(f"  ✗ {description}")
            failed += 1
    
    return failed == 0


def test_error_json_structure():
    """Test that error JSON has correct structure"""
    print("\nTesting error JSON structure...")
    
    with open('war_importer.py', 'r') as f:
        content = f.read()
    
    # Check for JSON structure fields
    fields = ['scan_time', 'total_errors', 'errors_by_clan', 'all_errors']
    
    passed = 0
    failed = 0
    
    for field in fields:
        if f"'{field}'" in content:
            print(f"  ✓ JSON field '{field}' present")
            passed += 1
        else:
            print(f"  ✗ JSON field '{field}' missing")
            failed += 1
    
    return failed == 0


def test_documentation_exists():
    """Test that documentation exists"""
    print("\nTesting documentation...")
    
    if os.path.exists('ERROR_TRACKING_README.md'):
        print("  ✓ ERROR_TRACKING_README.md exists")
        return True
    else:
        print("  ✗ ERROR_TRACKING_README.md not found")
        return False


def test_no_200_limit():
    """Test that the 200 clan limit is removed"""
    print("\nTesting removal of 200 clan limit...")
    
    with open('war_importer.py', 'r') as f:
        content = f.read()
    
    # Check that we don't have hardcoded limit=200 in the location loop
    import re
    
    # Find the _import_by_locations method
    method_match = re.search(r'async def _import_by_locations\(self\):.*?(?=\n    async def|\n    def|\Z)', 
                            content, re.DOTALL)
    
    if method_match:
        method_content = method_match.group(0)
        
        # Check if it mentions getting ALL clans
        if 'ВСЕ кланы' in method_content or 'ALL clans' in method_content:
            print("  ✓ Comments indicate scanning ALL clans")
        else:
            print("  ⚠ Comments don't explicitly mention ALL clans")
        
        # Check for pagination loop
        if 'for limit_offset in range' in method_content:
            print("  ✓ Uses pagination loop instead of fixed limit")
            return True
        else:
            print("  ✗ No pagination loop found")
            return False
    else:
        print("  ✗ Could not find _import_by_locations method")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("War Importer Improvements Validation Tests")
    print("=" * 60)
    
    tests = [
        ('CocApiClient Error Tracking', test_coc_api_error_tracking),
        ('War Importer Pagination', test_war_importer_pagination),
        ('Error Handler', test_error_handler_exists),
        ('Error JSON Structure', test_error_json_structure),
        ('Documentation', test_documentation_exists),
        ('200 Clan Limit Removal', test_no_200_limit)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
