import sys
import subprocess
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def check_python_version():
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

def check_pip_packages():
    try:
        import pymongo
        print(f"pymongo version: {pymongo.__version__}")
    except ImportError:
        print("pymongo is not installed!")
        return False
    return True

def check_mongodb_service():
    try:
        # Try to run mongod --version
        result = subprocess.run(['mongod', '--version'], capture_output=True, text=True)
        print("MongoDB is installed:")
        print(result.stdout)
        return True
    except FileNotFoundError:
        print("MongoDB is not installed or not in PATH")
        return False

def test_mongodb_connection():
    print("\nTesting MongoDB connection...")
    try:
        # Try different connection strings
        connection_strings = [
            'mongodb://127.0.0.1:27017/',
            'mongodb://localhost:27017/',
            'mongodb://localhost:27017'
        ]
        
        for uri in connection_strings:
            print(f"\nTrying connection string: {uri}")
            try:
                client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                client.server_info()  # Will throw an exception if connection fails
                print(f"Successfully connected using: {uri}")
                return True
            except ConnectionFailure as e:
                print(f"Connection failed: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
            finally:
                try:
                    client.close()
                except:
                    pass
        
        return False
    except Exception as e:
        print(f"Error during connection test: {e}")
        return False

def main():
    print("=== MongoDB Connection Diagnostic Tool ===\n")
    
    # Check Python environment
    print("1. Checking Python environment:")
    check_python_version()
    
    # Check required packages
    print("\n2. Checking required packages:")
    if not check_pip_packages():
        print("\nPlease install pymongo using:")
        print("python -m pip install pymongo")
        return
    
    # Check MongoDB installation
    print("\n3. Checking MongoDB installation:")
    if not check_mongodb_service():
        print("\nPlease install MongoDB from:")
        print("https://www.mongodb.com/try/download/community")
        return
    
    # Test MongoDB connection
    print("\n4. Testing MongoDB connection:")
    if not test_mongodb_connection():
        print("\nTroubleshooting steps:")
        print("1. Make sure MongoDB service is running:")
        print("   - Press Windows + R")
        print("   - Type 'services.msc'")
        print("   - Find 'MongoDB' service")
        print("   - Make sure it's running")
        print("2. Try installing MongoDB Compass:")
        print("   - Download from: https://www.mongodb.com/try/download/compass")
        print("   - Connect using: mongodb://127.0.0.1:27017")
        print("3. Check if MongoDB is listening on port 27017:")
        print("   - Open Command Prompt as Administrator")
        print("   - Run: netstat -an | findstr 27017")

if __name__ == "__main__":
    main() 