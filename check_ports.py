#!/usr/bin/env python3
"""
Script kiểm tra port conflicts trước khi chạy Docker stack
"""

import socket
import sys

# Các port mà stack sẽ sử dụng
REQUIRED_PORTS = {
    8080: "Nginx (reverse proxy)",
    8001: "FastAPI (direct access)",
    27019: "MongoDB (external access)",
    6381: "Redis (external access)"
}

def check_port_available(port):
    """Kiểm tra xem port có đang được sử dụng không"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # Port available if connection fails
    except Exception:
        return True  # Assume available if can't check

def main():
    print("🔍 Kiểm tra port conflicts cho FX-API Docker stack...")
    print("=" * 60)
    
    conflicts = []
    
    for port, service in REQUIRED_PORTS.items():
        if check_port_available(port):
            print(f"✅ Port {port:5d} - {service:<30} - Available")
        else:
            print(f"❌ Port {port:5d} - {service:<30} - OCCUPIED")
            conflicts.append(port)
    
    print("=" * 60)
    
    if conflicts:
        print(f"⚠️  CẢNH BÁO: {len(conflicts)} port(s) đang bị sử dụng!")
        print("\nCác port bị xung đột:")
        for port in conflicts:
            print(f"  - Port {port}: {REQUIRED_PORTS[port]}")
        
        print("\n💡 Giải pháp:")
        print("1. Dừng các ứng dụng đang sử dụng port trên")
        print("2. Hoặc thay đổi port trong docker-compose.yml")
        print("3. Sử dụng lệnh sau để xem process đang dùng port:")
        for port in conflicts:
            print(f"   netstat -ano | findstr :{port}")
        
        sys.exit(1)
    else:
        print("🎉 Tất cả port đều available! Có thể chạy Docker stack.")
        print("\n🚀 Để chạy stack:")
        print("   docker-compose up -d --build")
        print("\n🧪 Để test stack:")
        print("   python test_stack.py")

if __name__ == "__main__":
    main()
