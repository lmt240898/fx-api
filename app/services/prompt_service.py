"""
Prompt Service - Tạo prompt cho AI trading analysis
Kế thừa và tối ưu hóa logic từ create_prompt_for_signal_analyst
"""
import json
from typing import Dict, Any, Optional, List
from ..utils.logger import Logger


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder để xử lý các kiểu dữ liệu đặc biệt"""
    def default(self, obj):
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        return super().default(obj)


class PromptService:
    """Service để tạo prompt cho AI trading analysis"""
    
    def __init__(self):
        self.logger = Logger("PromptService")
        self._prompt_functions = {}
        self._load_prompt_functions()
    
    def _load_prompt_functions(self):
        """Load các prompt functions từ prompts module"""
        try:
            # Import prompts module dynamically
            from ..prompts.prompt_signal_analyst import prompt_signal_analyst
            self._prompt_functions['prompt_signal_analyst'] = prompt_signal_analyst
            self.logger.info("Loaded prompt functions successfully")
        except ImportError as e:
            self.logger.error(f"Failed to load prompt functions: {e}")
            raise
    
    def get_prompt_function(self, prompt_name: str):
        """Lấy prompt function theo tên"""
        return self._prompt_functions.get(prompt_name)
    
    def create_prompt_for_signal_analyst(self, data: Dict[str, Any]) -> str:
        """
        Tạo prompt cho Signal Analyst AI - Tối ưu hóa từ code cũ
        
        Args:
            data: Dữ liệu trading từ API /signal
            
        Returns:
            str: Prompt string để gửi cho AIService
        """
        try:
            # Copy dữ liệu để tránh modify original
            data_for_prompt = data.copy()
            
            # Extract thông tin cần thiết
            symbol = data_for_prompt.get('symbol', '')
            main_timeframe = data_for_prompt.get('timeframe', 'H4')
            
            # Loại bỏ các field không cần thiết để giảm chi phí API
            fields_to_remove = [
                'cache_key', 'all_order_active', 'active_orders_summary',
                'portfolio_exposure', 'account_info', 'account_type_details',
                'balance_config', 'max_positions', 'pending_orders_summary',
                'symbol', 'timeframe'
            ]
            
            for field in fields_to_remove:
                if field in data_for_prompt:
                    del data_for_prompt[field]
            
            # Convert dữ liệu còn lại thành JSON string
            provided_data = json.dumps(data_for_prompt, cls=CustomEncoder, ensure_ascii=False)
            
            # Lấy prompt function
            prompt_function = self.get_prompt_function('prompt_signal_analyst')
            if not prompt_function:
                self.logger.error("Prompt function 'prompt_signal_analyst' not found")
                raise ValueError("Prompt function 'prompt_signal_analyst' not found")
            
            # Tạo parameters cho prompt
            params = {
                'symbol': symbol,
                'provided_data': provided_data,
                'main_timeframe': main_timeframe
            }
            
            # Generate prompt message
            prompt_message = prompt_function(params)
            
            # Trả về prompt string để tương thích với AIService
            return prompt_message
            
        except Exception as e:
            self.logger.error(f"Error creating prompt for signal analyst: {e}")
            raise
    
    def create_prompt_for_risk_manager(self, data: Dict[str, Any]) -> str:
        """
        Tạo prompt cho Risk Manager AI
        
        Args:
            data: Dữ liệu từ API /risk_manager
            
        Returns:
            str: Prompt string để gửi cho AIService
        """
        try:
            # TODO: Implement risk manager prompt creation
            # Hiện tại trả về placeholder
            self.logger.warning("Risk manager prompt creation not implemented yet")
            
            return "Risk manager prompt placeholder - to be implemented"
            
        except Exception as e:
            self.logger.error(f"Error creating prompt for risk manager: {e}")
            raise
    
    def validate_trading_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate dữ liệu trading trước khi tạo prompt
        
        Args:
            data: Dữ liệu trading
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Kiểm tra các field bắt buộc
            required_fields = ['symbol', 'timeframe', 'multi_timeframes']
            
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            # Kiểm tra symbol
            symbol = data.get('symbol')
            if not symbol or not isinstance(symbol, str):
                return False, "Invalid symbol format"
            
            # Kiểm tra timeframe
            timeframe = data.get('timeframe')
            valid_timeframes = ['H2', 'H4', 'H8', 'D1']
            if timeframe not in valid_timeframes:
                return False, f"Invalid timeframe: {timeframe}. Must be one of {valid_timeframes}"
            
            # Kiểm tra multi_timeframes
            multi_timeframes = data.get('multi_timeframes')
            if not multi_timeframes or not isinstance(multi_timeframes, dict):
                return False, "Invalid multi_timeframes format"
            
            # Kiểm tra ít nhất có 1 timeframe
            if not multi_timeframes:
                return False, "No timeframe data provided"
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error validating trading data: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_prompt_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lấy thống kê về prompt để monitor
        
        Args:
            data: Dữ liệu trading
            
        Returns:
            Dict: Thống kê prompt
        """
        try:
            # Tính toán kích thước dữ liệu
            data_size = len(json.dumps(data, cls=CustomEncoder))
            
            # Đếm số timeframes
            multi_timeframes = data.get('multi_timeframes', {})
            timeframe_count = len(multi_timeframes)
            
            # Đếm số indicators per timeframe
            indicators_per_tf = {}
            for tf, tf_data in multi_timeframes.items():
                indicators = tf_data.get('indicators', {})
                indicators_per_tf[tf] = len(indicators)
            
            return {
                'data_size_bytes': data_size,
                'timeframe_count': timeframe_count,
                'indicators_per_timeframe': indicators_per_tf,
                'symbol': data.get('symbol'),
                'main_timeframe': data.get('timeframe'),
                'has_account_info': 'account_info' in data,
                'has_portfolio_exposure': 'portfolio_exposure' in data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting prompt statistics: {e}")
            return {'error': str(e)}


# Global service instance
prompt_service = PromptService()
