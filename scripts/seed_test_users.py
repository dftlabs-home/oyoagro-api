"""
FILE: scripts/seed_test_users.py
Seed script to create test admin and officer users
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select, create_engine
from datetime import datetime
from src.shared.models import (
    Useraccount, Userprofile, Address, Userregion,
    Region, Lga, Role
)
from src.core.security import simple_encrypt, generate_salt
from src.core.config import settings


def get_or_create_region(session: Session) -> Region:
    """Get or create test region"""
    region = session.exec(
        select(Region).where(Region.regionname == "Ibadan Zone")
    ).first()
    
    if not region:
        region = Region(
            regionname="Ibadan Zone",
            createdat=datetime.utcnow(),
            version=1
        )
        session.add(region)
        session.flush()
        print(f"✅ Created region: {region.regionname} (ID: {region.regionid})")
    else:
        print(f"ℹ️  Region already exists: {region.regionname} (ID: {region.regionid})")
    
    return region


def get_or_create_lga(session: Session, region: Region) -> Lga:
    """Get or create test LGA"""
    lga = session.exec(
        select(Lga).where(Lga.lganame == "Ibadan North")
    ).first()
    
    if not lga:
        lga = Lga(
            lganame="Ibadan North",
            regionid=region.regionid,
            createdat=datetime.utcnow(),
            version=1
        )
        session.add(lga)
        session.flush()
        print(f"✅ Created LGA: {lga.lganame} (ID: {lga.lgaid})")
    else:
        print(f"ℹ️  LGA already exists: {lga.lganame} (ID: {lga.lgaid})")
    
    return lga


def get_or_create_roles(session: Session) -> dict:
    """Get or create roles"""
    roles = {}
    
    # Admin role (ID: 1)
    admin_role = session.exec(select(Role).where(Role.roleid == 1)).first()
    if not admin_role:
        admin_role = Role(roleid=1, rolename="Admin")
        session.add(admin_role)
        print(f"✅ Created role: Admin (ID: 1)")
    else:
        print(f"ℹ️  Role already exists: Admin (ID: 1)")
    roles['admin'] = admin_role
    
    # Officer role (ID: 2)
    officer_role = session.exec(select(Role).where(Role.roleid == 2)).first()
    if not officer_role:
        officer_role = Role(roleid=2, rolename="Extension Officer")
        session.add(officer_role)
        print(f"✅ Created role: Extension Officer (ID: 2)")
    else:
        print(f"ℹ️  Role already exists: Extension Officer (ID: 2)")
    roles['officer'] = officer_role
    
    session.flush()
    return roles


def create_user(
    session: Session,
    username: str,
    email: str,
    password: str,
    firstname: str,
    lastname: str,
    middlename: str,
    roleid: int,
    lga: Lga,
    region: Region
) -> Useraccount:
    """Create a user with profile, address, and region"""
    
    # Check if user already exists
    existing = session.exec(
        select(Useraccount).where(
            (Useraccount.username == username) | (Useraccount.email == email)
        )
    ).first()
    
    if existing:
        print(f"⚠️  User already exists: {username} ({email})")
        return existing
    
    # Create user account
    salt = generate_salt()
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        username=username,
        email=email,
        passwordhash=encrypted_password,
        salt=salt,
        status=1,
        isactive=True,
        islocked=False,
        logincount=0,
        failedloginattempt=0,
        lgaid=lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(user)
    session.flush()
    
    # Create profile
    profile = Userprofile(
        userid=user.userid,
        firstname=firstname,
        middlename=middlename,
        lastname=lastname,
        email=email,
        phonenumber="08012345678",  # Default phone
        roleid=roleid,
        lgaid=lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(profile)
    
    # Create address
    address = Address(
        userid=user.userid,
        streetaddress="Test Address",
        town="Ibadan",
        postalcode="200001",
        lgaid=lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(address)
    
    # Create user-region mapping
    user_region = Userregion(
        userid=user.userid,
        regionid=region.regionid,
        createdat=datetime.utcnow()
    )
    session.add(user_region)
    
    session.flush()
    
    print(f"✅ Created user: {username} ({email})")
    print(f"   - Role: {'Admin' if roleid == 1 else 'Extension Officer'}")
    print(f"   - User ID: {user.userid}")
    print(f"   - Password: {password}")
    
    return user


def main():
    """Main seeding function"""
    print("=" * 70)
    print("🌱 SEEDING TEST USERS")
    print("=" * 70)
    print()
    
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    
    with Session(engine) as session:
        try:
            print("📋 Step 1: Creating/Verifying Reference Data...")
            print("-" * 70)
            
            # Get or create region
            region = get_or_create_region(session)
            
            # Get or create LGA
            lga = get_or_create_lga(session, region)
            
            # Get or create roles
            roles = get_or_create_roles(session)
            
            session.commit()
            print()
            
            print("👤 Step 2: Creating Users...")
            print("-" * 70)
            
            # Create Admin User
            print("\n1️⃣  ADMIN USER:")
            admin = create_user(
                session=session,
                username="oluwafemip",
                email="oluwafemip.adejumobi@gmail.com",
                password="123456",
                firstname="Oluwafemi",
                lastname="Adejumobi",
                middlename="Philip",
                roleid=1,  # Admin role
                lga=lga,
                region=region
            )
            
            print()
            
            # Create Officer User
            print("2️⃣  OFFICER USER:")
            officer = create_user(
                session=session,
                username="olufemip",
                email="olufemiphil7@gmail.com",
                password="123456",
                firstname="Olu",
                lastname="Ade",
                middlename="Peter",
                roleid=2,  # Officer role
                lga=lga,
                region=region
            )
            
            session.commit()
            print()
            
            print("=" * 70)
            print("✅ SEEDING COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print()
            print("📝 LOGIN CREDENTIALS:")
            print("-" * 70)
            print()
            print("🔐 ADMIN:")
            print(f"   Username: oluwafemip")
            print(f"   Email:    oluwafemip.adejumobi@gmail.com")
            print(f"   Password: 123456")
            print()
            print("🔐 OFFICER:")
            print(f"   Username: olufemip")
            print(f"   Email:    olufemiphil7@gmail.com")
            print(f"   Password: 123456")
            print()
            print("💡 You can login with either username OR email!")
            print("=" * 70)
            
        except Exception as e:
            session.rollback()
            print()
            print("=" * 70)
            print("❌ ERROR DURING SEEDING:")
            print("=" * 70)
            print(f"{str(e)}")
            print()
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()