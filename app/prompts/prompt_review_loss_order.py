import json
from utils.logger import Logger
# Giả định bạn có hàm này trong utils
from utils.market_context import get_market_context

def prompt_review_loss_order(params):
    """
    Prompt cuối cùng để AI review lệnh đang thua lỗ, đã tích hợp phân tích thời gian.
    - Tư duy: Quản lý rủi ro, mặc định là ĐÓNG (CLOSE).
    - Nguồn dữ liệu: 'analyze_price_action' và bối cảnh thị trường.
    - Quy trình: Một luồng 5 bước có hệ thống, bao gồm cả phân tích thời gian.
    - Output: Chi tiết, bao gồm cả mức độ tự tin và tóm tắt.
    """
    logger = Logger("prompts")
    logger.info("===> PROMPT_REVIEW_LOSS_ORDER (FINAL ADVANCED VERSION)")

    # 1. Trích xuất và phân tích cú pháp dữ liệu đầu vào
    order_data = params.get('order_data', {})
    market_data = params.get('market_data', {})

    if isinstance(order_data, str):
        try:
            order_data = json.loads(order_data)
        except json.JSONDecodeError:
            logger.error("Lỗi phân tích cú pháp order_data JSON")
            order_data = {}
    if isinstance(market_data, str):
        try:
            market_data = json.loads(market_data)
        except json.JSONDecodeError:
            logger.error("Lỗi phân tích cú pháp market_data JSON")
            market_data = {}

    # 2. Trích xuất thông tin chi tiết của lệnh
    mt5_data = order_data.get('mt5_position', {})
    db_data = order_data.get('database_info', {})
    
    ticket = mt5_data.get('ticket', 'N/A')
    symbol = mt5_data.get('symbol', 'N/A')
    action = "BUY" if mt5_data.get('type') == 0 else "SELL"
    entry_price = mt5_data.get('price_open', 0)
    current_price = mt5_data.get('price_current', 0)
    stop_loss = mt5_data.get('sl', 0)
    take_profit = mt5_data.get('tp', 0)
    current_profit = mt5_data.get('profit', 0)
    
    estimate_loss = db_data.get('estimate_loss', 0)
    
    technical_reasoning = db_data.get('technical_reasoning', 'Not provided.')
    if not technical_reasoning or technical_reasoning.strip().lower() in ['none', 'n/a', '']:
        technical_reasoning = 'Not provided.'

    if estimate_loss and estimate_loss < 0:
        loss_percentage = (abs(current_profit) / abs(estimate_loss)) * 100
    else:
        loss_percentage = 0

    structured_market_data = json.dumps(market_data, separators=(',', ':'))
    
    # Lấy thông tin bối cảnh thị trường
    try:
        market_context = get_market_context()
    except Exception as e:
        logger.error(f"Không thể lấy market_context: {e}")
        market_context = {
            'current_time_utc': 'N/A', 'current_date': 'N/A', 'current_day': 'N/A',
            'current_session': 'N/A', 'session_status': 'N/A', 'next_session': 'N/A',
            'overlap_status': 'N/A', 'trading_recommendation': 'N/A', 'market_mood': 'N/A',
            'day_consideration': 'N/A', 'day_recommendation': 'N/A', 'next_event': 'N/A',
            'event_countdown': 'N/A'
        }

    # 3. Xây dựng Prompt hoàn chỉnh
    fmessage = f"""You are a professional Risk Manager AI for a trading firm. Your sole task is to review a losing position and decide if it must be closed immediately to preserve capital. Your default bias is to **CLOSE** the position unless there is overwhelming evidence to hold.

        **CORE PRINCIPLES:**
        1.  **Capital Preservation is Paramount:** Your primary directive is to prevent large losses.
        2.  **Objectivity Over Hope:** Analyze the market as it IS, not as you hope it will be.
        3.  **Data-Driven Decisions:** Every decision must be justified by the provided data. You MUST use the pre-analyzed `analyze_price_action` and `indicators` objects.

        **POSITION OVERVIEW:**
        - Ticket: {ticket} | Symbol: {symbol} | Position: {action}
        - Entry Price: {entry_price}
        - Current Price: {current_price}
        - Current Loss: ${current_profit:.2f} (This is {loss_percentage:.1f}% of the way to the Stop Loss)
        - Stop Loss (SL): {stop_loss}
        - Take Profit (TP): {take_profit}

        **CURRENT MARKET CONTEXT & TIMING:**
        - UTC Time: {market_context['current_time_utc']}
        - Current Session: {market_context['current_session']} ({market_context['session_status']})
        - Session Overlap Status: {market_context['overlap_status']}
        - Day Consideration: {market_context['day_consideration']} ({market_context['day_recommendation']})
        - Next Market Event: {market_context['next_event']}

        ---
        **SYSTEMATIC ANALYSIS FRAMEWORK (MANDATORY - FOLLOW STEP-BY-STEP)**

        **STEP 1: RE-EVALUATE MARKET STRUCTURE**
        Using ONLY the `analyze_price_action` data for all timeframes:
        - **Identify Key Levels:** What are the nearest STRONG support/resistance levels to the current price ({current_price})?
        - **Assess Price Context:** Has the price broken any critical levels? For a `{action}` trade, is a key support level holding or has it been violated?
        - **Check Momentum Context:** What does the `volume_context` say?

        **STEP 2: VALIDATE THE ORIGINAL THESIS**
        - **Original Reasoning:** "{technical_reasoning}"
        - **Your Task:** Is this reasoning still valid, or has the market proven it wrong? If no reasoning was provided, does holding a `{action}` position now make any technical sense?

        **STEP 3: CHECK INDICATOR CONFLUENCE**
        Analyze the `indicators` across all timeframes. Are they supporting or fighting the position?
        - **Momentum (RSI, MACD):** Is momentum strongly against the position?
        - **Trend (ADX, SMAs):** Is the price on the wrong side of key MAs? Is ADX > 25, showing a strong trend against the position?

        **STEP 4: INTEGRATE MARKET CONTEXT & TIMING (NEW)**
        Based on the `CURRENT MARKET CONTEXT & TIMING` section, answer this critical question:
        - Does the current session, liquidity level, and day of the week **support** holding this `{action}` position on `{symbol}`? For example, holding a BUY on EURUSD is more favorable during the London session than during a quiet Asian session. A "Low Liquidity" or "End of week profit taking" context increases risk.

        **STEP 5: APPLY THE DECISION MATRIX (FINAL JUDGEMENT)**
        Synthesize all steps to make a final call.

        **---> HOLD (Requires OVERWHELMING evidence - ALL 5 criteria must be met):**
        1.  **Thesis Intact:** The original trade reasoning is still 100% valid.
        2.  **Structure Holding:** Price is reacting positively at a MAJOR pre-identified support (for BUY) or resistance (for SELL).
        3.  **No Major Red Flags:** Indicators are NOT showing strong, sustained momentum against the position.
        4.  **Favorable R:R:** The potential reward (to TP) is still significantly greater than the remaining risk (to SL).
        5.  **Favorable Timing:** The current market session and liquidity conditions support a potential move in the direction of the trade.

        **---> CLOSE (Default Action - ANY ONE of these criteria is enough to trigger):**
        1.  **Thesis Invalidated:** The original reason for the trade is clearly no longer valid.
        2.  **Structure Broken:** A key support (for BUYs) or resistance (for SELLs) has been decisively broken.
        3.  **Strong Opposing Momentum:** Indicators show a strong, accelerating trend against the position.
        4.  **Unfavorable Timing:** The session context (e.g., low liquidity, wrong session for the pair) increases the risk of holding the position.
        5.  **ANY Doubt:** If the analysis is unclear or conflicting, **you MUST default to `CLOSE`** to preserve capital.

        ---
        **PROVIDED DATA (YOUR SOLE SOURCE OF TRUTH):**
        ```json
        {structured_market_data}

        {{
        "signal": "HOLD" or "CLOSE",
        "confidence_level": "High" or "Medium" or "Low",
        "analysis_summary": "A brief, one-sentence justification for the decision, citing the most critical factor (e.g., 'Key support at 1.1630 broken, invalidating the bullish thesis.' or 'Price holding at H4 support 1.1650 with favorable London session timing.')"
        }}
        """
    return fmessage