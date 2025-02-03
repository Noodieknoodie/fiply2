"""
Main entry point for the FIPLI application.
This file handles initialization of core components like the database.
"""
from database_operations.connection import init_database, get_session

def initialize_application():
    """Initialize all required components of the application."""
    print("Initializing FIPLI application...")
    
    # Initialize the database first
    print("Initializing database...")
    engine = init_database()
    print("Database initialized successfully!")
    
    return engine

def main():
    """Main entry point of the application."""
    try:
        engine = initialize_application()
        
        # At this point, the database is initialized and ready to use
        # You can add more startup logic here as needed
        
        print("FIPLI application started successfully!")
        return engine
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        raise

if __name__ == "__main__":
    # This means "only run this if you're running this file directly"
    main() 