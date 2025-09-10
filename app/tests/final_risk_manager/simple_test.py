"""
Simple test script to validate RiskManagerService without complex dependencies
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Direct import to avoid package-level imports
sys.path.append(str(project_root / "app" / "services"))
sys.path.append(str(project_root / "app" / "utils"))

from risk_manager_service import RiskManagerService
from logger import Logger


def test_simple_case():
    """Test with a simple case"""
    print("Testing RiskManagerService with simple case...")
    
    # Create service
    service = RiskManagerService()
    
    # Simple test data
    test_params = {
        "proposed_signal_json": {
            "symbol": "EURUSD",
            "signal_type": "BUY",
            "order_type_proposed": "MARKET",
            "entry_price_proposed": 1.1000,
            "stop_loss_proposed": 1.0950,
            "take_profit_proposed": 1.1100,
            "estimate_win_probability": 65,
            "technical_reasoning": "Test case"
        },
        "account_info_json": {
            "balance": 1000.0,
            "equity": 1000.0,
            "profit": 0.0,
            "leverage": 500
        },
        "symbol_info": {
            "volume_min": 0.01,
            "volume_max": 100.0,
            "volume_step": 0.01,
            "trade_tick_value": 10.0,
            "trade_tick_size": 0.0001,
            "trade_contract_size": 100000.0
        },
        "portfolio_exposure_json": {
            "active_positions": [],
            "pending_orders": [],
            "summary": {
                "total_potential_loss_from_portfolio_usd": 0.0,
                "total_margin_used_from_portfolio_usd": 0.0
            }
        },
        "balance_config": {
            "max_position": 5,
            "max_risk": 2.0,
            "total_max_risk": 8.0
        },
        "correlation_groups_json": {
            "EURO_BLOCK": ["EURUSD", "GBPUSD"]
        },
        "symbol": {"origin_name": "EURUSD"},
        "lot_size_to_margin_map": {
            "0.01": 2.2,
            "0.02": 4.4,
            "0.03": 6.6,
            "0.04": 8.8,
            "0.05": 11.0,
            "0.06": 13.2,
            "0.07": 15.4,
            "0.08": 17.6,
            "0.09": 19.8,
            "0.10": 22.0
        }
    }
    
    try:
        result = service.analyze_risk(test_params)
        
        print("✅ Test successful!")
        print(f"Status: {result.get('status')}")
        print(f"Signal: {result.get('signal')}")
        print(f"Lot Size: {result.get('lot_size')}")
        print(f"Entry Price: {result.get('entry_price')}")
        print(f"Stop Loss: {result.get('stop_loss')}")
        print(f"Take Profit: {result.get('take_profit')}")
        print(f"Estimate Profit: {result.get('estimate_profit')}")
        print(f"Estimate Loss: {result.get('estimate_loss')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_test_cases():
    """Test with actual test cases from JSON"""
    print("\nTesting with actual test cases...")
    
    service = RiskManagerService()
    test_cases_file = Path(__file__).parent / "test_cases.json"
    
    if not test_cases_file.exists():
        print("❌ test_cases.json not found")
        return False
    
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    # Test first few cases
    success_count = 0
    total_tests = min(5, len(test_cases))
    
    for i in range(total_tests):
        test_case = test_cases[i]
        test_name = test_case.get('test_name', f'test_{i}')
        print(f"\nTesting {i+1}/{total_tests}: {test_name}")
        
        try:
            params = test_case['params']
            result = service.analyze_risk(params)
            
            print(f"  Status: {result.get('status')}")
            print(f"  Signal: {result.get('signal')}")
            if result.get('lot_size'):
                print(f"  Lot Size: {result.get('lot_size')}")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
    
    print(f"\n✅ {success_count}/{total_tests} tests passed")
    return success_count == total_tests


def main():
    """Main test function"""
    print("RiskManagerService Simple Test")
    print("=" * 40)
    
    # Test 1: Simple case
    test1_success = test_simple_case()
    
    # Test 2: With test cases
    test2_success = test_with_test_cases()
    
    print("\n" + "=" * 40)
    if test1_success and test2_success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
