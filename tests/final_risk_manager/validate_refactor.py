"""
Validation script to compare results between old final_risk_manager.py 
and new RiskManagerService implementation.

This script ensures that the refactored code produces identical results
to the original implementation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import both implementations
from app.utils.final_risk_manager import final_risk_manager
from app.services.risk_manager_service import RiskManagerService
from app.utils.logger import Logger


class RefactorValidator:
    """Validator class to compare old and new implementations"""
    
    def __init__(self):
        self.old_service = None  # final_risk_manager function
        self.new_service = RiskManagerService()
        self.test_cases_file = Path(__file__).parent / "test_cases.json"
        self.results = []
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from JSON file"""
        with open(self.test_cases_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def prepare_test_params(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare test parameters with required fields"""
        params = test_case['params'].copy()
        
        # Add lot_size_to_margin_map if not present
        if 'lot_size_to_margin_map' not in params:
            params['lot_size_to_margin_map'] = self._generate_mock_margin_map()
        
        return params
    
    def _generate_mock_margin_map(self) -> Dict[str, float]:
        """Generate mock margin map for testing"""
        margin_map = {}
        for i in range(1, 201):  # 0.01 to 2.00
            lot_size = i * 0.01
            margin_map[f"{lot_size:.2f}"] = lot_size * 50.0  # Mock margin calculation
        return margin_map
    
    def run_old_implementation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run old final_risk_manager implementation"""
        try:
            # Create a copy to avoid modifying original
            test_params = params.copy()
            return final_risk_manager(test_params)
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def run_new_implementation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run new RiskManagerService implementation"""
        try:
            # Create a copy to avoid modifying original
            test_params = params.copy()
            return self.new_service.analyze_risk(test_params)
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def compare_results(self, old_result: Dict[str, Any], new_result: Dict[str, Any], 
                       test_name: str) -> Dict[str, Any]:
        """Compare results between old and new implementations"""
        comparison = {
            'test_name': test_name,
            'status_match': old_result.get('status') == new_result.get('status'),
            'signal_match': old_result.get('signal') == new_result.get('signal'),
            'lot_size_match': self._compare_lot_size(old_result.get('lot_size'), new_result.get('lot_size')),
            'take_profit_match': self._compare_take_profit(old_result.get('take_profit'), new_result.get('take_profit')),
            'estimate_profit_match': self._compare_estimate_profit(
                old_result.get('estimate_profit'), new_result.get('estimate_profit')),
            'estimate_loss_match': self._compare_estimate_loss(
                old_result.get('estimate_loss'), new_result.get('estimate_loss')),
            'old_result': old_result,
            'new_result': new_result,
            'overall_match': True
        }
        
        # Check overall match
        critical_fields = ['status_match', 'signal_match']
        if old_result.get('status') == 'CONTINUE':
            critical_fields.extend(['lot_size_match', 'take_profit_match'])
        
        comparison['overall_match'] = all(comparison[field] for field in critical_fields)
        
        return comparison
    
    def _compare_lot_size(self, old_lot: Any, new_lot: Any) -> bool:
        """Compare lot size with tolerance"""
        if old_lot is None and new_lot is None:
            return True
        if old_lot is None or new_lot is None:
            return False
        return abs(float(old_lot) - float(new_lot)) <= 0.01
    
    def _compare_take_profit(self, old_tp: Any, new_tp: Any) -> bool:
        """Compare take profit with tolerance"""
        if old_tp is None and new_tp is None:
            return True
        if old_tp is None or new_tp is None:
            return False
        return abs(float(old_tp) - float(new_tp)) <= 0.00001
    
    def _compare_estimate_profit(self, old_profit: Any, new_profit: Any) -> bool:
        """Compare estimate profit with tolerance"""
        if old_profit is None and new_profit is None:
            return True
        if old_profit is None or new_profit is None:
            return False
        return abs(float(old_profit) - float(new_profit)) <= 0.01
    
    def _compare_estimate_loss(self, old_loss: Any, new_loss: Any) -> bool:
        """Compare estimate loss with tolerance"""
        if old_loss is None and new_loss is None:
            return True
        if old_loss is None or new_loss is None:
            return False
        return abs(float(old_loss) - float(new_loss)) <= 0.01
    
    def validate_all_tests(self) -> Dict[str, Any]:
        """Validate all test cases"""
        test_cases = self.load_test_cases()
        results = {
            'total_tests': len(test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'test_results': [],
            'summary': {}
        }
        
        print(f"Starting validation of {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases):
            test_name = test_case['test_name']
            print(f"Running test {i+1}/{len(test_cases)}: {test_name}")
            
            try:
                # Prepare test parameters
                params = self.prepare_test_params(test_case)
                
                # Run both implementations
                old_result = self.run_old_implementation(params)
                new_result = self.run_new_implementation(params)
                
                # Compare results
                comparison = self.compare_results(old_result, new_result, test_name)
                results['test_results'].append(comparison)
                
                if comparison['overall_match']:
                    results['passed_tests'] += 1
                    print(f"  ✅ PASSED")
                else:
                    results['failed_tests'] += 1
                    print(f"  ❌ FAILED")
                    self._print_failure_details(comparison)
                
            except Exception as e:
                results['error_tests'] += 1
                print(f"  💥 ERROR: {str(e)}")
                results['test_results'].append({
                    'test_name': test_name,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        # Generate summary
        results['summary'] = {
            'pass_rate': (results['passed_tests'] / results['total_tests']) * 100,
            'failure_rate': (results['failed_tests'] / results['total_tests']) * 100,
            'error_rate': (results['error_tests'] / results['total_tests']) * 100
        }
        
        return results
    
    def _print_failure_details(self, comparison: Dict[str, Any]):
        """Print detailed failure information"""
        print(f"    Status match: {comparison['status_match']}")
        print(f"    Signal match: {comparison['signal_match']}")
        if not comparison['lot_size_match']:
            print(f"    Lot size mismatch: {comparison['old_result'].get('lot_size')} vs {comparison['new_result'].get('lot_size')}")
        if not comparison['take_profit_match']:
            print(f"    Take profit mismatch: {comparison['old_result'].get('take_profit')} vs {comparison['new_result'].get('take_profit')}")
        if not comparison['estimate_profit_match']:
            print(f"    Estimate profit mismatch: {comparison['old_result'].get('estimate_profit')} vs {comparison['new_result'].get('estimate_profit')}")
        if not comparison['estimate_loss_match']:
            print(f"    Estimate loss mismatch: {comparison['old_result'].get('estimate_loss')} vs {comparison['new_result'].get('estimate_loss')}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print validation summary"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Total tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']} ({results['summary']['pass_rate']:.1f}%)")
        print(f"Failed: {results['failed_tests']} ({results['summary']['failure_rate']:.1f}%)")
        print(f"Errors: {results['error_tests']} ({results['summary']['error_rate']:.1f}%)")
        
        if results['failed_tests'] > 0:
            print("\nFAILED TESTS:")
            for test_result in results['test_results']:
                if not test_result.get('overall_match', True):
                    print(f"  - {test_result['test_name']}")
        
        if results['error_tests'] > 0:
            print("\nERROR TESTS:")
            for test_result in results['test_results']:
                if 'error' in test_result:
                    print(f"  - {test_result['test_name']}: {test_result['error']}")
        
        print("="*60)
        
        if results['summary']['pass_rate'] == 100.0:
            print("🎉 ALL TESTS PASSED! Refactor is successful.")
        elif results['summary']['pass_rate'] >= 95.0:
            print("✅ Refactor is mostly successful with minor issues.")
        else:
            print("❌ Refactor has significant issues that need to be addressed.")
    
    def save_detailed_results(self, results: Dict[str, Any], filename: str = "validation_results.json"):
        """Save detailed results to JSON file"""
        output_file = Path(__file__).parent / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {output_file}")


def main():
    """Main validation function"""
    print("Risk Manager Service Refactor Validation")
    print("="*50)
    
    validator = RefactorValidator()
    
    try:
        # Run validation
        results = validator.validate_all_tests()
        
        # Print summary
        validator.print_summary(results)
        
        # Save detailed results
        validator.save_detailed_results(results)
        
        # Return exit code based on results
        if results['summary']['pass_rate'] == 100.0:
            return 0
        elif results['summary']['pass_rate'] >= 95.0:
            return 1  # Warning
        else:
            return 2  # Error
            
    except Exception as e:
        print(f"Validation failed with error: {str(e)}")
        print(traceback.format_exc())
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
