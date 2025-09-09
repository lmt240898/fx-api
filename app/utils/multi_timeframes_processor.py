"""
Multi Timeframes Processor Utility
Tái sử dụng logic từ signalGeneratorBot._process_multi_timeframes
"""

import copy
from typing import Dict, Any, Optional
from utils.logger import Logger
from utils.price_action_analyzer import PriceActionAnalyzer


class MultiTimeframesProcessor:
    """
    Utility class để xử lý multi_timeframes data
    Tái sử dụng logic từ signalGeneratorBot._process_multi_timeframes
    """
    
    def __init__(self, logger: Logger):
        """
        Initialize processor
        
        Args:
            logger: Logger instance từ utils/logger.py
        """
        self.logger = logger
        self.price_action_logger = Logger("PriceAction")
    
    def _derive_pip_size(self, symbol_info: dict) -> float:
        """
        Derive pip size from symbol info
        Copied from signalGeneratorBot._process_multi_timeframes
        """
        try:
            point = symbol_info.get('point') or symbol_info.get('trade_tick_size')
            digits = symbol_info.get('digits')
            if isinstance(point, (int, float)) and point > 0:
                if digits in (3, 5):
                    return float(point) * 10.0
                return float(point)
        except Exception:
            pass
        return 0.0001
    
    def process_multi_timeframes(self, symbol_origin_name: str, symbol_info: dict, 
                               multi_timeframes: dict, context: str = "general") -> dict:
        """
        Phân tích price action cho từng timeframe
        
        Args:
            symbol_origin_name: Symbol name
            symbol_info: Symbol information
            multi_timeframes: Multi timeframes data
            context: Context sử dụng ("signal_generation" hoặc "review_loss_order")
            
        Returns:
            dict: {
                'success': bool,
                'error': Optional[str],
                'title': Optional[str],
                'processed_multi_timeframes': dict,  # Đã có analyze_price_action
                'tmp_multi_timeframes': dict,        # Chỉ cho signal_generation
                'raw_data_counts': dict
            }
        """
        self.logger.info(f"Processing multi_timeframes for {symbol_origin_name} (context: {context})")
        
        # Validate input
        if not multi_timeframes:
            return {
                "success": False, 
                "error": "Empty multi_timeframes data", 
                "title": "Multi Timeframes Processing Failed"
            }
        
        # Initialize analyzer
        analyzer = PriceActionAnalyzer()
        pip_size = self._derive_pip_size(symbol_info or {})
        self.price_action_logger.info(f"Begin price action analysis for {symbol_origin_name} with pip_size={pip_size}")
        
        try:
            # Process each timeframe
            for tf, tf_data in multi_timeframes.items():
                raw_list = tf_data.get('raw_data')
                if not isinstance(raw_list, list) or len(raw_list) < 20:
                    err = f"Price action input not enough candles (<20) for {symbol_origin_name} @ {tf}"
                    self.logger.critical(err)
                    return {"success": False, "error": err, "title": "Price Action Analysis Failed"}

                # Chuẩn hóa dữ liệu đầu vào cho analyzer: map tick_volume -> volume
                mapped = []
                for c in raw_list:
                    try:
                        mapped.append({
                            'open': c.get('open'),
                            'high': c.get('high'),
                            'low': c.get('low'),
                            'close': c.get('close'),
                            'volume': c.get('tick_volume', 0),
                            'time': c.get('time')
                        })
                    except Exception:
                        err = f"Malformed raw_data record for {symbol_origin_name} @ {tf}"
                        self.logger.critical(err)
                        return {"success": False, "error": err, "title": "Price Action Analysis Failed"}

                # Analyze price action
                analysis = analyzer.analyze_price_action(mapped, instrument_pip_size=pip_size)

                # Kiểm tra kết quả hợp lệ (tránh default-analysis)
                try:
                    if (
                        not isinstance(analysis, dict) or
                        analysis.get('volume_context', {}).get('status') == 'N/A' or
                        float(analysis.get('current_price_context', {}).get('price', 0) or 0) == 0
                    ):
                        err = f"Price action returned invalid/default analysis for {symbol_origin_name} @ {tf}"
                        self.logger.critical(err)
                        return {"success": False, "error": err, "title": "Price Action Analysis Failed"}
                except Exception:
                    err = f"Price action post-check failed for {symbol_origin_name} @ {tf}"
                    self.logger.critical(err)
                    return {"success": False, "error": err, "title": "Price Action Analysis Failed"}

                # Gắn kết quả vào cấu trúc timeframe
                tf_data['analyze_price_action'] = analysis
                self.price_action_logger.info(f"Analyzed {symbol_origin_name} @ {tf} OK with {len(mapped)} candles")

        except Exception as e:
            err = f"Exception during price action analysis for {symbol_origin_name}: {e}"
            self.logger.critical(err)
            return {"success": False, "error": err, "title": "Price Action Analysis Failed"}

        # Prepare result based on context
        result = {
            'success': True,
            'error': None,
            'title': None,
            'processed_multi_timeframes': multi_timeframes,  # Đã có analyze_price_action
            'raw_data_counts': {}
        }
        
        # Calculate raw_data_counts
        for tf, data in multi_timeframes.items():
            if data and isinstance(data.get('raw_data'), list):
                result['raw_data_counts'][tf] = len(data['raw_data'])
            else:
                result['raw_data_counts'][tf] = 0
        
        # For signal_generation context, create tmp_multi_timeframes (copy with raw_data)
        if context == "signal_generation":
            tmp_multi_timeframes = copy.deepcopy(multi_timeframes)
            result['tmp_multi_timeframes'] = tmp_multi_timeframes
            
            # Xóa raw_data khỏi cấu trúc dùng cho prompt (chỉ giữ trong tmp)
            for _tf, _data in multi_timeframes.items():
                if isinstance(_data, dict) and 'raw_data' in _data:
                    try:
                        del _data['raw_data']
                    except Exception:
                        pass
        
        self.logger.info(f"Multi timeframes processing completed for {symbol_origin_name}")
        return result
    
    def get_processing_summary(self, result: dict) -> str:
        """
        Get processing summary for logging
        
        Args:
            result: Result from process_multi_timeframes
            
        Returns:
            Formatted summary string
        """
        if not result.get('success'):
            return f"Processing failed: {result.get('error', 'Unknown error')}"
        
        raw_data_counts = result.get('raw_data_counts', {})
        total_candles = sum(raw_data_counts.values())
        timeframes_count = len(raw_data_counts)
        
        summary_lines = [
            f"Processing successful",
            f"Timeframes processed: {timeframes_count}",
            f"Total candles analyzed: {total_candles}",
            f"Timeframes: {', '.join(raw_data_counts.keys())}"
        ]
        
        return "\n".join(summary_lines) 