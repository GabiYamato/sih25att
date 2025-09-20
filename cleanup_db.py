import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData

# Load environment variables
load_dotenv()

# --- DB Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def cleanup_database():
    """Drop all existing tables to start fresh"""
    try:
        with engine.connect() as connection:
            # Get all table names
            result = connection.execute(text("SHOW TABLES;"))
            tables = [row[0] for row in result]
            
            print(f"Found {len(tables)} existing tables: {tables}")
            
            if tables:
                # Disable foreign key checks temporarily
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
                
                # Drop all tables
                for table in tables:
                    print(f"Dropping table: {table}")
                    connection.execute(text(f"DROP TABLE IF EXISTS {table};"))
                
                # Re-enable foreign key checks
                connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                
                # Commit the changes
                connection.commit()
                print("✅ All tables dropped successfully!")
            else:
                print("No tables found to drop.")
                
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

if __name__ == "__main__":
    cleanup_database()
