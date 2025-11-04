#!/usr/bin/env python3

import connexion
from pathlib import Path
from dotenv import load_dotenv

from swagger_server import encoder
from swagger_server.database import db_connection

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def main():
    print("Connecting to MongoDB...")
    print(f"Connection string: {db_connection.connection_string[:50]}...")  # Show first 50 chars for security
    if db_connection.connect():
        print(f"Successfully connected to MongoDB database: {db_connection.database_name}")
    else:
        print("Warning: Failed to connect to MongoDB. The application will continue but database operations may fail.")
    
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Online Shop - API'}, pythonic_params=True)
    
    import atexit
    atexit.register(db_connection.disconnect)
    
    app.run(port=8080)


if __name__ == '__main__':
    main()
