"""
Market Hours Utility Module
Provides functions to check if forex market is open/closed
"""

from datetime import datetime, timezone


class MarketHours:
    """Utility class for checking forex market trading hours"""
    
    @staticmethod
    def is_market_open() -> bool:
        """
        Check if forex market is currently open
        
        Forex Market Hours (UTC):
        - Monday 00:00 UTC (Sydney open) to Friday 22:00 UTC (New York close)
        - Closed: Saturday 22:00 UTC to Sunday 22:00 UTC
        
        Returns:
            bool: True if market is open, False if closed
        """
        current_time_utc = datetime.now(timezone.utc)
        weekday = current_time_utc.weekday()  # 0=Monday, 6=Sunday
        hour = current_time_utc.hour
        
        # Saturday (5) and Sunday (6) - Market closed
        if weekday == 5:  # Saturday
            return False
        elif weekday == 6:  # Sunday
            # Sunday before 22:00 UTC - Market closed
            # Sunday after 22:00 UTC - Market opens (Sydney)
            return hour >= 22
        else:  # Monday (0) to Friday (4)
            if weekday == 4:  # Friday
                # Friday after 22:00 UTC - Market closed
                return hour < 22
            else:  # Monday to Thursday
                return True
    
    @staticmethod
    def is_trading_time_london_ny() -> bool:
        """
        Check if it's London-New York trading hours
        
        Trading Hours:
        - Monday to Friday: 08:00 UTC to 22:00 UTC
        - Weekend: Closed
        
        Returns:
            bool: True if within London-NY hours, False otherwise
        """
        current_time_utc = datetime.now(timezone.utc)
        weekday = current_time_utc.weekday()  # 0=Monday, 6=Sunday
        hour = current_time_utc.hour
        
        # Weekend check
        if weekday >= 5:  # Saturday (5) or Sunday (6)
            return False
        
        # Weekday hours: 08:00 to 22:00 UTC
        return 8 <= hour < 22
    
    @staticmethod
    def get_market_status() -> dict:
        """
        Get detailed market status information
        
        Returns:
            dict: Market status details
        """
        current_time_utc = datetime.now(timezone.utc)
        weekday = current_time_utc.weekday()
        hour = current_time_utc.hour
        
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'current_time_utc': current_time_utc.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'weekday': weekday_names[weekday],
            'hour': hour,
            'is_market_open': MarketHours.is_market_open(),
            'is_london_ny_hours': MarketHours.is_trading_time_london_ny(),
            'is_weekend': weekday >= 5
        }
    
    @staticmethod
    def should_skip_trading() -> tuple[bool, str]:
        """
        Check if trading should be skipped with reason
        
        Returns:
            tuple: (should_skip: bool, reason: str)
        """
        if not MarketHours.is_market_open():
            current_time_utc = datetime.now(timezone.utc)
            weekday = current_time_utc.weekday()
            
            if weekday >= 5:  # Weekend
                return True, "Market closed - Weekend"
            else:
                return True, "Market closed - Outside trading hours"
        
        return False, "Market is open"

    @staticmethod
    def should_skip_trading_broker(broker_info: dict) -> tuple[bool, str]:
        """
        Check if trading should be skipped using BROKER time information.

        Args:
            broker_info: dict returned by MT5Services.get_broker_time_info(),
                         requires keys: 'day_of_week_broker', 'current_time_broker'

        Returns:
            tuple: (should_skip: bool, reason: str)
        """
        try:
            if not broker_info or not isinstance(broker_info, dict):
                return False, "Market is open (No broker info)"

            day_of_week_broker = broker_info.get('day_of_week_broker')
            current_time_broker = broker_info.get('current_time_broker')

            # Weekend check using broker time
            if day_of_week_broker in ['Saturday', 'Sunday']:
                return True, f"Market closed - Weekend (Broker time: {day_of_week_broker} {current_time_broker})"

            # Parse broker time for hour-based checks
            broker_hour = None
            if isinstance(current_time_broker, str):
                try:
                    from datetime import datetime as _dt
                    broker_dt_obj = _dt.strptime(current_time_broker, "%Y/%m/%d %H:%M:%S")
                    broker_hour = broker_dt_obj.hour
                except Exception:
                    # If parsing fails, skip hour-based checks and assume open
                    broker_hour = None

            # Friday after 22:00 (broker time) - market closed
            if day_of_week_broker == 'Friday' and broker_hour is not None and broker_hour >= 22:
                return True, f"Market closed - Outside trading hours (Broker time: {day_of_week_broker} {current_time_broker})"

            # Sunday before 22:00 (broker time) - market closed
            if day_of_week_broker == 'Sunday' and broker_hour is not None and broker_hour < 22:
                return True, f"Market closed - Outside trading hours (Broker time: {day_of_week_broker} {current_time_broker})"

            return False, f"Market is open (Broker time: {day_of_week_broker} {current_time_broker})"
        except Exception:
            # Be conservative: if any unexpected error occurs, report as open to avoid blocking
            return False, "Market is open (Broker check error)"


# Convenience functions for backward compatibility
def is_market_open() -> bool:
    """Check if forex market is currently open"""
    return MarketHours.is_market_open()

def is_trading_time() -> bool:
    """Check if it's within London-NY trading hours"""
    return MarketHours.is_trading_time_london_ny()

def should_skip_weekend_trading() -> bool:
    """Check if current time is weekend (Saturday/Sunday)"""
    current_time_utc = datetime.now(timezone.utc)
    return current_time_utc.weekday() >= 5  # Saturday=5, Sunday=6 