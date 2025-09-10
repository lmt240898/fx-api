from utils.logger import Logger
import json
import math
import os
from pathlib import Path

__all__ = ['map_signal_to_action']

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

def map_signal_to_action(proposed_signal):
    """Maps a proposed signal's type to an action constant."""
    signal_type = proposed_signal.get('signal_type', 'BUY').upper()
    order_type = proposed_signal.get('order_type_proposed', 'MARKET').upper()

    # Đây là logic ánh xạ chuẩn
    if signal_type == 'BUY':
        if order_type == 'LIMIT': return ORDER_TYPE_BUY_LIMIT
        if order_type == 'STOP': return ORDER_TYPE_BUY_STOP
        return ORDER_TYPE_BUY
    elif signal_type == 'SELL':
        if order_type == 'LIMIT': return ORDER_TYPE_SELL_LIMIT
        if order_type == 'STOP': return ORDER_TYPE_SELL_STOP
        return ORDER_TYPE_SELL
    
    return ORDER_TYPE_BUY # Fallback an toàn