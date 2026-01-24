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
from src.core.security import simple_encrypt, generate_salt
from src.shared.models import (
    Useraccount, Userprofile, Region, Lga, Association, Season, 
    Crop, Livestock, Farmtype, BusinessType, PrimaryProduct,
    Farmer, Farm, Address
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
# USER FIXTURES
# ============================================================================

@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session):
    """Create admin user for testing"""
    salt = "admin123"
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
        createdat=datetime.utcnow()
    )
    
    session.add(user)
    
    profile = Userprofile(
        userprofileid=100,
        userid=100,
        firstname="Admin",
        lastname="User",
        email="admin@oyoagro.gov.ng",
        phonenumber="08011111111",
        roleid=1,  # Admin role
        createdat=datetime.utcnow()
    )
    
    session.add(profile)
    session.commit()
    session.refresh(user)
    
    return {"user": user, "password": password}


@pytest.fixture(name="officer_user")
def officer_user_fixture(session: Session, test_lga):
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
    session.commit()
    session.refresh(user)
    
    return {"user": user, "password": password}


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
    session.commit()
    session.refresh(farmer)
    
    # Create address for farmer
    address = Address(
        addressid=1,
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
    session.commit()
    session.refresh(farm)
    
    # Create address for farm
    address = Address(
        addressid=2,
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
    
    return farm


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture(name="auth_token")
def auth_token_fixture(client: TestClient, officer_user: dict):
    """Get authentication token for testing protected endpoints"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": officer_user["user"].username,
            "password": officer_user["password"]
        }
    )
    return response.json()["data"]["token"]


@pytest.fixture(name="admin_token")
def admin_token_fixture(client: TestClient, admin_user: dict):
    """Get admin authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": admin_user["user"].username,
            "password": admin_user["password"]
        }
    )
    return response.json()["data"]["token"]


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Get authorization headers for API requests"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(admin_token: str):
    """Get admin authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}


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
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "associations: Association tests")
    config.addinivalue_line("markers", "regions: Region tests")
    config.addinivalue_line("markers", "lgas: LGA tests")
    config.addinivalue_line("markers", "seasons: Season tests")
    config.addinivalue_line("markers", "farmtypes: Farm type tests")
    config.addinivalue_line("markers", "farmers: Farmer tests")
    config.addinivalue_line("markers", "farms: Farm tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")