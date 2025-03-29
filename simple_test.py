from pymongo import MongoClient

def test_connection():
    try:
        # Try to connect to MongoDB
        print("Attempting to connect to MongoDB...")
        client = MongoClient('mongodb://127.0.0.1:27017/')
        
        # Test the connection
        print("Testing connection...")
        client.server_info()
        print("Successfully connected to MongoDB!")
        
        # List databases
        print("\nAvailable databases:")
        for db_name in client.list_database_names():
            print(f"- {db_name}")
            
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure MongoDB is installed")
        print("2. Check if MongoDB service is running:")
        print("   - Press Windows + R")
        print("   - Type 'services.msc'")
        print("   - Look for 'MongoDB' service")
        print("   - Make sure it's running")
        print("3. Try opening MongoDB Compass")
        print("   - Download from: https://www.mongodb.com/try/download/compass")
        print("   - Connect using: mongodb://127.0.0.1:27017")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    test_connection() 