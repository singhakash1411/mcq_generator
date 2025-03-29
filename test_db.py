from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://127.0.0.1:27017/')
        
        # Get database
        db = client['mcq_database']
        
        # Test connection
        client.server_info()
        print("Successfully connected to MongoDB!")
        
        # Create collections if they don't exist
        collections = ['generated_quizzes', 'quiz_responses']
        
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                print(f"Created collection: {collection}")
            else:
                print(f"Collection {collection} already exists")
        
        # Insert a test document
        test_doc = {
            "test": "This is a test document",
            "timestamp": datetime.utcnow()
        }
        
        db['generated_quizzes'].insert_one(test_doc)
        print("Successfully inserted test document!")
        
        # List all databases
        print("\nAvailable databases:")
        for db_name in client.list_database_names():
            print(f"- {db_name}")
            
        # List collections in our database
        print(f"\nCollections in mcq_database:")
        for collection in db.list_collection_names():
            print(f"- {collection}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease make sure MongoDB is installed and running!")
    finally:
        client.close()

if __name__ == "__main__":
    test_mongodb_connection() 