"""
FILE: reset_db.py
Database reset script - DANGER: Drops all tables and recreates them

Usage:
    python reset_db.py

⚠️  WARNING: This will DELETE ALL DATA in the database!
"""
import sys
import logging
from sqlmodel import SQLModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def confirm_reset():
    """Ask for confirmation before resetting database"""
    print("\n")
    print("=" * 70)
    print("⚠️  WARNING: DATABASE RESET")
    print("=" * 70)
    print("This will:")
    print("  1. Drop ALL existing tables")
    print("  2. Delete ALL data")
    print("  3. Create fresh tables")
    print("=" * 70)
    print()
    
    response = input("Are you ABSOLUTELY sure you want to continue? (type 'YES' to confirm): ")
    
    if response != "YES":
        print("❌ Reset cancelled")
        sys.exit(0)
    
    print()
    response = input("This is your last chance. Type 'DELETE ALL DATA' to proceed: ")
    
    if response != "DELETE ALL DATA":
        print("❌ Reset cancelled")
        sys.exit(0)
    
    print()
    logger.info("✅ Confirmation received. Proceeding with reset...")


def reset_database():
    """Drop all tables and recreate them"""
    from src.core.database import engine
    
    # Import all models
    from src.shared.models import (
        Useraccount, Userprofile, PasswordResetToken,
        Region, Lga, Address, Userregion,
        Association, Farmer, Farmtype, Farm,
        Season, Crop, CropRegistry, Livestock, LivestockRegistry,
        BusinessType, PrimaryProduct, AgroAlliedRegistry,
        Notification, Notificationtarget,
        Profileactivityparent, Profileactivity, Profileadditionalactivity,
        Dashboardmetrics, Role, Synclog
    )
    
    try:
        # Drop all tables
        logger.info("🔥 Dropping all tables...")
        SQLModel.metadata.drop_all(engine)
        logger.info("✅ All tables dropped")
        
        print()
        
        # Create all tables
        logger.info("🔨 Creating fresh tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("✅ All tables created")
        
        # List created tables
        tables = list(SQLModel.metadata.tables.keys())
        logger.info(f"📊 Created {len(tables)} tables:")
        for table in sorted(tables):
            logger.info(f"   ✓ {table}")
        
        print()
        logger.info("=" * 70)
        logger.info("🎉 Database reset completed successfully!")
        logger.info("=" * 70)
        logger.info("Next steps:")
        logger.info("1. Run: python init_db.py (to seed initial data)")
        logger.info("2. Or start the API: uvicorn main:app --reload")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error resetting database: {e}")
        sys.exit(1)


def main():
    """Main function"""
    confirm_reset()
    reset_database()


if __name__ == "__main__":
    main()