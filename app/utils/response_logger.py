"""
Response Logger utility for FX API
Tạo folder theo format symbol_ddmmyyhhmmss và lưu response vào result.log
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from app.utils.logger import Logger


class ResponseLogger:
    """Logger để lưu response vào folder theo format symbol_ddmmyyhhmmss"""
    
    def __init__(self):
        self.logger = Logger("response_logger")
        self.base_logs_dir = "logs"
    
    def _create_symbol_folder(self, symbol: str) -> str:
        """
        Tạo folder theo format symbol_ddmmyyhhmmss
        
        Args:
            symbol: Tên symbol (ví dụ: EURUSD)
            
        Returns:
            str: Đường dẫn folder đã tạo
        """
        try:
            # Tạo timestamp theo format ddmmyyhhmmss
            now = datetime.now()
            timestamp = now.strftime("%d%m%y%H%M%S")
            
            # Tạo tên folder: symbol_ddmmyyhhmmss
            folder_name = f"{symbol}_{timestamp}"
            
            # Tạo đường dẫn theo cấu trúc logs/tháng-năm/ngày/
            month_year = now.strftime("%m-%Y")
            day = now.strftime("%d")
            
            folder_path = os.path.join(
                self.base_logs_dir,
                month_year,
                day,
                folder_name
            )
            
            # Tạo folder nếu chưa tồn tại
            os.makedirs(folder_path, exist_ok=True)
            
            self.logger.info(f"Created response folder: {folder_path}")
            return folder_path
            
        except Exception as e:
            self.logger.error(f"Error creating symbol folder: {e}")
            raise
    
    def log_response(self, symbol: str, response_data: Dict[str, Any], 
                    request_data: Dict[str, Any] = None) -> str:
        """
        Lưu response vào file result.log trong folder symbol_ddmmyyhhmmss
        
        Args:
            symbol: Tên symbol
            response_data: Dữ liệu response cần lưu
            request_data: Dữ liệu request (optional)
            
        Returns:
            str: Đường dẫn file log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_symbol_folder(symbol)
            
            # Tạo nội dung log
            log_content = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "request_data": request_data,
                "response_data": response_data
            }
            
            # Đường dẫn file log
            log_file_path = os.path.join(folder_path, "result.log")
            
            # Ghi file log
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(log_content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Response logged to: {log_file_path}")
            return log_file_path
            
        except Exception as e:
            self.logger.error(f"Error logging response: {e}")
            raise
    
    def log_signal_response(self, symbol: str, timeframe: str, 
                          response_data: Dict[str, Any], 
                          request_data: Dict[str, Any] = None) -> str:
        """
        Lưu signal response với thông tin bổ sung
        
        Args:
            symbol: Tên symbol
            timeframe: Timeframe (H2, H4, etc.)
            response_data: Dữ liệu response
            request_data: Dữ liệu request
            
        Returns:
            str: Đường dẫn file log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_symbol_folder(symbol)
            
            # Tạo nội dung log với thông tin bổ sung
            log_content = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "timeframe": timeframe,
                "request_data": request_data,
                "response_data": response_data,
                "log_type": "signal_analysis"
            }
            
            # Đường dẫn file log
            log_file_path = os.path.join(folder_path, "result.log")
            
            # Ghi file log
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(log_content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Signal response logged to: {log_file_path}")
            return log_file_path
            
        except Exception as e:
            self.logger.error(f"Error logging signal response: {e}")
            raise
    
    def log_risk_manager_response(self, symbol: str, 
                                response_data: Dict[str, Any], 
                                request_data: Dict[str, Any] = None) -> str:
        """
        Lưu risk manager response
        
        Args:
            symbol: Tên symbol
            response_data: Dữ liệu response
            request_data: Dữ liệu request
            
        Returns:
            str: Đường dẫn file log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_symbol_folder(symbol)
            
            # Tạo nội dung log
            log_content = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "request_data": request_data,
                "response_data": response_data,
                "log_type": "risk_manager"
            }
            
            # Đường dẫn file log
            log_file_path = os.path.join(folder_path, "result.log")
            
            # Ghi file log
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(log_content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Risk manager response logged to: {log_file_path}")
            return log_file_path
            
        except Exception as e:
            self.logger.error(f"Error logging risk manager response: {e}")
            raise


# Singleton instance
response_logger = ResponseLogger()
