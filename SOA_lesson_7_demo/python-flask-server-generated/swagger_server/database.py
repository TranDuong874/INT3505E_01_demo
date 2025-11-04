# coding: utf-8

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class MongoDBConnection:
    """MongoDB connection handler"""
    
    def __init__(self):
        # Get MongoDB connection string from .env file or environment variable or use default
        self.connection_string = os.getenv(
            'DATABASE',
            os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        )
        self.database_name = os.getenv('MONGODB_DATABASE', 'product_db')
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db['products']
            # Create index on id field for faster lookups
            self.collection.create_index('id', unique=True)
            return True
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None
    
    def get_collection(self):
        """Get the products collection"""
        if not self.collection:
            self.connect()
        return self.collection


# Global database connection instance
db_connection = MongoDBConnection()
