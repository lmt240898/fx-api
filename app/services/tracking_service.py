# Tracking Service - Handles tracking data storage
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from app.utils.logger import Logger
from app.utils.response_handler import ResponseHandler

class TrackingService:
    """
    Tracking Service - Handles storage of tracking data for audit and analysis.
    
    This service creates folder structure and saves tracking data from both
    Signal API and Risk Manager API for complete process tracking.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize TrackingService.
        
        Args:
            logger: Optional logger instance. If not provided, creates a default one.
        """
        self.logger = logger or Logger("tracking_service")
        self.base_logs_dir = "logs"
    
    def save_tracking_data(self, params: dict) -> dict:
        """
        Main entry point for saving tracking data.
        
        Args:
            params (dict): Object containing all necessary parameters:
                - login: User login ID
                - ticket: Ticket ID
                - synthetic_params_signal: Signal API data
                - synthetic_params_risk_manager: Risk Manager API data
        
        Returns:
            dict: Success/failure result
        """
        try:
            self.logger.info("=== BẮT ĐẦU QUÁ TRÌNH LƯU TRACKING DATA ===")
            
            # Extract required fields
            login = params.get('login')
            ticket = params.get('ticket')
            synthetic_params_signal = params.get('synthetic_params_signal', {})
            synthetic_response_signal = params.get('synthetic_response_signal', {})
            synthetic_params_risk_manager = params.get('synthetic_params_risk_manager', {})
            synthetic_response_risk_manager = params.get('synthetic_response_risk_manager', {})
            
            # Validate required fields
            if not login or not ticket:
                self.logger.error("Missing required fields: login or ticket")
                return ResponseHandler.validation_error("Missing required fields: login or ticket")
            
            self.logger.info(f"📊 Processing tracking data - Login: {login}, Ticket: {ticket}")
            
            # Create folder structure
            folder_path = self._create_tracking_folder(login, ticket)
            
            # Save signal data (params and response)
            signal_params_file_path = self._save_signal_params_data(folder_path, synthetic_params_signal)
            signal_response_file_path = self._save_signal_response_data(folder_path, synthetic_response_signal)
            
            # Save risk manager data (params and response)
            risk_manager_params_file_path = self._save_risk_manager_params_data(folder_path, synthetic_params_risk_manager)
            risk_manager_response_file_path = self._save_risk_manager_response_data(folder_path, synthetic_response_risk_manager)
            
            self.logger.info("=== KẾT THÚC QUÁ TRÌNH LƯU TRACKING DATA ===")
            
            return ResponseHandler.success({
                "message": "Tracking data saved successfully",
                "login": login,
                "ticket": ticket,
                "folder_path": folder_path,
                "signal_params_file": signal_params_file_path,
                "signal_response_file": signal_response_file_path,
                "risk_manager_params_file": risk_manager_params_file_path,
                "risk_manager_response_file": risk_manager_response_file_path
            })
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi trong quá trình lưu tracking data: {str(e)}")
            return ResponseHandler.internal_server_error(f"Error saving tracking data: {str(e)}")
    
    def _create_tracking_folder(self, login: str, ticket: str) -> str:
        """
        Create tracking folder structure: ORDERS/LOGINID_{login}/ticket_{ticket}/
        
        Args:
            login: User login ID
            ticket: Ticket ID
            
        Returns:
            str: Full path to the created folder
        """
        try:
            # Create base folder structure: logs/MM-YYYY/DD/
            now = datetime.now()
            month_year = now.strftime("%m-%Y")
            day = now.strftime("%d")
            
            # Create tracking folder: ORDERS/LOGINID_{login}/ticket_{ticket}/
            orders_folder = "ORDERS"
            login_folder = f"LOGINID_{login}"
            ticket_folder = f"ticket_{ticket}"
            
            # Full path: logs/MM-YYYY/DD/ORDERS/LOGINID_{login}/ticket_{ticket}/
            folder_path = os.path.join(
                self.base_logs_dir, 
                month_year, 
                day, 
                orders_folder,      # ← THÊM MỚI: ORDERS folder
                login_folder, 
                ticket_folder
            )
            
            # Create directories
            os.makedirs(folder_path, exist_ok=True)
            
            self.logger.info(f"📁 Created tracking folder: {folder_path}")
            return folder_path
            
        except Exception as e:
            self.logger.error(f"❌ Error creating tracking folder: {e}")
            raise
    
    def _save_signal_params_data(self, folder_path: str, signal_data: Dict[str, Any]) -> str:
        """
        Save synthetic_params_signal data to file.
        
        Args:
            folder_path: Path to the tracking folder
            signal_data: Signal API input data
            
        Returns:
            str: Path to the saved file
        """
        try:
            file_path = os.path.join(folder_path, "synthetic_params_signal.log")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(signal_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved signal params data to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Error saving signal params data: {e}")
            raise
    
    def _save_signal_response_data(self, folder_path: str, signal_response_data: Dict[str, Any]) -> str:
        """
        Save synthetic_response_signal data to file.
        
        Args:
            folder_path: Path to the tracking folder
            signal_response_data: Signal API response data
            
        Returns:
            str: Path to the saved file
        """
        try:
            file_path = os.path.join(folder_path, "synthetic_response_signal.log")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(signal_response_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved signal response data to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Error saving signal response data: {e}")
            raise
    
    def _save_risk_manager_params_data(self, folder_path: str, risk_manager_data: Dict[str, Any]) -> str:
        """
        Save synthetic_params_risk_manager data to file.
        
        Args:
            folder_path: Path to the tracking folder
            risk_manager_data: Risk Manager API input data
            
        Returns:
            str: Path to the saved file
        """
        try:
            file_path = os.path.join(folder_path, "synthetic_params_risk_manager.log")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(risk_manager_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved risk manager params data to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Error saving risk manager params data: {e}")
            raise
    
    def _save_risk_manager_response_data(self, folder_path: str, risk_manager_response_data: Dict[str, Any]) -> str:
        """
        Save synthetic_response_risk_manager data to file.
        
        Args:
            folder_path: Path to the tracking folder
            risk_manager_response_data: Risk Manager API response data
            
        Returns:
            str: Path to the saved file
        """
        try:
            file_path = os.path.join(folder_path, "synthetic_response_risk_manager.log")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(risk_manager_response_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved risk manager response data to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Error saving risk manager response data: {e}")
            raise
