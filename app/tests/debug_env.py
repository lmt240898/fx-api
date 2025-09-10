#!/usr/bin/env python3
"""
Debug script to test .env file loading
"""
import os
from dotenv import load_dotenv

print("=== DEBUG .ENV FILE LOADING ===")
print()

# Check current working directory
print(f"Current working directory: {os.getcwd()}")
print()

# Check if .env file exists
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .env file exists at: {os.path.abspath(env_file)}")
    print(f"File size: {os.path.getsize(env_file)} bytes")
else:
    print(f"❌ .env file NOT found at: {os.path.abspath(env_file)}")
print()

# Read .env file content
if os.path.exists(env_file):
    print("📄 .env file content:")
    print("-" * 50)
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"Error reading file: {e}")
        # Try with different encoding
        try:
            with open(env_file, 'r', encoding='latin-1') as f:
                content = f.read()
                print("Content with latin-1 encoding:")
                print(content)
        except Exception as e2:
            print(f"Error with latin-1: {e2}")
    print("-" * 50)
print()

# Test load_dotenv
print("🔄 Testing load_dotenv()...")
print("Before load_dotenv:")
print(f"  AI_API_KEY: {os.getenv('AI_API_KEY', 'NOT SET')[:20]}..." if os.getenv('AI_API_KEY') else "  AI_API_KEY: NOT SET")
print(f"  AI_API_ENDPOINT: {os.getenv('AI_API_ENDPOINT', 'NOT SET')}")
print(f"  MONGO_URI: {os.getenv('MONGO_URI', 'NOT SET')}")
print(f"  REDIS_URI: {os.getenv('REDIS_URI', 'NOT SET')}")
print()

# Load .env file
try:
    result = load_dotenv(env_file)
    print(f"load_dotenv() result: {result}")
except Exception as e:
    print(f"Error in load_dotenv(): {e}")

print()
print("After load_dotenv:")
print(f"  AI_API_KEY: {os.getenv('AI_API_KEY', 'NOT SET')[:20]}..." if os.getenv('AI_API_KEY') else "  AI_API_KEY: NOT SET")
print(f"  AI_API_ENDPOINT: {os.getenv('AI_API_ENDPOINT', 'NOT SET')}")
print(f"  MONGO_URI: {os.getenv('MONGO_URI', 'NOT SET')}")
print(f"  REDIS_URI: {os.getenv('REDIS_URI', 'NOT SET')}")
print()

# Test with absolute path
print("🔄 Testing with absolute path...")
abs_env_path = os.path.abspath(env_file)
try:
    result2 = load_dotenv(abs_env_path)
    print(f"load_dotenv('{abs_env_path}') result: {result2}")
except Exception as e:
    print(f"Error with absolute path: {e}")

print()
print("After load_dotenv with absolute path:")
print(f"  AI_API_KEY: {os.getenv('AI_API_KEY', 'NOT SET')[:20]}..." if os.getenv('AI_API_KEY') else "  AI_API_KEY: NOT SET")
print(f"  AI_API_ENDPOINT: {os.getenv('AI_API_ENDPOINT', 'NOT SET')}")
print(f"  MONGO_URI: {os.getenv('MONGO_URI', 'NOT SET')}")
print(f"  REDIS_URI: {os.getenv('REDIS_URI', 'NOT SET')}")
print()

print("=== END DEBUG ===")
