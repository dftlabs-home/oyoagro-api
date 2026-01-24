"""
FILE: init_db.py
Database initialization script - Run this to create all tables

Usage:
    python init_db.py

This script will:
1. Check database connection
2. Create all tables if they don't exist
3. Optionally seed initial data
"""
import sys
import logging
from sqlmodel import Session, select
from datetime import datetime, date

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    from src.core.database import engine, check_database_connection
    from sqlmodel import SQLModel
    
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
    
    logger.info("=" * 60)
    logger.info("OyoAgro Database Initialization")
    logger.info("=" * 60)
    
    # Check connection
    logger.info("🔍 Checking database connection...")
    if not check_database_connection():
        logger.error("❌ Database connection failed. Please check your DATABASE_URL")
        sys.exit(1)
    
    # Create tables
    logger.info("🔨 Creating database tables...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("✅ All tables created successfully!")
        
        # List created tables
        tables = list(SQLModel.metadata.tables.keys())
        logger.info(f"📊 Created {len(tables)} tables:")
        for table in sorted(tables):
            logger.info(f"   ✓ {table}")
            
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        sys.exit(1)


def seed_roles():
    """Seed initial roles"""
    from src.core.database import engine
    from src.shared.models import Role
    
    logger.info("🌱 Seeding roles...")
    
    roles = [
        {"roleid": 1, "rolename": "Admin"},
        {"roleid": 2, "rolename": "Extension Officer"},
        {"roleid": 3, "rolename": "Data Analyst"},
    ]
    
    try:
        with Session(engine) as session:
            for role_data in roles:
                # Check if role exists
                existing = session.exec(
                    select(Role).where(Role.roleid == role_data["roleid"])
                ).first()
                
                if not existing:
                    role = Role(**role_data)
                    session.add(role)
                    logger.info(f"   ✓ Created role: {role_data['rolename']}")
                else:
                    logger.info(f"   ⊙ Role already exists: {role_data['rolename']}")
            
            session.commit()
        
        logger.info("✅ Roles seeded successfully")
        
    except Exception as e:
        logger.error(f"❌ Error seeding roles: {e}")


def seed_sample_data():
    """Seed sample reference data (optional)"""
    from src.core.database import engine
    from src.shared.models import Region, Lga, Farmtype
    
    logger.info("🌱 Seeding sample reference data...")
    
    try:
        with Session(engine) as session:
            # Check if data already exists
            existing_regions = session.exec(select(Region)).first()
            
            if existing_regions:
                logger.info("   ⊙ Sample data already exists, skipping...")
                return
            
            # Create sample regions
            regions = [
                {"regionname": "Ibadan Zone", "createdat": datetime.utcnow(), "version": 1},
                {"regionname": "Ogbomoso Zone", "createdat": datetime.utcnow(), "version": 1},
                {"regionname": "Oyo Zone", "createdat": datetime.utcnow(), "version": 1},
            ]
            
            region_objects = []
            for region_data in regions:
                region = Region(**region_data)
                session.add(region)
                region_objects.append(region)
                logger.info(f"   ✓ Created region: {region_data['regionname']}")
            
            session.commit()
            
            # Refresh to get IDs
            for region in region_objects:
                session.refresh(region)
            
            # Create sample LGAs for Ibadan Zone
            lgas = [
                {"lganame": "Ibadan North", "regionid": region_objects[0].regionid},
                {"lganame": "Ibadan South", "regionid": region_objects[0].regionid},
                {"lganame": "Ibadan North-East", "regionid": region_objects[0].regionid},
            ]
            
            for lga_data in lgas:
                lga = Lga(
                    **lga_data,
                    createdat=datetime.utcnow(),
                    version=1
                )
                session.add(lga)
                logger.info(f"   ✓ Created LGA: {lga_data['lganame']}")
            
            session.commit()
            
            # Create sample farm types
            farmtypes = [
                {"typename": "Crop Farming", "description": "Focuses on crop production"},
                {"typename": "Livestock Farming", "description": "Focuses on animal husbandry"},
                {"typename": "Mixed Farming", "description": "Combination of crops and livestock"},
            ]
            
            for ft_data in farmtypes:
                farmtype = Farmtype(
                    **ft_data, # type: ignore
                    createdat=datetime.utcnow()
                )
                session.add(farmtype)
                logger.info(f"   ✓ Created farm type: {ft_data['typename']}")
            
            session.commit()
            
        logger.info("✅ Sample data seeded successfully")
        
    except Exception as e:
        logger.error(f"❌ Error seeding sample data: {e}")


def create_admin_user():
    """Create default admin user"""
    from src.core.database import engine
    from src.shared.models import Useraccount, Userprofile
    from src.core.security import simple_encrypt, generate_salt
    
    logger.info("👤 Creating default admin user...")
    
    try:
        with Session(engine) as session:
            # Check if admin exists
            existing = session.exec(
                select(Useraccount).where(Useraccount.username == "admin")
            ).first()
            
            if existing:
                logger.info("   ⊙ Admin user already exists")
                return
            
            # Create admin user
            salt = generate_salt()
            password = "Admin@123"  # Default password - CHANGE THIS!
            encrypted_password = simple_encrypt(password, salt)
            
            admin = Useraccount(
                username="admin",
                email="admin@oyoagro.gov.ng",
                passwordhash=encrypted_password,
                salt=salt,
                status=1,
                isactive=True,
                islocked=False,
                logincount=0,
                failedloginattempt=0,
                createdat=datetime.utcnow()
            )
            
            session.add(admin)
            session.commit()
            session.refresh(admin)
            
            # Create admin profile
            profile = Userprofile(
                userid=admin.userid,
                firstname="System",
                lastname="Administrator",
                email="admin@oyoagro.gov.ng",
                phonenumber="08000000000",
                roleid=1,  # Admin role
                createdat=datetime.utcnow(),
                version=1
            )
            
            session.add(profile)
            session.commit()
            
            logger.info("✅ Admin user created successfully")
            logger.info("=" * 60)
            logger.info("🔑 DEFAULT ADMIN CREDENTIALS")
            logger.info("=" * 60)
            logger.info(f"   Username: admin")
            logger.info(f"   Password: {password}")
            logger.info("=" * 60)
            logger.info("⚠️  IMPORTANT: Change this password immediately!")
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")


def main():
    """Main initialization function"""
    print("\n")
    
    # Step 1: Create tables
    create_tables()
    print()
    
    # Step 2: Seed roles
    seed_roles()
    print()
    
    # Step 3: Ask about sample data
    print("=" * 60)
    response = input("Would you like to seed sample reference data? (y/n): ")
    if response.lower() == 'y':
        seed_sample_data()
        print()
    
    # Step 4: Ask about admin user
    print("=" * 60)
    response = input("Would you like to create a default admin user? (y/n): ")
    if response.lower() == 'y':
        create_admin_user()
        print()
    
    # Success message
    logger.info("=" * 60)
    logger.info("🎉 Database initialization completed successfully!")
    logger.info("=" * 60)
    logger.info("Next steps:")
    logger.info("1. Start the API: uvicorn main:app --reload")
    logger.info("2. Visit: http://localhost:8000/docs")
    logger.info("3. Login with admin credentials (if created)")
    logger.info("=" * 60)
    print()


if __name__ == "__main__":
    main()