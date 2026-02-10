"""
FILE: tests/conftest.py
Shared pytest fixtures and configuration for all modules
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime, date

from main import app
from src.core.database import get_session
from src.core.security import simple_encrypt, generate_salt, create_access_token
from src.shared.models import (
    Useraccount, Userprofile, Region, Lga, Association, Season, 
    Crop, Livestock, Farmtype, BusinessType, PrimaryProduct,
    Farmer, Farm, Address, Userregion, Role,
    CropRegistry, LivestockRegistry, AgroAlliedRegistry
)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create test database session"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database override"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============================================================================
# REFERENCE DATA FIXTURES
# ============================================================================

@pytest.fixture(name="test_region")
def test_region_fixture(session: Session):
    """Create test region"""
    region = Region(
        regionid=1,
        regionname="Ibadan Zone",
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(region)
    session.commit()
    session.refresh(region)
    return region


@pytest.fixture(name="test_lga")
def test_lga_fixture(session: Session, test_region: Region):
    """Create test LGA"""
    lga = Lga(
        lgaid=1,
        lganame="Ibadan North",
        regionid=test_region.regionid,
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(lga)
    session.commit()
    session.refresh(lga)
    return lga


@pytest.fixture(name="test_association")
def test_association_fixture(session: Session):
    """Create test farmers association"""
    association = Association(
        associationid=1,
        name="Oyo State Farmers Association",
        registrationno="OSFA-001",
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(association)
    session.commit()
    session.refresh(association)
    return association


@pytest.fixture(name="test_season")
def test_season_fixture(session: Session):
    """Create test farming season"""
    season = Season(
        seasonid=1,
        name="2025 Wet Season",
        year=2025,
        startdate=date(2025, 4, 1),
        enddate=date(2025, 10, 31),
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(season)
    session.commit()
    session.refresh(season)
    return season


@pytest.fixture(name="test_crop")
def test_crop_fixture(session: Session):
    """Create test crop type"""
    crop = Crop(
        croptypeid=1,
        name="Maize",
        createdat=datetime.utcnow()
    )
    session.add(crop)
    session.commit()
    session.refresh(crop)
    return crop


@pytest.fixture(name="test_livestock")
def test_livestock_fixture(session: Session):
    """Create test livestock type"""
    livestock = Livestock(
        livestocktypeid=1,
        name="Poultry (Chicken)",
        createdat=datetime.utcnow()
    )
    session.add(livestock)
    session.commit()
    session.refresh(livestock)
    return livestock


@pytest.fixture(name="test_farmtype")
def test_farmtype_fixture(session: Session):
    """Create test farm type"""
    farmtype = Farmtype(
        farmtypeid=1,
        typename="Mixed Farming",
        createdat=datetime.utcnow()
    )
    session.add(farmtype)
    session.commit()
    session.refresh(farmtype)
    return farmtype


@pytest.fixture(name="test_businesstype")
def test_businesstype_fixture(session: Session):
    """Create test business type"""
    businesstype = BusinessType(
        businesstypeid=1,
        name="Processing",
        createdat=datetime.utcnow()
    )
    session.add(businesstype)
    session.commit()
    session.refresh(businesstype)
    return businesstype


@pytest.fixture(name="test_primaryproduct")
def test_primaryproduct_fixture(session: Session):
    """Create test primary product"""
    product = PrimaryProduct(
        primaryproducttypeid=1,
        name="Cassava Flour",
        createdat=datetime.utcnow()
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@pytest.fixture(name="test_role")
def test_role_fixture(session: Session):
    """Create test role"""
    role = Role(
        roleid=2,
        rolename="Extension Officer"
    )
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


# ============================================================================
# USER FIXTURES (Admin & Officers)
# ============================================================================

@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session, test_lga: Lga, test_region: Region):
    """Create admin user for testing"""
    salt = generate_salt()
    password = "AdminPass123"
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        userid=100,
        username="admin",
        email="admin@oyoagro.gov.ng",
        passwordhash=encrypted_password,
        salt=salt,
        status=1,
        isactive=True,
        islocked=False,
        logincount=10,
        failedloginattempt=0,
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(user)
    session.flush()
    
    profile = Userprofile(
        userprofileid=100,
        userid=100,
        firstname="Admin",
        lastname="User",
        email="admin@oyoagro.gov.ng",
        phonenumber="08011111111",
        roleid=1,  # Admin role
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(profile)
    
    # Create user-region
    user_region = Userregion(
        userid=100,
        regionid=test_region.regionid,
        createdat=datetime.utcnow()
    )
    session.add(user_region)
    
    session.commit()
    session.refresh(user)
    
    return {"user": user, "profile": profile, "password": password}


@pytest.fixture(name="officer_user")
def officer_user_fixture(session: Session, test_lga: Lga, test_region: Region):
    """Create extension officer user for testing"""
    salt = generate_salt()
    password = "OfficerPass123"
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        userid=101,
        username="officer1",
        email="officer1@oyoagro.gov.ng",
        passwordhash=encrypted_password,
        salt=salt,
        status=1,
        isactive=True,
        islocked=False,
        logincount=5,
        failedloginattempt=0,
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(user)
    session.flush()
    
    profile = Userprofile(
        userprofileid=101,
        userid=101,
        firstname="Extension",
        lastname="Officer",
        email="officer1@oyoagro.gov.ng",
        phonenumber="08022222222",
        roleid=2,  # Officer role
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(profile)
    
    # Create address
    address = Address(
        userid=101,
        streetaddress="123 Officer Street",
        town="Ibadan",
        postalcode="200001",
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(address)
    
    # Create user-region
    user_region = Userregion(
        userid=101,
        regionid=test_region.regionid,
        createdat=datetime.utcnow()
    )
    session.add(user_region)
    
    session.commit()
    session.refresh(user)
    
    return {"user": user, "profile": profile, "password": password}


# ============================================================================
# FARMER & FARM FIXTURES
# ============================================================================

@pytest.fixture(name="test_farmer")
def test_farmer_fixture(session: Session, test_association: Association, test_lga: Lga, officer_user: dict):
    """Create test farmer with address"""
    farmer = Farmer(
        farmerid=1,
        firstname="John",
        middlename="Ade",
        lastname="Farmer",
        gender="Male",
        dateofbirth=date(1985, 5, 15),
        email="john.farmer@example.com",
        phonenumber="08012345678",
        associationid=test_association.associationid,
        householdsize=5,
        availablelabor=3,
        userid=officer_user["user"].userid,
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(farmer)
    session.flush()
    
    # Create address for farmer
    address = Address(
        farmerid=farmer.farmerid,
        streetaddress="123 Farm Road",
        town="Ibadan",
        postalcode="200001",
        lgaid=test_lga.lgaid,
        latitude=7.3775, # type: ignore
        longitude=3.9470, # type: ignore
        createdat=datetime.utcnow()
    )
    session.add(address)
    session.commit()
    session.refresh(farmer)
    
    return farmer


@pytest.fixture(name="test_farm")
def test_farm_fixture(session: Session, test_farmer: Farmer, test_farmtype: Farmtype, test_lga: Lga):
    """Create test farm with address"""
    farm = Farm(
        farmid=1,
        farmerid=test_farmer.farmerid,
        farmtypeid=test_farmtype.farmtypeid,
        farmsize=5.5, # type: ignore
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(farm)
    session.flush()
    
    # Create address for farm
    address = Address(
        farmid=farm.farmid,
        streetaddress="Farm Location Road",
        town="Ibadan",
        postalcode="200001",
        lgaid=test_lga.lgaid,
        latitude=7.3800,  # type: ignore
        longitude=3.9500, # type: ignore
        createdat=datetime.utcnow()
    )
    session.add(address)
    session.commit()
    session.refresh(farm)
    
    return farm


# ============================================================================
# REGISTRY FIXTURES
# ============================================================================

@pytest.fixture(name="test_crop_registry")
def test_crop_registry_fixture(session: Session, test_farm: Farm, test_season: Season, test_crop: Crop):
    """Create test crop registry"""
    registry = CropRegistry(
        cropregistryid=1,
        farmid=test_farm.farmid,
        seasonid=test_season.seasonid,
        croptypeid=test_crop.croptypeid,
        cropvariety="Oba Super 2",
        areaplanted=5.5, # type: ignore
        plantedquantity=25.0, # type: ignore
        plantingdate=test_season.startdate,
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(registry)
    session.commit()
    session.refresh(registry)
    return registry


@pytest.fixture(name="test_livestock_registry")
def test_livestock_registry_fixture(session: Session, test_farm: Farm, test_season: Season, test_livestock: Livestock):
    """Create test livestock registry"""
    registry = LivestockRegistry(
        livestockregistryid=1,
        farmid=test_farm.farmid,
        seasonid=test_season.seasonid,
        livestocktypeid=test_livestock.livestocktypeid,
        quantity=50,
        startdate=test_season.startdate,
        createdat=datetime.utcnow(),
        version=1
    )
    session.add(registry)
    session.commit()
    session.refresh(registry)
    return registry


@pytest.fixture(name="test_agroallied_registry")
def test_agroallied_registry_fixture(
    session: Session, 
    test_farm: Farm, 
    test_season: Season, 
    test_businesstype: BusinessType,
    test_primaryproduct: PrimaryProduct
):
    """Create test agro-allied registry"""
    registry = AgroAlliedRegistry(
        agroalliedregistryid=1,
        farmid=test_farm.farmid,
        seasonid=test_season.seasonid,
        businesstypeid=test_businesstype.businesstypeid,
        primaryproducttypeid=test_primaryproduct.primaryproducttypeid,
        productioncapacity=1000.0, # type: ignore
        createdat=datetime.utcnow()
    )
    session.add(registry)
    session.commit()
    session.refresh(registry)
    return registry


# ============================================================================
# AUTHENTICATION TOKEN FIXTURES
# ============================================================================

@pytest.fixture(name="auth_token")
def auth_token_fixture(officer_user: dict, session: Session):
    """Generate auth token for officer user"""
    token_data = {
        "UserId": officer_user["user"].userid,
        "UserName": officer_user["user"].username,
        "UserStatus": officer_user["user"].status,
        "Email": officer_user["user"].email
    }
    access_token = create_access_token(data=token_data)
    
    # Update user with token
    officer_user["user"].apitoken = access_token
    session.add(officer_user["user"])
    session.commit()
    
    return access_token


@pytest.fixture(name="admin_token")
def admin_token_fixture(admin_user: dict, session: Session):
    """Generate auth token for admin user"""
    token_data = {
        "UserId": admin_user["user"].userid,
        "UserName": admin_user["user"].username,
        "UserStatus": admin_user["user"].status,
        "Email": admin_user["user"].email
    }
    access_token = create_access_token(data=token_data)
    
    # Update user with token
    admin_user["user"].apitoken = access_token
    session.add(admin_user["user"])
    session.commit()
    
    return access_token


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Get authorization headers for API requests"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(admin_token: str):
    """Get admin authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# TEST USER FIXTURES (For Auth Tests)
