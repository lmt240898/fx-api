from datetime import datetime

def get_market_context():
    """
    Lấy thông tin market context và timing hiện tại
    
    Returns:
        dict: Thông tin market context với các key:
            - current_time_utc: Thời gian UTC hiện tại
            - current_date: Ngày hiện tại
            - current_day: Ngày trong tuần
            - current_session: Session hiện tại
            - session_status: Trạng thái session
            - next_session: Session tiếp theo
            - overlap_status: Trạng thái overlap
            - trading_recommendation: Khuyến nghị trading
            - day_consideration: Xem xét theo ngày
            - day_recommendation: Khuyến nghị theo ngày
            - market_mood: Tâm trạng thị trường
            - next_event: Sự kiện tiếp theo
            - event_countdown: Đếm ngược đến sự kiện
    """
    # Get current UTC time
    utc_now = datetime.utcnow()
    current_time_utc = utc_now.strftime("%I:%M %p UTC")  # 2:30 PM UTC format
    current_day = utc_now.strftime("%A")  # Monday, Tuesday, etc.
    current_date = utc_now.strftime("%B %d, %Y")  # January 15, 2025
    
    # Determine current market session and status
    current_hour = utc_now.hour
    current_minute = utc_now.minute
    
    # Market session detection
    if 0 <= current_hour < 8:
        current_session = "Asian Session (Tokyo)"
        session_status = "ACTIVE"
        next_session = "European Session (London) - starts in " + str(8 - current_hour) + "h " + str(60 - current_minute) + "m"
    elif 8 <= current_hour < 16:
        current_session = "European Session (London)"
        session_status = "ACTIVE"
        next_session = "American Session (NY) - starts in " + str(16 - current_hour) + "h " + str(60 - current_minute) + "m"
    elif 16 <= current_hour < 24:
        current_session = "American Session (NY)"
        session_status = "ACTIVE"
        next_session = "Asian Session (Tokyo) - starts in " + str(24 - current_hour + 8) + "h " + str(60 - current_minute) + "m"
    
    # Session overlap detection
    if 8 <= current_hour < 10:  # London-Asian overlap
        overlap_status = "HIGH LIQUIDITY - London-Asian Session Overlap"
        trading_recommendation = "Optimal time for entries - high volume and tight spreads"
    elif 13 <= current_hour < 15:  # London-NY overlap
        overlap_status = "HIGHEST LIQUIDITY - London-NY Session Overlap"
        trading_recommendation = "Best trading time - maximum liquidity and volatility"
    elif current_hour == 0 or current_hour == 1:  # Asian session start
        overlap_status = "LOW LIQUIDITY - Asian Session Start"
        trading_recommendation = "Avoid major trades - low volume and wide spreads"
    elif current_hour == 7:  # Asian session end
        overlap_status = "TRANSITION - Asian Session Ending"
        trading_recommendation = "Prepare for London session - expect increased volatility"
    elif current_hour == 15:  # London session end
        overlap_status = "TRANSITION - London Session Ending"
        trading_recommendation = "NY session starting - good for trend continuation trades"
    else:
        overlap_status = "NORMAL LIQUIDITY - Standard Session Conditions"
        trading_recommendation = "Standard trading conditions - normal spreads and volume"
    
    # Day-specific considerations
    if current_day == "Monday":
        day_consideration = "Monday - Watch for weekend gaps and new week positioning"
        day_recommendation = "Start with smaller positions, wait for market direction to establish"
    elif current_day == "Friday":
        day_consideration = "Friday - End of week positioning and profit taking"
        day_recommendation = "Consider shorter-term trades, avoid holding over weekend"
    elif current_day in ["Tuesday", "Wednesday", "Thursday"]:
        day_consideration = f"{current_day} - Mid-week trading, normal market conditions"
        day_recommendation = "Standard trading approach, good for all timeframes"
    else:  # Weekend
        day_consideration = "Weekend - Market closed"
        day_recommendation = "No trading - market closed"
    
    # Time-based market mood
    if 2 <= current_hour < 6:
        market_mood = "Quiet - Low volatility expected"
    elif 6 <= current_hour < 10:
        market_mood = "Building - Volatility increasing"
    elif 10 <= current_hour < 16:
        market_mood = "Active - High volatility and opportunities"
    elif 16 <= current_hour < 20:
        market_mood = "Peak - Maximum volatility and trading opportunities"
    elif 20 <= current_hour < 24:
        market_mood = "Winding down - Volatility decreasing"
    else:
        market_mood = "Very quiet - Minimal market activity"
    
    # Next important market events
    if current_hour < 8:
        next_event = "London Session Opening (08:00 UTC)"
        event_countdown = f"in {8 - current_hour}h {60 - current_minute}m"
    elif current_hour < 13:
        next_event = "NY Session Opening (13:00 UTC)"
        event_countdown = f"in {13 - current_hour}h {60 - current_minute}m"
    elif current_hour < 16:
        next_event = "London Session Closing (16:00 UTC)"
        event_countdown = f"in {16 - current_hour}h {60 - current_minute}m"
    elif current_hour < 20:
        next_event = "NY Session Closing (20:00 UTC)"
        event_countdown = f"in {20 - current_hour}h {60 - current_minute}m"
    else:
        next_event = "Asian Session Opening (00:00 UTC)"
        event_countdown = f"in {24 - current_hour}h {60 - current_minute}m"
    
    return {
        "current_time_utc": current_time_utc,
        "current_date": current_date,
        "current_day": current_day,
        "current_session": current_session,
        "session_status": session_status,
        "next_session": next_session,
        "overlap_status": overlap_status,
        "trading_recommendation": trading_recommendation,
        "day_consideration": day_consideration,
        "day_recommendation": day_recommendation,
        "market_mood": market_mood,
        "next_event": next_event,
        "event_countdown": event_countdown
    }
