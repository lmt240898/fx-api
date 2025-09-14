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
    
    def _create_cache_key_folder(self, timezone: str, timeframe: str, symbol: str) -> str:
        """
        Tạo folder theo format cache_key với số thứ tự tăng dần
        
        Args:
            timezone: Timezone (ví dụ: GMT+3.0)
            timeframe: Timeframe (ví dụ: H2, H4)
            symbol: Tên symbol (ví dụ: EURUSD)
            
        Returns:
            str: Đường dẫn folder đã tạo
        """
        try:
            # Clean timezone: thay + thành _ và : thành _
            timezone_clean = timezone.replace("+", "_").replace(":", "_")
            
            # Tạo tên folder cache key: GMT_3.0_H2_EURUSD
            cache_key_folder = f"{timezone_clean}_{timeframe}_{symbol}"
            
            # Tạo đường dẫn theo cấu trúc logs/tháng-năm/ngày/
            now = datetime.now()
            month_year = now.strftime("%m-%Y")
            day = now.strftime("%d")
            
            base_folder_path = os.path.join(
                self.base_logs_dir,
                month_year,
                day,
                cache_key_folder
            )
            
            # Tạo folder cache key nếu chưa tồn tại
            os.makedirs(base_folder_path, exist_ok=True)
            
            # Tìm số thứ tự tiếp theo
            next_number = self._get_next_folder_number(base_folder_path)
            
            # Tạo folder với số thứ tự
            folder_path = os.path.join(base_folder_path, str(next_number))
            os.makedirs(folder_path, exist_ok=True)
            
            self.logger.info(f"Created cache key folder: {folder_path}")
            return folder_path
            
        except Exception as e:
            self.logger.error(f"Error creating cache key folder: {e}")
            raise
    
    def _get_next_folder_number(self, base_path: str) -> int:
        """
        Tìm số thứ tự tiếp theo cho folder cache key
        
        Args:
            base_path: Đường dẫn folder cache key
            
        Returns:
            int: Số thứ tự tiếp theo
        """
        try:
            if not os.path.exists(base_path):
                return 1
            
            # Lấy tất cả folder con (chỉ số)
            existing_folders = []
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path) and item.isdigit():
                    existing_folders.append(int(item))
            
            if not existing_folders:
                return 1
            
            # Trả về số lớn nhất + 1
            return max(existing_folders) + 1
            
        except Exception as e:
            self.logger.error(f"Error getting next folder number: {e}")
            return 1
    
    def log_response(self, timezone: str, timeframe: str, symbol: str, 
                    response_data: Dict[str, Any], request_data: Dict[str, Any] = None) -> str:
        """
        Lưu response vào file result.log trong folder cache_key với số thứ tự
        
        Args:
            timezone: Timezone (ví dụ: GMT+3.0)
            timeframe: Timeframe (ví dụ: H2, H4)
            symbol: Tên symbol
            response_data: Dữ liệu response cần lưu
            request_data: Dữ liệu request (optional)
            
        Returns:
            str: Đường dẫn file log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_cache_key_folder(timezone, timeframe, symbol)
            
            # Tạo nội dung log
            log_content = {
                "timestamp": datetime.now().isoformat(),
                "timezone": timezone,
                "timeframe": timeframe,
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
    
    def log_signal_response(self, timezone: str, timeframe: str, symbol: str,
                          response_data: Dict[str, Any], 
                          request_data: Dict[str, Any] = None,
                          prompt_content: str = None) -> str:
        """
        Lưu signal response với thông tin bổ sung và prompt content
        
        Args:
            timezone: Timezone (ví dụ: GMT+3.0)
            timeframe: Timeframe (H2, H4, etc.)
            symbol: Tên symbol
            response_data: Dữ liệu response
            request_data: Dữ liệu request
            prompt_content: Nội dung prompt đã tạo (optional)
            
        Returns:
            str: Đường dẫn file log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_cache_key_folder(timezone, timeframe, symbol)
            
            # Tạo nội dung log với thông tin bổ sung
            log_content = {
                "timestamp": datetime.now().isoformat(),
                "timezone": timezone,
                "timeframe": timeframe,
                "symbol": symbol,
                "request_data": request_data,
                "response_data": response_data,
                "log_type": "signal_analysis"
            }
            
            # Đường dẫn file log
            log_file_path = os.path.join(folder_path, "result.log")
            
            # Ghi file log
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump(log_content, f, indent=2, ensure_ascii=False)
            
            # Lưu prompt content nếu có
            if prompt_content:
                self._log_prompt_content(folder_path, timezone, timeframe, symbol, prompt_content, request_data)
            
            self.logger.info(f"Signal response logged to: {log_file_path}")
            return log_file_path
            
        except Exception as e:
            self.logger.error(f"Error logging signal response: {e}")
            raise
    
    def log_risk_manager_response(self, timezone: str, timeframe: str, symbol: str,
                                response_data: Dict[str, Any], 
                                request_data: Dict[str, Any] = None) -> str:
        """
        Lưu risk manager response
        
        Args:
            timezone: Timezone (ví dụ: GMT+3.0)
            timeframe: Timeframe (ví dụ: H2, H4)
            symbol: Tên symbol
            response_data: Dữ liệu response
            request_data: Dữ liệu request
            
        Returns:
            str: Đường dẫn file log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_cache_key_folder(timezone, timeframe, symbol)
            
            # Tạo nội dung log
            log_content = {
                "timestamp": datetime.now().isoformat(),
                "timezone": timezone,
                "timeframe": timeframe,
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
    
    def _log_prompt_content(self, folder_path: str, timezone: str, timeframe: str, symbol: str,
                           prompt_content: str, request_data: Dict[str, Any] = None) -> str:
        """
        Lưu nội dung prompt vào file prompt.log (text format thuần túy)
        
        Args:
            folder_path: Đường dẫn folder đã tạo
            timezone: Timezone (ví dụ: GMT+3.0)
            timeframe: Timeframe
            symbol: Tên symbol
            prompt_content: Nội dung prompt
            request_data: Dữ liệu request (optional)
            
        Returns:
            str: Đường dẫn file prompt.log đã tạo
        """
        try:
            # Đường dẫn file prompt.log
            prompt_log_path = os.path.join(folder_path, "prompt.log")
            
            # Ghi file prompt.log với nội dung text thuần túy
            with open(prompt_log_path, 'w', encoding='utf-8') as f:
                # Ghi nội dung prompt trực tiếp (không JSON format)
                f.write(prompt_content)
            
            self.logger.info(f"Prompt content logged to: {prompt_log_path}")
            return prompt_log_path
            
        except Exception as e:
            self.logger.error(f"Error logging prompt content: {e}")
            raise
    
    def log_prompt_only(self, timezone: str, timeframe: str, symbol: str, prompt_content: str, 
                       request_data: Dict[str, Any] = None) -> str:
        """
        Chỉ lưu prompt content (không lưu response)
        
        Args:
            timezone: Timezone (ví dụ: GMT+3.0)
            timeframe: Timeframe
            symbol: Tên symbol
            prompt_content: Nội dung prompt
            request_data: Dữ liệu request (optional)
            
        Returns:
            str: Đường dẫn file prompt.log đã tạo
        """
        try:
            # Tạo folder
            folder_path = self._create_cache_key_folder(timezone, timeframe, symbol)
            
            # Lưu prompt content
            return self._log_prompt_content(folder_path, timezone, timeframe, symbol, prompt_content, request_data)
            
        except Exception as e:
            self.logger.error(f"Error logging prompt only: {e}")
            raise


# Singleton instance
response_logger = ResponseLogger()
