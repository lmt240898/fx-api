#!/usr/bin/env python3
"""
Script để chạy các test cho API /signal
"""

import subprocess
import sys
import os

def run_test(test_file):
    """Chạy một test file"""
    print(f"🚀 Running {test_file}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ Test {test_file} timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Signal API Test Runner")
    print("=" * 60)
    
    # Danh sách các test files
    test_files = [
        "tests/simple_signal_test.py",
        "tests/test_signal_api_cache.py"
    ]
    
    results = []
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_test(test_file)
            results.append((test_file, success))
            print(f"\n{'✅' if success else '❌'} {test_file}: {'PASSED' if success else 'FAILED'}")
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results.append((test_file, False))
        
        print("\n" + "=" * 60)
    
    # Tổng kết
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_file, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_file}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
