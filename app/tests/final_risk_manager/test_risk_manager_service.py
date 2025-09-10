"""
Test suite for RiskManagerService - Comprehensive testing based on test_cases.json

This test suite validates the refactored RiskManagerService against the original
final_risk_manager.py implementation using the same test cases.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.services.risk_manager_service import RiskManagerService
from app.utils.logger import Logger


class TestRiskManagerService:
    """Test class for RiskManagerService"""
    
    def setup_method(self):
        """Setup test environment before each test method"""
        self.service = RiskManagerService()
        self.test_cases_file = Path(__file__).parent / "test_cases.json"
        
    def load_test_cases(self):
        """Load test cases from JSON file"""
        with open(self.test_cases_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_preflight_stop_trade_max_positions(self):
        """Test pre-flight check: Stop trade when max positions reached"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'preflight_stop_trade_max_positions')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert result['lot_size'] is None
        assert result['entry_price'] is None
    
    def test_preflight_skip_losing_active_trade(self):
        """Test pre-flight check: Skip when active trade is losing"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'preflight_skip_losing_active_trade')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert result['lot_size'] is None
    
    def test_preflight_stop_trade_total_risk_exceeded(self):
        """Test pre-flight check: Stop trade when total risk exceeded"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'preflight_stop_trade_total_risk_exceeded')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert result['lot_size'] is None
    
    def test_lotsize_risk_tier_75_percent(self):
        """Test lot size calculation with 75% win probability"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'lotsize_risk_tier_75_percent')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add required lot_size_to_margin_map for margin safety check
        params['lot_size_to_margin_map'] = {
            "0.18": 10.0,  # Mock margin for 0.18 lot
            "0.17": 9.5,
            "0.16": 9.0,
            "0.15": 8.5,
            "0.14": 8.0,
            "0.13": 7.5,
            "0.12": 7.0,
            "0.11": 6.5,
            "0.10": 6.0,
            "0.09": 5.5,
            "0.08": 5.0,
            "0.07": 4.5,
            "0.06": 4.0,
            "0.05": 3.5,
            "0.04": 3.0,
            "0.03": 2.5,
            "0.02": 2.0,
            "0.01": 1.0
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        # Allow some tolerance for lot size due to margin adjustments
        assert abs(result['lot_size'] - expected['lot_size']) <= 0.01
    
    def test_lotsize_capped_by_vRisk(self):
        """Test lot size calculation capped by vRisk"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'lotsize_capped_by_vRisk')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add required lot_size_to_margin_map
        params['lot_size_to_margin_map'] = {
            "0.10": 5.0,
            "0.09": 4.5,
            "0.08": 4.0,
            "0.07": 3.5,
            "0.06": 3.0,
            "0.05": 2.5,
            "0.04": 2.0,
            "0.03": 1.5,
            "0.02": 1.0,
            "0.01": 0.5
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert abs(result['lot_size'] - expected['lot_size']) <= 0.01
    
    def test_lotsize_adj_drawdown(self):
        """Test lot size adjustment due to drawdown"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'lotsize_adj_drawdown')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add required lot_size_to_margin_map
        params['lot_size_to_margin_map'] = {
            "0.08": 4.0,
            "0.07": 3.5,
            "0.06": 3.0,
            "0.05": 2.5,
            "0.04": 2.0,
            "0.03": 1.5,
            "0.02": 1.0,
            "0.01": 0.5
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert abs(result['lot_size'] - expected['lot_size']) <= 0.01
    
    def test_lotsize_adj_multiple_factors(self):
        """Test lot size adjustment with multiple factors"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'lotsize_adj_multiple_factors')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add required lot_size_to_margin_map
        params['lot_size_to_margin_map'] = {
            "0.06": 3.0,
            "0.05": 2.5,
            "0.04": 2.0,
            "0.03": 1.5,
            "0.02": 1.0,
            "0.01": 0.5
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert abs(result['lot_size'] - expected['lot_size']) <= 0.01
    
    def test_final_validation_hold_lot_too_small(self):
        """Test final validation: Hold when lot size too small"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'final_validation_hold_lot_too_small')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add required lot_size_to_margin_map
        params['lot_size_to_margin_map'] = {
            "0.01": 0.5
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert result['lot_size'] is None
    
    def test_final_validation_hold_margin_safety(self):
        """Test final validation: Hold when margin safety fails"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'final_validation_hold_margin_safety')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add lot_size_to_margin_map that will cause margin safety failure
        params['lot_size_to_margin_map'] = {
            "0.18": 500.0,  # High margin that will fail safety check
            "0.17": 450.0,
            "0.16": 400.0,
            "0.15": 350.0,
            "0.14": 300.0,
            "0.13": 250.0,
            "0.12": 200.0,
            "0.11": 150.0,
            "0.10": 100.0,
            "0.09": 90.0,
            "0.08": 80.0,
            "0.07": 70.0,
            "0.06": 60.0,
            "0.05": 50.0,
            "0.04": 40.0,
            "0.03": 30.0,
            "0.02": 20.0,
            "0.01": 10.0
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        assert result['lot_size'] is None
    
    def test_final_validation_rr_adjust_high(self):
        """Test final validation: R:R adjustment for high ratio"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'final_validation_rr_adjust_high')
        
        params = test_case['params']
        expected = test_case['expected_result']
        
        # Add required lot_size_to_margin_map
        params['lot_size_to_margin_map'] = {
            "0.18": 10.0,
            "0.17": 9.5,
            "0.16": 9.0,
            "0.15": 8.5,
            "0.14": 8.0,
            "0.13": 7.5,
            "0.12": 7.0,
            "0.11": 6.5,
            "0.10": 6.0,
            "0.09": 5.5,
            "0.08": 5.0,
            "0.07": 4.5,
            "0.06": 4.0,
            "0.05": 3.5,
            "0.04": 3.0,
            "0.03": 2.5,
            "0.02": 2.0,
            "0.01": 1.0
        }
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == expected['status']
        assert result['signal'] == expected['signal']
        # Check that take_profit was adjusted
        assert result['take_profit'] is not None
        assert result['risk_reward_after'] is not None
        assert result['risk_reward_after'] <= 1.5  # Should be capped at 1.5
    
    def test_random_cases(self):
        """Test random cases for robustness"""
        test_cases = self.load_test_cases()
        random_cases = [tc for tc in test_cases if tc['test_name'].startswith('random_case_')]
        
        for test_case in random_cases[:5]:  # Test first 5 random cases
            params = test_case['params']
            expected = test_case['expected_result']
            
            # Add required lot_size_to_margin_map
            params['lot_size_to_margin_map'] = self._generate_mock_margin_map()
            
            result = self.service.analyze_risk(params)
            
            assert result['status'] == expected['status']
            assert result['signal'] == expected['signal']
            
            if expected['status'] == 'CONTINUE':
                assert result['lot_size'] is not None
                assert result['entry_price'] is not None
                assert result['stop_loss'] is not None
                assert result['take_profit'] is not None
    
    def _generate_mock_margin_map(self):
        """Generate mock margin map for testing"""
        margin_map = {}
        for i in range(1, 201):  # 0.01 to 2.00
            lot_size = i * 0.01
            margin_map[f"{lot_size:.2f}"] = lot_size * 50.0  # Mock margin calculation
        return margin_map
    
    def test_service_initialization(self):
        """Test RiskManagerService initialization"""
        # Test with default logger
        service1 = RiskManagerService()
        assert service1.logger is not None
        
        # Test with custom logger
        custom_logger = Logger("test_logger")
        service2 = RiskManagerService(logger=custom_logger)
        assert service2.logger == custom_logger
    
    def test_error_handling(self):
        """Test error handling in service"""
        # Test with invalid params
        invalid_params = {
            'proposed_signal_json': None,
            'account_info_json': {},
            'symbol_info': {},
            'portfolio_exposure_json': {},
            'balance_config': {},
            'correlation_groups_json': {},
            'symbol': {'origin_name': 'TEST'}
        }
        
        result = self.service.analyze_risk(invalid_params)
        
        assert result['status'] == 'SKIP'
        assert result['signal'] == 'HOLD'
        assert 'error' in result.get('reason', '').lower() or 'unexpected' in result.get('reason', '').lower()
    
    def test_missing_lot_size_to_margin_map(self):
        """Test behavior when lot_size_to_margin_map is missing"""
        test_cases = self.load_test_cases()
        test_case = next(tc for tc in test_cases if tc['test_name'] == 'lotsize_risk_tier_75_percent')
        
        params = test_case['params']
        # Don't add lot_size_to_margin_map
        
        result = self.service.analyze_risk(params)
        
        assert result['status'] == 'HOLD'
        assert result['signal'] == 'HOLD'
        assert result['lot_size'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