# ============================================================================

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session, test_lga, test_region):
    """Create basic test user with encrypted password"""
    from src.shared.models import Userprofile, Address, Userregion
    
    salt = generate_salt()
    password = "TestPassword123"
    encrypted_password = simple_encrypt(password, salt)
    
    user = Useraccount(
        userid=1,
        username="testuser",
        email="test@example.com",
        passwordhash=encrypted_password,
        salt=salt,
        status=1,
        isactive=False,
        islocked=False,
        logincount=0,
        failedloginattempt=0,
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(user)
    session.flush()
    
    # Add profile
    profile = Userprofile(
        userid=user.userid,
        firstname="Test",
        lastname="User",
        email="test@example.com",
        phonenumber="08012345678",
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(profile)
    
    # Add address
    address = Address(
        userid=user.userid,
        streetaddress="Test Address",
        town="Ibadan",
        postalcode="200001",
        lgaid=test_lga.lgaid,
        createdat=datetime.utcnow()
    )
    session.add(address)
    
    # Add user-region
    user_region = Userregion(
        userid=user.userid,
        regionid=test_region.regionid,
        createdat=datetime.utcnow()
    )
    session.add(user_region)
    
    session.commit()
    session.refresh(user)
    
    return {"user": user, "password": password}


# ============================================================================
# EMAIL SERVICE FIXTURES
# ============================================================================

@pytest.fixture(name="mock_email_settings")
def mock_email_settings_fixture():
    """Mock email settings for testing"""
    from src.email.config import email_settings
    
    # Store original values
    original_send = email_settings.SEND_EMAILS
    original_username = email_settings.MAIL_USERNAME
    original_password = email_settings.MAIL_PASSWORD
    
    # Set test values
    email_settings.SEND_EMAILS = False
    email_settings.MAIL_USERNAME = "test@example.com"
    email_settings.MAIL_PASSWORD = "test_password"
    
    yield email_settings
    
    # Restore original values
    email_settings.SEND_EMAILS = original_send
    email_settings.MAIL_USERNAME = original_username
    email_settings.MAIL_PASSWORD = original_password


# ============================================================================
# NOTIFICATION FIXTURES
# ============================================================================

@pytest.fixture(name="test_notifications")
def test_notifications_fixture(session: Session, officer_user: dict):
    """Create test notifications for officer user"""
    from src.notifications.models import Notification
    from src.notifications.types import NotificationType, NotificationPriority
    
    notifications = []
    
    # Notification 1
    notif1 = Notification(
        userid=officer_user["user"].userid,
        type=NotificationType.USER_ACTIVITY.value,
        priority=NotificationPriority.MEDIUM.value,
        title="Notification 1",
        message="Test notification 1",
        isread=False,
        createdat=datetime.utcnow()
    )
    session.add(notif1)
    notifications.append(notif1)
    
    # Notification 2
    notif2 = Notification(
        userid=officer_user["user"].userid,
        type=NotificationType.SYSTEM.value,
        priority=NotificationPriority.LOW.value,
        title="Notification 2",
        message="Test notification 2",
        link="/test",
        isread=False,
        createdat=datetime.utcnow()
    )
    session.add(notif2)
    notifications.append(notif2)
    
    # Notification 3
    notif3 = Notification(
        userid=officer_user["user"].userid,
        type=NotificationType.ALERT.value,
        priority=NotificationPriority.HIGH.value,
        title="Notification 3",
        message="Test notification 3",
        notif_metadata={"test": "data"},  # FIXED: Use notif_metadata
        isread=False,
        createdat=datetime.utcnow()
    )
    session.add(notif3)
    notifications.append(notif3)
    
    session.commit()
    
    for notif in notifications:
        session.refresh(notif)
    
    return notifications


@pytest.fixture(name="multiple_officers")
def multiple_officers_fixture(session: Session, test_lga: Lga, test_region: Region):
    """Create multiple officer users for broadcast testing"""
    officers = []
    
    for i in range(2, 5):  # Create officers with IDs 102, 103, 104
        salt = generate_salt()
        password = f"OfficerPass{i}"
        encrypted_password = simple_encrypt(password, salt)
        
        user = Useraccount(
            userid=100 + i,
            username=f"officer{i}",
            email=f"officer{i}@oyoagro.gov.ng",
            passwordhash=encrypted_password,
            salt=salt,
            status=1,
            isactive=True,
            islocked=False,
            lgaid=test_lga.lgaid,
            createdat=datetime.utcnow()
        )
        session.add(user)
        session.flush()
        
        profile = Userprofile(
            userid=user.userid,
            firstname=f"Officer{i}",
            lastname="Test",
            email=f"officer{i}@oyoagro.gov.ng",
            phonenumber=f"0802222222{i}",
            roleid=2,  # Officer role
            lgaid=test_lga.lgaid,
            createdat=datetime.utcnow()
        )
        session.add(profile)
        
        # Create user-region
        user_region = Userregion(
            userid=user.userid,
            regionid=test_region.regionid,
            createdat=datetime.utcnow()
        )
        session.add(user_region)
        
        officers.append({"user": user, "profile": profile, "password": password})
    
    session.commit()
    return officers


@pytest.fixture(name="test_broadcast")
def test_broadcast_fixture(session: Session, admin_user: dict, multiple_officers: list):
    """Create test broadcast with notifications"""
    from src.notifications.models import Broadcast, Notification
    from src.notifications.types import NotificationType, NotificationPriority
    
    # Create broadcast
    broadcast = Broadcast(
        senderid=admin_user["user"].userid,
        title="Test Broadcast",
        message="This is a test broadcast message",
        priority=NotificationPriority.MEDIUM.value,
        recipienttype="all",
        totalrecipients=3,
        deliveredcount=3,
        readcount=0,
        status="completed",
        createdat=datetime.utcnow(),
        sentat=datetime.utcnow(),
        completedat=datetime.utcnow()
    )
    session.add(broadcast)
    session.flush()
    
    # Create notifications for each officer
    for officer in multiple_officers:
        notification = Notification(
            userid=officer["user"].userid,
            type=NotificationType.ADMIN_BROADCAST.value,
            priority=NotificationPriority.MEDIUM.value,
            title="Test Broadcast",
            message="This is a test broadcast message",
            broadcastid=broadcast.broadcastid,
            isread=False,
            createdat=datetime.utcnow()
        )
        session.add(notification)
    
    session.commit()
    session.refresh(broadcast)
    
    return broadcast


# ============================================================================
# SETUP & TEARDOWN
# ============================================================================

@pytest.fixture(autouse=True)
def reset_database(session: Session):
    """Reset database state between tests"""
    yield
    # Cleanup is automatic with session fixture
    session.rollback()


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    # Authentication
    config.addinivalue_line("markers", "auth: Authentication tests")
    
    # Email
    config.addinivalue_line("markers", "email: Email service tests")
    
    # Notifications
    config.addinivalue_line("markers", "notifications: Notification tests")
    
    # Admin
    config.addinivalue_line("markers", "admin: Admin user management tests")
    
    # Reference data
    config.addinivalue_line("markers", "associations: Association tests")
    config.addinivalue_line("markers", "regions: Region tests")
    config.addinivalue_line("markers", "lgas: LGA tests")
    config.addinivalue_line("markers", "seasons: Season tests")
    config.addinivalue_line("markers", "farmtypes: Farm type tests")
    config.addinivalue_line("markers", "crops: Crop tests")
    config.addinivalue_line("markers", "livestock: Livestock tests")
    config.addinivalue_line("markers", "businesstypes: Business type tests")
    config.addinivalue_line("markers", "primaryproducts: Primary product tests")
    
    # Farmer & Farm
    config.addinivalue_line("markers", "farmers: Farmer tests")
    config.addinivalue_line("markers", "farms: Farm tests")
    
    # Data collection
    config.addinivalue_line("markers", "cropregistry: Crop registry tests")
    config.addinivalue_line("markers", "livestockregistry: Livestock registry tests")
    config.addinivalue_line("markers", "agroalliedregistry: Agro-allied registry tests")
    
    # General
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "asyncio: Async tests")