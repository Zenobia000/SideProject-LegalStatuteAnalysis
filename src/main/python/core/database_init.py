"""
Database initialization and management utilities
"""
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from .database import engine, Base, SessionLocal
from .config import settings
from ..models import User, Document, LegalArticle, QuestionAnalysis

logger = logging.getLogger(__name__)


def check_database_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            # Simple query to test connection
            result = connection.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_existing_tables() -> list:
    """
    Get list of existing tables in the database
    
    Returns:
        list: List of table names
    """
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get table names: {e}")
        return []


def create_database_tables():
    """
    Create all database tables if they don't exist
    """
    try:
        logger.info("Creating database tables...")
        
        # Import all models to ensure they're registered with Base
        from ..models import User, Document, LegalArticle, QuestionAnalysis
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        existing_tables = get_existing_tables()
        expected_tables = ['users', 'documents', 'legal_articles', 'question_analyses']
        
        for table in expected_tables:
            if table in existing_tables:
                logger.info(f"✓ Table '{table}' created successfully")
            else:
                logger.warning(f"✗ Table '{table}' was not created")
        
        logger.info("Database tables creation completed")
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_database_tables():
    """
    Drop all database tables (use with caution!)
    """
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All database tables dropped")
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def reset_database():
    """
    Reset database by dropping and recreating all tables
    """
    logger.warning("Resetting database...")
    drop_database_tables()
    create_database_tables()
    logger.info("Database reset completed")


def initialize_database():
    """
    Initialize database with tables and basic data
    """
    logger.info("Initializing database...")
    
    # Check connection
    if not check_database_connection():
        raise ConnectionError("Cannot connect to database")
    
    logger.info("✓ Database connection successful")
    
    # Get existing tables
    existing_tables = get_existing_tables()
    logger.info(f"Existing tables: {existing_tables}")
    
    # Create tables if they don't exist
    expected_tables = ['users', 'documents', 'legal_articles', 'question_analyses']
    tables_to_create = [table for table in expected_tables if table not in existing_tables]
    
    if tables_to_create:
        logger.info(f"Creating missing tables: {tables_to_create}")
        create_database_tables()
    else:
        logger.info("All required tables already exist")
    
    # Initialize default data if needed
    try:
        with SessionLocal() as db:
            # Check if we have any users
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("No users found, database is ready for first-time setup")
            else:
                logger.info(f"Database initialized with {user_count} existing users")
    
    except SQLAlchemyError as e:
        logger.error(f"Error checking database state: {e}")
        raise
    
    logger.info("Database initialization completed successfully")


def get_database_info():
    """
    Get information about the current database state
    
    Returns:
        dict: Database information
    """
    info = {
        "connection_status": check_database_connection(),
        "existing_tables": get_existing_tables(),
        "database_url": settings.database_url,
        "table_counts": {}
    }
    
    if info["connection_status"]:
        try:
            with SessionLocal() as db:
                info["table_counts"]["users"] = db.query(User).count()
                info["table_counts"]["documents"] = db.query(Document).count()
                info["table_counts"]["legal_articles"] = db.query(LegalArticle).count()
                info["table_counts"]["question_analyses"] = db.query(QuestionAnalysis).count()
        except SQLAlchemyError as e:
            logger.error(f"Error getting table counts: {e}")
            info["table_counts"] = {"error": str(e)}
    
    return info


if __name__ == "__main__":
    # This script can be run directly to initialize the database
    import sys
    from pathlib import Path
    
    # Add src/main/python to path so we can import modules
    src_path = Path(__file__).parent.parent.parent.parent.parent / "src" / "main" / "python"
    sys.path.insert(0, str(src_path))
    
    from core.logging import setup_logging
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting database initialization...")
    
    try:
        initialize_database()
        
        # Print database info
        db_info = get_database_info()
        logger.info("Database Information:")
        logger.info(f"  Connection: {'✓' if db_info['connection_status'] else '✗'}")
        logger.info(f"  Tables: {db_info['existing_tables']}")
        logger.info(f"  Table counts: {db_info['table_counts']}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)