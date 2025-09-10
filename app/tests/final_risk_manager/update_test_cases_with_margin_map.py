"""
Script to update test_cases.json with lot_size_to_margin_map for each test case.

This script calculates the appropriate lot_size_to_margin_map based on:
- Account balance (equity)
- Symbol info (contract_size, leverage)
- Entry price from proposed_signal

The margin map will cover lot sizes from 0.01 to a reasonable maximum based on balance.
"""

import json
import math
from pathlib import Path
from typing import Dict, Any, List


class TestCaseMarginUpdater:
    """Class to update test cases with lot_size_to_margin_map"""
    
    def __init__(self):
        self.test_cases_file = Path(__file__).parent / "test_cases.json"
        self.backup_file = Path(__file__).parent / "test_cases_backup.json"
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from JSON file"""
        with open(self.test_cases_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_test_cases(self, test_cases: List[Dict[str, Any]]):
        """Save test cases to JSON file"""
        with open(self.test_cases_file, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2, ensure_ascii=False)
    
    def create_backup(self, test_cases: List[Dict[str, Any]]):
        """Create backup of original test cases"""
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2, ensure_ascii=False)
        print(f"Backup created: {self.backup_file}")
    
    def calculate_margin_for_lot_size(self, lot_size: float, entry_price: float, 
                                    contract_size: float, leverage: float) -> float:
        """
        Calculate margin required for a given lot size.
        
        Formula: Margin = (Lot Size × Contract Size × Entry Price) / Leverage
        
        Args:
            lot_size: Lot size (e.g., 0.01, 0.02, etc.)
            entry_price: Entry price from proposed signal
            contract_size: Contract size (usually 100,000 for forex)
            leverage: Account leverage (e.g., 500, 1000, etc.)
            
        Returns:
            float: Required margin in USD
        """
        margin = (lot_size * contract_size * entry_price) / leverage
        return round(margin, 2)
    
    def generate_lot_size_to_margin_map(self, test_case: Dict[str, Any]) -> Dict[str, float]:
        """
        Generate lot_size_to_margin_map for a test case.
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            Dict[str, float]: Mapping from lot size string to margin in USD
        """
        params = test_case['params']
        
        # Extract required data
        proposed_signal = params.get('proposed_signal_json', {})
        account_info = params.get('account_info_json', {})
        symbol_info = params.get('symbol_info', {})
        
        # Get entry price
        entry_price = float(proposed_signal.get('entry_price_proposed', 1.0))
        
        # Get contract size (default to 100,000 for forex)
        contract_size = float(symbol_info.get('trade_contract_size', 100000.0))
        
        # Get leverage (default to 500)
        leverage = float(account_info.get('leverage', 500))
        
        # Get account equity to determine reasonable lot size range
        equity = float(account_info.get('equity', 1000.0))
        
        # Calculate maximum reasonable lot size based on equity
        # Rule: Maximum lot size should not require more than 20% of equity as margin
        max_margin_percent = 0.20  # 20%
        max_margin_usd = equity * max_margin_percent
        
        # Calculate maximum lot size
        max_lot_size = (max_margin_usd * leverage) / (contract_size * entry_price)
        max_lot_size = min(max_lot_size, 10.0)  # Cap at 10 lots maximum
        
        # Generate margin map
        margin_map = {}
        volume_step = float(symbol_info.get('volume_step', 0.01))
        
        # Start from minimum lot size and go up to maximum
        current_lot = 0.01
        while current_lot <= max_lot_size:
            lot_str = f"{current_lot:.2f}"
            margin = self.calculate_margin_for_lot_size(
                current_lot, entry_price, contract_size, leverage
            )
            margin_map[lot_str] = margin
            
            # Increment by volume step
            current_lot = round(current_lot + volume_step, 2)
            
            # Safety check to prevent infinite loop
            if current_lot > 20.0:
                break
        
        return margin_map
    
    def update_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a single test case with lot_size_to_margin_map.
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            Dict[str, Any]: Updated test case
        """
        # Create a copy to avoid modifying original
        updated_case = test_case.copy()
        updated_params = updated_case['params'].copy()
        
        # Generate margin map
        margin_map = self.generate_lot_size_to_margin_map(test_case)
        
        # Add margin map to params
        updated_params['lot_size_to_margin_map'] = margin_map
        
        # Update the test case
        updated_case['params'] = updated_params
        
        return updated_case
    
    def update_all_test_cases(self):
        """Update all test cases with lot_size_to_margin_map"""
        print("Loading test cases...")
        test_cases = self.load_test_cases()
        
        print(f"Found {len(test_cases)} test cases")
        
        # Create backup
        self.create_backup(test_cases)
        
        # Update each test case
        updated_cases = []
        for i, test_case in enumerate(test_cases):
            test_name = test_case.get('test_name', f'test_{i}')
            print(f"Updating test case {i+1}/{len(test_cases)}: {test_name}")
            
            try:
                updated_case = self.update_test_case(test_case)
                updated_cases.append(updated_case)
                
                # Show some info about the generated margin map
                margin_map = updated_case['params']['lot_size_to_margin_map']
                lot_sizes = list(margin_map.keys())
                print(f"  Generated margin map with {len(margin_map)} lot sizes: {lot_sizes[0]} to {lot_sizes[-1]}")
                
            except Exception as e:
                print(f"  Error updating test case {test_name}: {str(e)}")
                # Keep original test case if update fails
                updated_cases.append(test_case)
        
        # Save updated test cases
        print("Saving updated test cases...")
        self.save_test_cases(updated_cases)
        
        print(f"Successfully updated {len(updated_cases)} test cases")
        print(f"Updated file: {self.test_cases_file}")
        
        return updated_cases
    
    def validate_updated_test_cases(self, test_cases: List[Dict[str, Any]]):
        """Validate that all test cases have lot_size_to_margin_map"""
        print("\nValidating updated test cases...")
        
        missing_margin_map = []
        for i, test_case in enumerate(test_cases):
            test_name = test_case.get('test_name', f'test_{i}')
            params = test_case.get('params', {})
            
            if 'lot_size_to_margin_map' not in params:
                missing_margin_map.append(test_name)
            else:
                margin_map = params['lot_size_to_margin_map']
                if not isinstance(margin_map, dict) or len(margin_map) == 0:
                    missing_margin_map.append(test_name)
        
        if missing_margin_map:
            print(f"❌ {len(missing_margin_map)} test cases missing valid lot_size_to_margin_map:")
            for test_name in missing_margin_map:
                print(f"  - {test_name}")
        else:
            print("✅ All test cases have valid lot_size_to_margin_map")
        
        return len(missing_margin_map) == 0
    
    def show_sample_margin_map(self, test_cases: List[Dict[str, Any]]):
        """Show sample margin map from first test case"""
        if not test_cases:
            return
        
        first_case = test_cases[0]
        test_name = first_case.get('test_name', 'first_test')
        margin_map = first_case.get('params', {}).get('lot_size_to_margin_map', {})
        
        print(f"\nSample margin map from '{test_name}':")
        print("Lot Size -> Margin (USD)")
        print("-" * 25)
        
        # Show first 10 entries
        for i, (lot_size, margin) in enumerate(margin_map.items()):
            if i >= 10:
                print(f"... and {len(margin_map) - 10} more entries")
                break
            print(f"{lot_size:>6} -> {margin:>8.2f}")
    
    def run(self):
        """Run the complete update process"""
        print("Test Case Margin Map Updater")
        print("=" * 40)
        
        try:
            # Update all test cases
            updated_cases = self.update_all_test_cases()
            
            # Validate results
            is_valid = self.validate_updated_test_cases(updated_cases)
            
            # Show sample
            self.show_sample_margin_map(updated_cases)
            
            if is_valid:
                print("\n🎉 All test cases successfully updated with lot_size_to_margin_map!")
                return True
            else:
                print("\n❌ Some test cases failed validation. Please check the output above.")
                return False
                
        except Exception as e:
            print(f"\n💥 Error during update process: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function"""
    updater = TestCaseMarginUpdater()
    success = updater.run()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
