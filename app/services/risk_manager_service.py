# Risk Manager Service - Refactored from final_risk_manager.py
from pathlib import Path
from functools import wraps
from datetime import datetime
import requests, time, json, os, sys, random
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
load_dotenv()
sys.path.append(str(Path(__file__).parent.parent))
from app.utils.logger import Logger
from app.utils.common import *
from app.utils.response_logger import response_logger
import json
import math
from app.utils.common import map_signal_to_action

# Order Type Constants (mirrors MT5 values for interoperability)
ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

class RiskManagerService:
    """
    Risk Manager Service - Handles comprehensive risk management for trading signals.
    
    This service provides risk analysis, lot size calculation, and portfolio management
    for trading operations. Refactored from final_risk_manager.py for better maintainability.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize RiskManagerService.
        
        Args:
            logger: Optional logger instance. If not provided, creates a default one.
        """
        self.logger = logger or Logger("risk_manager_service")
    
    def analyze_risk(self, params: dict) -> dict:
        """
        Main entry point for risk analysis - equivalent to final_risk_manager().
        
        Args:
            params (dict): Object containing all necessary parameters:
                - proposed_signal_json: Proposed trading signal
                - account_info_json: Account information
                - symbol: Symbol information
                - symbol_info: Detailed symbol information
                - correlation_groups_json: Correlation groups
                - balance_config: Risk configuration by balance
                - account_type_details: Account type details
                - portfolio_exposure_json: Current portfolio information
        
        Returns:
            dict: Risk analysis result
        """
        # Use the override logger if provided, otherwise use instance logger
        logger = params.get('logger_override') or self.logger
        
        logger.info("=== BẮT ĐẦU QUÁ TRÌNH QUẢN LÝ RỦI RO ===")
        
        # Create a shallow copy for logging to avoid modifying the original dict
        params_to_log = params.copy()
        # Remove non-serializable objects before logging
        params_to_log.pop('mt5_services', None)
        params_to_log.pop('logger_override', None)
        logger.info(f"=== PARAMS: {json.dumps(params_to_log, indent=2)} ===")
        
        # Call enhanced risk manager to process risk management logic
        result = self._analyze_risk_enhanced(params, logger)
        
        logger.info(f"=== KẾT THÚC QUÁ TRÌNH QUẢN LÝ RỦI RO - STATUS: {result.get('status', 'UNKNOWN')} ===")
        
        # Log response
        try:
            symbol = params.get('symbol', {}).get('origin_name', 'UNKNOWN')
            response_logger.log_risk_manager_response(
                symbol=symbol,
                response_data=result,
                request_data=params_to_log
            )
        except Exception as log_error:
            logger.warning(f"Failed to log risk manager response: {log_error}")
        
        # Return result directly (no need to call AI API)
        return result

    def _analyze_risk_enhanced(self, params: dict, logger) -> dict:
        """
        Main coordinator function to evaluate a trading signal based on complex risk management rules.
        Equivalent to risk_manager_enhanced().

        Args:
            params (dict): Dictionary containing all necessary data and configuration.
            logger: Initialized logger instance.

        Returns:
            dict: Dictionary containing final decision and command parameters.
        """
        try:
            logger.info("[🔍 BƯỚC A: CHUẨN BỊ VÀ XÁC THỰC DỮ LIỆU]")
            # Extract and parse input data.
            # If there are errors at this step (e.g., invalid JSON, missing important fields),
            # log the error and return SKIP status.
            
            # Data from Proposed Signal
            proposed_signal = params.get('proposed_signal_json')
            symbol = proposed_signal.get('symbol', 'UNKNOWN')
            logger.info(f"📊 Symbol đang xử lý: {symbol}")

            # Account data
            account_info = params.get('account_info_json', {})
            equity = float(account_info.get('equity', 0))
            balance = float(account_info.get('balance', 0))
            logger.info(f"💰 Balance: ${balance:.2f}, Equity: ${equity:.2f}")

            # Symbol data
            symbol_info = params.get('symbol_info', {})
            volume_min = float(symbol_info.get('volume_min', 0.01))
            volume_max = float(symbol_info.get('volume_max', 200.0))
            volume_step = float(symbol_info.get('volume_step', 0.01))
            logger.info(f"📈 Symbol config - Min: {volume_min}, Max: {volume_max}, Step: {volume_step}")

            # Portfolio data
            portfolio_exposure = params.get('portfolio_exposure_json', {}) # This is dict, not JSON string

            # Risk configuration from balance_config
            balance_config = params.get('balance_config', {})
            vRisk = float(balance_config.get('max_risk', 2.0))
            vTotalRiskCap = float(balance_config.get('total_max_risk', 6.0))
            max_positions = int(balance_config.get('max_position', 5))
            correlation_groups = params.get('correlation_groups_json', {})
            logger.info(f"⚙️ Risk config - Max Risk: {vRisk}%, Total Risk Cap: {vTotalRiskCap}%, Max Positions: {max_positions}")

            logger.info("[🚀 BƯỚC B: THỰC THI WORKFLOW QUẢN LÝ RỦI RO]")

            # -- STEP 1: PRE-FLIGHT PORTFOLIO CHECK (GO/NO-GO) --
            logger.info("[🔍 STEP 1: KIỂM TRA PRE-FLIGHT PORTFOLIO]")
            pre_flight_status, pre_flight_reason, pre_flight_data = self._perform_pre_flight_checks(
                symbol=symbol,
                proposed_signal=proposed_signal,
                portfolio_exposure=portfolio_exposure,
                max_positions=max_positions,
                equity=equity,
                vTotalRiskCap=vTotalRiskCap,
                symbol_info=symbol_info,
                vRisk=vRisk,
                logger=logger
            )

            logger.info(f"📋 Kết quả pre-flight check: {pre_flight_status} - {pre_flight_reason}")
            
            if pre_flight_status != "CONTINUE":
                logger.warning(f"❌ Dừng xử lý do pre-flight check: {pre_flight_status}")
                return self._build_final_response(status=pre_flight_status, symbol=symbol, proposed_signal=proposed_signal, reason=pre_flight_reason)

            # -- STEP 2 & 3: TÍNH TOÁN LOT SIZE --
            logger.info("[🧮 STEP 2 & 3: TÍNH TOÁN LOT SIZE]")
            # This step will calculate lot size based on risk, capital and adjustments.
            # It will return adjusted lot size or a status (e.g., HOLD) if there are issues.
            lot_size_result = self._calculate_final_lot_size(
                proposed_signal=proposed_signal,
                account_info=account_info,
                symbol_info=symbol_info,
                portfolio_exposure=portfolio_exposure,
                correlation_groups=correlation_groups,
                vRisk=vRisk,
                params=params, # Pass params in
                logger=logger
            )

            final_lot_size = lot_size_result.get('final_lot_size')
            correlated_symbols_found = lot_size_result.get('correlated_symbols', []) # Get correlated symbols list
            logger.info(f"📊 Kết quả tính lot size: {final_lot_size}")
            
            if lot_size_result.get('status') == "HOLD":
                logger.warning("❌ Lot size quá nhỏ, trả về HOLD")
                return self._build_final_response(status="HOLD", symbol=symbol, proposed_signal=proposed_signal, reason="Lot size too small")

            # -- STEP 4: FINAL VALIDATION AND PROFIT/LOSS CALCULATION --
            logger.info("[✅ STEP 4: VALIDATION CUỐI CÙNG VÀ TÍNH TOÁN LỢI NHUẬN/THUA LỖ]")
            
            # 4g. Adjust Risk-to-Reward Ratio (New logic: R:R > 1.5 then adjust)
            logger.info("📊 Điều chỉnh tỷ lệ Risk-to-Reward")
            adjusted_take_profit = self._validate_and_adjust_rr_ratio(
                entry_price=float(proposed_signal.get('entry_price_proposed')),
                stop_loss=float(proposed_signal.get('stop_loss_proposed')),
                take_profit=float(proposed_signal.get('take_profit_proposed')),
                signal_type=proposed_signal.get('signal_type'),
                logger=logger
            )
            logger.info(f"🎯 Take Profit sau điều chỉnh: {adjusted_take_profit}")
            
            # 4f. Recalculate Expected Profit/Loss with final lot size
            logger.info("💰 Tính toán lợi nhuận/thua lỗ dự kiến")
            expected_loss_per_lot = self._calculate_expected_loss_per_lot(
                entry_price=float(proposed_signal.get('entry_price_proposed')),
                stop_loss=float(proposed_signal.get('stop_loss_proposed')),
                symbol_info=symbol_info,
                logger=logger
            )
            
            estimate_loss = -abs(final_lot_size * expected_loss_per_lot)
            logger.info(f"📉 Thua lỗ dự kiến: ${estimate_loss:.2f}")
            
            # Calculate TP distance from entry
            sl_distance = abs(float(proposed_signal.get('entry_price_proposed')) - float(proposed_signal.get('stop_loss_proposed')))
            tp_distance = abs(adjusted_take_profit - float(proposed_signal.get('entry_price_proposed')))
            
            # Profit = (TP distance / SL distance) * Loss
            if sl_distance > 0:
                estimate_profit = abs((tp_distance / sl_distance) * estimate_loss)
            else:
                estimate_profit = 0
            
            logger.info(f"📈 Lợi nhuận dự kiến: ${estimate_profit:.2f}")
            
            # Calculate Risk-Reward before and after TP adjustment
            try:
                entry_price_val = float(proposed_signal.get('entry_price_proposed'))
                stop_loss_val = float(proposed_signal.get('stop_loss_proposed'))
                take_profit_original = float(proposed_signal.get('take_profit_proposed'))
                sl_dist_val = abs(entry_price_val - stop_loss_val)
                if sl_dist_val > 0:
                    risk_reward_before = abs(entry_price_val - take_profit_original) / sl_dist_val
                    risk_reward_after = abs(entry_price_val - adjusted_take_profit) / sl_dist_val
                else:
                    risk_reward_before = None
                    risk_reward_after = None
            except Exception:
                risk_reward_before = None
                risk_reward_after = None

            # ===== STEP C: BUILD FINAL RESULT =====
            logger.info("[🎯 BƯỚC C: XÂY DỰNG KẾT QUẢ TRẢ VỀ]")
            logger.info(f"✅ Hoàn thành xử lý - STATUS: CONTINUE, Lot Size: {final_lot_size}")

            return self._build_final_response(
                status="CONTINUE",
                symbol=symbol,
                proposed_signal=proposed_signal,
                lot_size=final_lot_size,
                take_profit=adjusted_take_profit,
                estimate_profit=estimate_profit,
                estimate_loss=estimate_loss,
                risk_reward_before=risk_reward_before,
                risk_reward_after=risk_reward_after,
                correlated_symbols=correlated_symbols_found, # Pass to response
                tickets_to_delete=pre_flight_data.get('tickets_to_delete') # Add ticket deletion list
            )

        except Exception as e:
            # If any unexpected error occurs, system returns SKIP
            # to not stop the entire process. Can log error `e` for debugging.
            logger.error(f"❌ LỖI KHÔNG LƯỜNG TRƯỚC: {str(e)}")
            return self._build_final_response(
                status="SKIP", 
                symbol=params.get('symbol', {}).get('origin_name', 'UNKNOWN'), 
                # Try to get technical reasoning if possible
                proposed_signal=params.get('proposed_signal_json', {}),
                reason=f"Unexpected error: {str(e)}"
            )

    def _perform_pre_flight_checks(self, symbol, proposed_signal, portfolio_exposure, max_positions, equity, vTotalRiskCap, symbol_info, vRisk, logger):
        """
        Perform all GO/NO-GO checks in STEP 1 of the prompt.
        
        Returns:
            tuple: (status, reason, data)
        """
        try:
            logger.info("🔍 STEP 1a: KIỂM TRA GIỚI HẠN VỊ THẾ ACTIVE")
            # STEP 1a: Active Position Limit Check
            active_positions = portfolio_exposure.get('active_positions', [])
            logger.info(f"   - Vị thế active hiện tại: {len(active_positions)} (Giới hạn: {max_positions})")
            if len(active_positions) >= max_positions:
                logger.warning(f"   -> ❌ KẾT QUẢ: Thất bại. Đã đạt giới hạn vị thế tối đa.")
                return ("STOP_TRADE", "Max position limit reached", {})
            logger.info("   -> ✅ KẾT QUẢ: Pass.")
            
            logger.info("🔍 STEP 1b: KIỂM TRA LỆNH ACTIVE CÙNG SYMBOL")
            # STEP 1b: Same Symbol Active Trade Check
            is_conflicting_active_trade = False
            for position in active_positions:
                if position.get('symbol') == symbol:
                    logger.info(f"   - Tìm thấy lệnh active cùng symbol: {symbol}")
                    if position.get('profit', 0) < 0:
                        logger.warning(f"   -> ❌ KẾT QUẢ: Thất bại. Lệnh active đang thua lỗ: ${position.get('profit', 0):.2f}")
                        return ("SKIP", "An active trade on the same symbol is losing", {})
                    elif position.get('profit', 0) >= 0:
                        # Check if opposite direction
                        position_type = position.get('type', '')
                        signal_type = proposed_signal.get('signal_type', '')
                        logger.info(f"   - Kiểm tra hướng giao dịch - Position: {position_type}, Signal: {signal_type}")
                        if position_type != signal_type:
                            logger.warning(f"   -> ❌ KẾT QUẢ: Thất bại. Cấm giao dịch ngược hướng trên symbol đang lãi.")
                            return ("SKIP", "Opposite direction trade on a profitable symbol is forbidden", {})
            if not is_conflicting_active_trade:
                logger.info("   -> ✅ KẾT QUẢ: Pass.")

            logger.info("🔍 STEP 1c: KIỂM TRA XUNG ĐỘT LỆNH PENDING (LOGIC MỚI: THAY THẾ)")
            # STEP 1c: Same Symbol Pending Order Conflict Check
            pending_orders_to_delete = []
            if proposed_signal.get('order_type_proposed') in ['LIMIT', 'STOP']:
                pending_orders = portfolio_exposure.get('pending_orders', [])
                logger.info(f"   - Tín hiệu mới là PENDING. Kiểm tra {len(pending_orders)} lệnh chờ hiện có.")
                for order in pending_orders:
                    if order.get('symbol') == symbol:
                        # According to option B: Delete all pending orders of the same symbol, regardless of direction.
                        logger.warning(f"   -> KẾT QUẢ: Tìm thấy lệnh chờ ticket: {order.get('ticket')} cho {symbol}. Sẽ được thay thế.")
                        pending_orders_to_delete.append(order.get('ticket'))
                
                if pending_orders_to_delete:
                    logger.info(f"   -> Sẽ đề xuất xóa {len(pending_orders_to_delete)} lệnh chờ cũ.")
                    return ("CONTINUE", "Pending orders identified for replacement", {'tickets_to_delete': pending_orders_to_delete})

            logger.info("   -> ✅ KẾT QUẢ: Pass.")
            
            logger.info("🔍 STEP 1d: KIỂM TRA TỔNG RỦI RO PORTFOLIO")
            # STEP 1d: Total Unified Portfolio Risk Check
            total_potential_loss_from_portfolio_usd = portfolio_exposure.get('summary', {}).get('total_potential_loss_from_portfolio_usd', 0.0)
            
            # Calculate potential loss for new signal (using vRisk)
            risk_in_usd_new = equity * (vRisk / 100)
            
            total_potential_risk_usd = total_potential_loss_from_portfolio_usd + risk_in_usd_new
            total_risk_percent = (total_potential_risk_usd / equity) * 100
            
            logger.info(f"   - Rủi ro hiện tại: ${total_potential_loss_from_portfolio_usd:.2f}")
            logger.info(f"   - Rủi ro mới (dự kiến): ${risk_in_usd_new:.2f}")
            logger.info(f"   - Tổng rủi ro (dự kiến): ${total_potential_risk_usd:.2f} ({total_risk_percent:.2f}%)")
            logger.info(f"   - Giới hạn rủi ro: {vTotalRiskCap}%")
            
            if total_risk_percent > vTotalRiskCap:
                logger.warning(f"   -> ❌ KẾT QUẢ: Thất bại. Tổng rủi ro vượt quá giới hạn: {total_risk_percent:.2f}% > {vTotalRiskCap}%")
                return ("STOP_TRADE", "Total portfolio risk exceeds cap", {})
            logger.info("   -> ✅ KẾT QUẢ: Pass.")
            
            logger.info("✅ Tất cả kiểm tra pre-flight đã pass")
            return ("CONTINUE", "All pre-flight checks passed", {})
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong pre-flight checks: {str(e)}")
            return ("SKIP", f"Error in pre-flight checks: {str(e)}", {})

    def _calculate_final_lot_size(self, proposed_signal, account_info, symbol_info, portfolio_exposure, correlation_groups, vRisk, params, logger):
        """
        Perform entire STEP 3 of the prompt, calculate lot size from basic to final.
        
        Returns:
            dict: {'final_lot_size': float} or {'status': 'HOLD'}
        """
        try:
            logger.info("🧮 STEP 3a: XÁC ĐỊNH RỦI RO CƠ BẢN")
            # STEP 3a: Determine Base Risk %
            estimate_win_probability = proposed_signal.get('estimate_win_probability', 50)
            logger.info(f"📊 Xác suất thắng: {estimate_win_probability}%")
            
            if estimate_win_probability > 75:
                calculated_risk_percent = 1.5
            elif estimate_win_probability >= 65:
                calculated_risk_percent = 1.2
            elif estimate_win_probability >= 55:
                calculated_risk_percent = 0.8
            else:
                calculated_risk_percent = 0.5
            
            final_risk_percent = min(calculated_risk_percent, vRisk)
            logger.info(f"📊 Rủi ro cơ bản: {calculated_risk_percent}%, Rủi ro cuối cùng (sau khi so sánh với vRisk): {final_risk_percent}%")
            
            logger.info("🧮 STEP 3b: TÍNH TOÁN LOT SIZE BAN ĐẦU")
            # STEP 3b: Calculate Initial Lot Size
            equity = float(account_info.get('equity'))
            risk_in_usd = equity * (final_risk_percent / 100)
            logger.info(f"💰 Rủi ro tính bằng USD: ${risk_in_usd:.2f}")
            
            expected_loss_per_lot = self._calculate_expected_loss_per_lot(
                entry_price=float(proposed_signal.get('entry_price_proposed')),
                stop_loss=float(proposed_signal.get('stop_loss_proposed')),
                symbol_info=symbol_info,
                logger=logger
            )
            
            logger.info(f"📉 Thua lỗ dự kiến cho 1 lot: ${expected_loss_per_lot:.2f}")
            
            if expected_loss_per_lot <= 0:
                logger.warning("❌ Thua lỗ dự kiến <= 0, trả về HOLD")
                return {'status': 'HOLD'}
            
            base_lot_size = risk_in_usd / expected_loss_per_lot
            logger.info(f"📊 Lot size ban đầu: {base_lot_size:.4f}")
            
            logger.info("🧮 STEP 3c: ÁP DỤNG ĐIỀU CHỈNH PORTFOLIO")
            adjusted_lot = base_lot_size
            
            # Drawdown Control - Loss control
            logger.info("   - ** Drawdown Control **")
            profit = float(account_info.get('profit', 0))
            balance = float(account_info.get('balance', 0))
            drawdown_threshold = -(0.04 * balance)
            logger.info(f"     - Profit hiện tại: ${profit:.2f}, Ngưỡng sụt giảm (4%): ${drawdown_threshold:.2f}")

            if profit < drawdown_threshold:
                original_lot = adjusted_lot
                adjusted_lot *= 0.7
                logger.warning(f"     -> KẾT QUẢ: Áp dụng giảm 30%. Lot size: {original_lot:.4f} -> {adjusted_lot:.4f}")
            else:
                logger.info("     -> KẾT QUẢ: Pass. Không điều chỉnh.")
            
            # Correlation Control - Correlation control
            logger.info("   - ** Correlation Control **")
            active_positions = portfolio_exposure.get('active_positions', [])
            symbol_name = proposed_signal.get('symbol', 'UNKNOWN')  # Get from proposed_signal
            
            correlated_symbols = [] # Initialize empty list
            
            # Find correlation group for current symbol
            current_symbol_group = None
            for group_name, group_symbols in correlation_groups.items():
                if symbol_name in group_symbols:
                    current_symbol_group = group_name
                    break
            
            if current_symbol_group:
                logger.info(f"     - Symbol '{symbol_name}' thuộc nhóm tương quan: {current_symbol_group}")
                correlated_positions = 0
                for position in active_positions:
                    pos_symbol = position.get('symbol')
                    if pos_symbol in correlation_groups.get(current_symbol_group, []):
                        correlated_positions += 1
                        correlated_symbols.append(pos_symbol) # Add symbol to list
                
                logger.info(f"     - Số vị thế tương quan đang active: {correlated_positions} - Symbols: {correlated_symbols}")
                if correlated_positions >= 2:
                    original_lot = adjusted_lot
                    adjusted_lot *= 0.5
                    logger.warning(f"     -> KẾT QUẢ: Áp dụng giảm 50%. Lot size: {original_lot:.4f} -> {adjusted_lot:.4f}")
                else:
                    logger.info("     -> KẾT QUẢ: Pass. Không điều chỉnh.")
            else:
                logger.info(f"     - Symbol '{symbol_name}' không thuộc nhóm tương quan nào. Bỏ qua kiểm tra.")

            # Weighted Position Count - Weighted position counting
            logger.info("   - ** Weighted Position Count **")
            num_active = len(portfolio_exposure.get('active_positions', []))
            num_pending = len(portfolio_exposure.get('pending_orders', []))
            effective_positions = num_active + (num_pending * 0.33)
            logger.info(f"     - Vị thế active: {num_active}, Pending: {num_pending} => Vị thế hiệu quả: {effective_positions:.2f}")
            
            original_lot = adjusted_lot
            if effective_positions >= 3:
                adjusted_lot *= 0.5
                logger.warning(f"     -> KẾT QUẢ: >= 3 vị thế hiệu quả, áp dụng giảm 50%. Lot size: {original_lot:.4f} -> {adjusted_lot:.4f}")
            elif 1 <= effective_positions < 3:
                adjusted_lot *= 0.7
                logger.warning(f"     -> KẾT QUẢ: 1-3 vị thế hiệu quả, áp dụng giảm 30%. Lot size: {original_lot:.4f} -> {adjusted_lot:.4f}")
            else:
                logger.info("     -> KẾT QUẢ: Pass. Không điều chỉnh.")
            
            logger.info(f"📊 Lot size sau điều chỉnh portfolio: {adjusted_lot:.4f}")
            
            logger.info(f"📊 Lot size cuối cùng trước lượng tử hóa: {adjusted_lot:.4f}")
            
            initial_quantized_lot = self._quantize_and_validate_lot(
                lot_size=adjusted_lot,
                volume_min=symbol_info.get('volume_min'),
                volume_max=symbol_info.get('volume_max'),
                volume_step=symbol_info.get('volume_step')
            )
            
            if initial_quantized_lot is None:
                logger.warning("❌ Lot size ban đầu sau lượng tử hóa không hợp lệ, trả về HOLD")
                return {'status': 'HOLD'}

            logger.info(f"✅ Lot size ban đầu (đã lượng tử hóa): {initial_quantized_lot}")
            
            # --- NEW: Adaptive Margin Lot Size Search ---
            logger.info("🔄 Bắt đầu dò tìm Lot Size thích ứng với Margin")
            
            lot_size_to_margin_map = params.get('lot_size_to_margin_map')
            if not isinstance(lot_size_to_margin_map, dict) or not lot_size_to_margin_map:
                logger.error("CRITICAL: 'lot_size_to_margin_map' không hợp lệ hoặc bị thiếu.")
                return {'status': 'HOLD', 'correlated_symbols': correlated_symbols}

            current_lot = initial_quantized_lot
            volume_min = symbol_info.get('volume_min', 0.01)
            volume_step = symbol_info.get('volume_step', 0.01)

            while current_lot >= volume_min:
                logger.info(f"   - Đang kiểm tra lot: {current_lot:.2f}...")
                
                # Look up margin from pre-calculated map
                current_lot_str = f"{current_lot:.2f}"
                new_margin = lot_size_to_margin_map.get(current_lot_str)
                
                if new_margin is None:
                    logger.warning(f"   - Không tìm thấy margin cho lot size {current_lot_str} trong map. Bỏ qua.")
                    current_lot = round(current_lot - volume_step, 2)
                    continue
                    
                margin_safe, margin_reason = self._check_margin_safety(
                    account_info, 
                    portfolio_exposure, 
                    new_margin, # Pass looked up margin
                    logger
                )
                
                if margin_safe:
                    logger.info(f"✅ Tìm thấy Lot Size hợp lệ về ký quỹ: {current_lot:.2f}")
                    if current_lot < initial_quantized_lot:
                        logger.warning(f"   - Lot size đã được điều chỉnh giảm từ {initial_quantized_lot} xuống {current_lot:.2f} do hạn chế về ký quỹ.")
                    
                    return {'final_lot_size': current_lot, 'correlated_symbols': correlated_symbols}

                # If not safe, reduce lot size and try again
                current_lot = round(current_lot - volume_step, 2)
            
            # If the loop finishes without finding a suitable lot size
            logger.warning(f"❌ Không tìm thấy Lot Size nào phù hợp sau khi dò tìm. Lot nhỏ nhất ({volume_min}) vẫn không đủ ký quỹ.")
            return {'status': 'HOLD', 'correlated_symbols': correlated_symbols}
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong tính toán lot size: {str(e)}")
            return {'status': 'HOLD', 'correlated_symbols': []}

    def _calculate_expected_loss_per_lot(self, entry_price, stop_loss, symbol_info, logger):
        """
        Calculate the amount (USD) that will be lost if a 1.0 lot trade hits stop loss.
        
        Returns:
            float: Expected loss amount for 1.0 lot
        """
        try:
            trade_tick_value = float(symbol_info.get('trade_tick_value', 0))
            trade_tick_size = float(symbol_info.get('trade_tick_size', 0))
            
            stop_loss_distance_points = abs(entry_price - stop_loss)
            
            logger.info(f"     - Tính toán Loss/Lot: SL distance={stop_loss_distance_points}, Tick value={trade_tick_value}, Tick size={trade_tick_size}")
            
            if trade_tick_size == 0:
                logger.warning("     -> Tick size bằng 0, không thể tính toán.")
                return 0
            
            ticks_in_sl = stop_loss_distance_points / trade_tick_size
            expected_loss_per_lot = ticks_in_sl * trade_tick_value
            
            logger.info(f"     -> Loss/Lot dự kiến: {expected_loss_per_lot:.2f} USD")
            return expected_loss_per_lot
            
        except Exception as e:
            logger.error(f"     -> Lỗi khi tính toán Loss/Lot: {e}")
            return 0

    def _calculate_max_allowed_lot_by_balance(self, balance: float) -> float:
        """
        Calculate maximum allowed lot size based on account balance.
        - Balance < $500: lot size = balance / 8000 (TIER 1: Very small capital)
        - Balance $500-$2000: lot size = balance / 15000 (TIER 2: Small capital)
        - Balance $2000-$5000: lot size = balance / 20000 (TIER 3: Medium capital)
        - Balance >= $5000: lot size = balance / 25000 (TIER 4: Large capital)
        NOTE: Code is upgrading to 4 tiers => different from prompt => no need to worry
        
        Returns:
            float: Maximum allowed lot size
        """
        if balance < 500:  # TIER 1: Very small capital
            return balance / 8000
        elif balance < 2000:  # TIER 2: Small capital
            return balance / 15000
        elif balance < 5000:  # TIER 3: Medium capital
            return balance / 20000
        else:  # TIER 4: Large capital
            return balance / 25000

    def _quantize_and_validate_lot(self, lot_size, volume_min, volume_max, volume_step):
        """
        Round, quantize and validate final lot size against symbol limits.
        
        Process:
        1. Round lot size to 2 decimal places
        2. Quantize according to symbol's volume_step
        3. Ensure within [volume_min, volume_max] range
        4. Check minimum volume_min
        
        Returns:
            float | None: Final valid lot size or None if too small
        """
        try:
            rounded_lot = round(lot_size, 2)
            quantized_lot = math.floor(rounded_lot / volume_step) * volume_step
            final_valid_lot = max(quantized_lot, volume_min)
            final_valid_lot = min(final_valid_lot, volume_max) # RESTORE
            
            if final_valid_lot < volume_min:
                return None
            
            return round(final_valid_lot, 2)
            
        except Exception as e:
            return None

    def _validate_and_adjust_rr_ratio(self, entry_price, stop_loss, take_profit, signal_type, logger):
        """
        Adjust Risk-to-Reward (R:R) ratio according to new logic.
        
        Logic:
        - R:R = TP distance / SL distance
        - If R:R < 1.0: No adjustment (keep original TP)
        - If R:R > 1.5: Mandatory TP adjustment to R:R = 1.5
        - If 1.0 <= R:R <= 1.5: Keep original TP
        
        Returns:
            float: Final take_profit value (may have been adjusted)
        """
        try:
            sl_distance = abs(entry_price - stop_loss)
            if sl_distance == 0:
                logger.warning("     - Khoảng cách Stop Loss bằng 0, không thể điều chỉnh R:R.")
                return take_profit
            
            tp_distance = abs(entry_price - take_profit)
            current_rr = tp_distance / sl_distance
            
            logger.info(f"     - R:R ban đầu: {current_rr:.2f} (TP={take_profit}, SL={stop_loss}, Entry={entry_price})")
            logger.info("     - Quy tắc mới: R:R < 1.0 không điều chỉnh, R:R > 1.5 điều chỉnh về 1.5")
            
            is_buy = signal_type.upper() == 'BUY'
            
            new_take_profit = take_profit
            reason = "R:R nằm trong khoảng cho phép (1.0 <= R:R <= 1.5)."

            if current_rr > 1.5:
                new_tp_distance = sl_distance * 1.5
                new_take_profit = entry_price + new_tp_distance if is_buy else entry_price - new_tp_distance
                reason = f"R:R > 1.5, điều chỉnh TP để R:R = 1.5."
            elif current_rr < 1.0:
                # No adjustment when R:R < 1.0
                reason = f"R:R < 1.0, giữ nguyên TP (không điều chỉnh)."

            if new_take_profit != take_profit:
                logger.info(f"     -> KẾT QUẢ: {reason} TP mới: {new_take_profit}")
            else:
                logger.info(f"     -> KẾT QUẢ: {reason}")
                
            return new_take_profit
                
        except Exception as e:
            logger.error(f"     -> Lỗi khi điều chỉnh R:R: {e}")
            return take_profit

    def _check_margin_safety(self, account_info, portfolio_exposure, new_order_margin_usd, logger):
        """
        Restore margin safety check logic, using standardized calculation method.
        - Free margin > 50% of equity
        - Total margin usage < 40% of equity
        """
        try:
            equity = float(account_info.get('equity', 0))
            if equity == 0:
                return False, "Equity is zero"

            # 1. Get current margin from portfolio (already calculated accurately upstream)
            existing_margin_usd = portfolio_exposure.get('summary', {}).get('total_margin_used_from_portfolio_usd', 0.0)
            
            # 2. NO MORE CALCULATION, USE DIRECTLY
            # new_order_margin_usd has been passed in

            # 3. Calculate and check
            total_margin_usage = existing_margin_usd + new_order_margin_usd
            free_margin_after_trade = equity - total_margin_usage
            
            free_margin_percent = (free_margin_after_trade / equity) * 100
            margin_usage_percent = (total_margin_usage / equity) * 100
            
            logger.info(f"📊 Margin Safety Analysis:")
            logger.info(f"   - Equity: ${equity:.2f}")
            logger.info(f"   - Existing Margin: ${existing_margin_usd:.2f}")
            logger.info(f"   - New Order Margin: ${new_order_margin_usd:.2f}")
            logger.info(f"   - Total Margin Usage (Predicted): ${total_margin_usage:.2f} ({margin_usage_percent:.2f}%)")
            logger.info(f"   - Free Margin (Predicted): ${free_margin_after_trade:.2f} ({free_margin_percent:.2f}%)")
            logger.info(f"   - Rule: Free > 50%, Usage < 40%")
            
            if free_margin_percent <= 50:
                reason = f"Predicted free margin ({free_margin_percent:.2f}%) would be <= 50%"
                logger.warning(f"   -> ❌ KẾT QUẢ: Thất bại. {reason}")
                return False, reason
            
            if margin_usage_percent >= 40:
                reason = f"Predicted total margin usage ({margin_usage_percent:.2f}%) would be >= 40%"
                logger.warning(f"   -> ❌ KẾT QUẢ: Thất bại. {reason}")
                return False, reason
            
            logger.info("   -> ✅ KẾT QUẢ: Pass. An toàn về ký quỹ.")
            return True, "Margin safety rules passed"
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong _check_margin_safety: {str(e)}")
            return False, f"Error in margin safety check: {str(e)}"

    def _build_final_response(self, status, symbol, proposed_signal, **kwargs):
        """
        Package final result into standard dictionary format.
        
        Logic:
        - Create base response with all null values
        - If status = "CONTINUE": Assign actual values from proposed_signal and kwargs
        - If status different: Keep null values, only assign signal = "HOLD"
        
        Returns:
            dict: Final result dictionary with standard format
        """
        # Create base dictionary with null values
        response = {
            "signal": "HOLD" if status in ["HOLD", "SKIP", "STOP_TRADE"] else proposed_signal.get('signal_type'),
            "status": status,
            "lot_size": None,
            "entry_price": None,
            "stop_loss": None,
            "take_profit": None,
            "trailing_stop_loss": proposed_signal.get('trailing_stop_loss'),
            "order_type": None,
            "estimate_win_probability": None,
            "symbol": symbol,
            "estimate_profit": None,
            "estimate_loss": None,
            "technical_reasoning": proposed_signal.get('technical_reasoning'),
            "risk_reward_before": kwargs.get('risk_reward_before'),
            "risk_reward_after": kwargs.get('risk_reward_after'),
            "correlated_symbols": kwargs.get('correlated_symbols'), # Add new field
            "delete_pending_orders": kwargs.get('tickets_to_delete') # Add new field
        }
        
        # If status is CONTINUE, assign values from kwargs
        if status == "CONTINUE":
            response.update({
                "lot_size": kwargs.get('lot_size'),
                "entry_price": proposed_signal.get('entry_price_proposed'),
                "stop_loss": proposed_signal.get('stop_loss_proposed'),
                "take_profit": kwargs.get('take_profit'),
                "order_type": proposed_signal.get('order_type_proposed'),
                "estimate_win_probability": proposed_signal.get('estimate_win_probability'),
                "estimate_profit": kwargs.get('estimate_profit'),
                "estimate_loss": kwargs.get('estimate_loss'),
                "risk_reward_before": kwargs.get('risk_reward_before'),
                "risk_reward_after": kwargs.get('risk_reward_after')
            })
        
        return response
