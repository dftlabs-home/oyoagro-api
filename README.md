# OyoAgro API Documentation

> **Oyo State Agricultural Data Management System**  
> A comprehensive FastAPI-based REST API for managing agricultural data collection, farmer registration, farm management, and crop/livestock tracking in Oyo State, Nigeria.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-latest-orange.svg)](https://sqlmodel.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
  - [Authentication](#authentication-endpoints)
  - [Associations](#associations-endpoints)
  - [Regions](#regions-endpoints)
  - [LGAs](#lgas-endpoints)
  - [Seasons](#seasons-endpoints)
  - [Farm Types](#farm-types-endpoints)
  - [Farmers](#farmers-endpoints)
  - [Farms](#farms-endpoints)
- [Authentication & Authorization](#authentication--authorization)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Development](#development)

---

## 🎯 Overview

The OyoAgro API is a modular monolith REST API designed to digitize and streamline agricultural data management for Oyo State, Nigeria. It provides endpoints for:

- **User Management**: Authentication, authorization, and role-based access control
- **Reference Data**: Regions, LGAs, Associations, Seasons, Farm Types
- **Farmer Management**: Registration, profile management, and tracking
- **Farm Management**: Farm registration, location tracking, and type classification
- **Data Collection**: Crop, livestock, and agro-allied enterprise tracking

---

## ✨ Features

### Core Features
- ✅ **JWT-based Authentication** - Secure token-based authentication
- ✅ **Role-Based Access Control** - Admin and Extension Officer roles
- ✅ **Soft Deletes** - Data preservation with logical deletion
- ✅ **Pagination** - Efficient data retrieval for large datasets
- ✅ **Search & Filtering** - Advanced query capabilities
- ✅ **Comprehensive Validation** - Input validation with Pydantic
- ✅ **Audit Trails** - Timestamps and version tracking
- ✅ **Geographic Data** - GPS coordinates and LGA-based organization

### Advanced Features
- ✅ **Password Reset Flow** - Email-based password recovery
- ✅ **Account Locking** - Security after failed login attempts
- ✅ **C# Compatibility** - XOR encryption for .NET integration
- ✅ **Statistics Endpoints** - Dashboard-ready aggregated data
- ✅ **Relationship Validation** - Ensures data integrity
- ✅ **Multi-level Filtering** - Filter by region, LGA, association, etc.

---

## 🛠 Technology Stack

- **Framework**: FastAPI 0.104+
- **ORM**: SQLModel (built on SQLAlchemy)
- **Database**: PostgreSQL 13+
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-cov
- **Documentation**: OpenAPI/Swagger (auto-generated)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- pip or uv for dependency management

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd oyoagro-api
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

Example `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/oyoagrodb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Initialize database**

**Option A: Use Existing Database**
```bash
# If you already have a database with tables, just configure .env and skip to step 6
```

**Option B: Create New Database (Automated)**
```bash
# Create empty PostgreSQL database first
createdb oyoagrodb

# Run initialization script
python init_db.py
```

This will:
- ✅ Create all 25+ database tables
- ✅ Seed roles (Admin, Extension Officer)
- ✅ Optionally seed sample data (regions, LGAs, farm types)
- ✅ Optionally create default admin user

**Default Admin Credentials (if created):**
- Username: `admin`
- Password: `Admin@123`
- ⚠️ Change immediately in production!

See [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for detailed database management instructions.

6. **Run the application**
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Standard Response Format
All endpoints return responses in this format:
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful",
  "total": 0,
  "tag": 1
}
```

---

## 🔐 Authentication Endpoints

### POST `/auth/register`
**Register a new user account**

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "firstname": "John",
  "lastname": "Doe",
  "phonenumber": "08012345678",
  "roleid": 2,
  "lgaid": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "userid": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "tag": 1
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric + underscore
- Email: Valid email format
- Password: 8+ characters, uppercase, lowercase, number
- Phone: 11 digits, starts with 0

---

### POST `/auth/login`
**Authenticate and receive JWT token**

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "userid": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "roleid": 2,
      "lgaid": 1
    }
  },
  "tag": 1
}
```

**Security Features:**
- Account locks after 5 failed attempts
- Inactive/locked accounts cannot login
- Login count and last login date tracked

---

### POST `/auth/logout`
**Invalidate current JWT token**

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully",
  "tag": 1
}
```

---

### POST `/auth/forgot-password`
**Request password reset token**

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset token generated",
  "data": {
    "reset_token": "550e8400-e29b-41d4-a716-446655440000"
  },
  "tag": 1
}
```

**Note:** In production, this would send an email instead of returning the token.

---

### POST `/auth/reset-password`
**Reset password with token**

**Request Body:**
```json
{
  "token": "550e8400-e29b-41d4-a716-446655440000",
  "new_password": "NewSecurePass123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset successful",
  "tag": 1
}
```

---

### GET `/auth/validate-reset-token/{token}`
**Validate if reset token is valid**

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "email": "john@example.com"
  },
  "tag": 1
}
```

---

## 🏢 Associations Endpoints

Manage farmer associations/cooperatives.

### POST `/associations/`
**Create new association**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Oyo State Farmers Association",
  "registrationno": "OSFA-001"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Association created successfully",
  "data": {
    "associationid": 1,
    "name": "Oyo State Farmers Association",
    "registrationno": "OSFA-001",
    "createdat": "2026-01-24T10:00:00",
    "version": 1
  },
  "tag": 1
}
```

---

### GET `/associations/`
**Get all associations (paginated)**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

**Example:** `GET /associations/?skip=0&limit=50`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "associationid": 1,
      "name": "Oyo State Farmers Association",
      "registrationno": "OSFA-001",
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/associations/search`
**Search associations by name or registration number**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `q`: Search query (min 2 characters)
- `skip`: Pagination offset
- `limit`: Results limit

**Example:** `GET /associations/search?q=Oyo&limit=20`

---

### GET `/associations/{association_id}`
**Get association by ID**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "data": {
    "associationid": 1,
    "name": "Oyo State Farmers Association",
    "registrationno": "OSFA-001",
    "createdat": "2026-01-24T10:00:00",
    "updatedat": null,
    "version": 1
  },
  "tag": 1
}
```

---

### PUT `/associations/{association_id}`
**Update association**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated Association Name"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Association updated successfully",
  "data": {
    "associationid": 1,
    "name": "Updated Association Name",
    "version": 2
  },
  "tag": 1
}
```

---

### DELETE `/associations/{association_id}`
**Delete association (soft delete)**

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Association deleted successfully",
  "tag": 1
}
```

**Note:** Cannot delete if association has farmers.

---

## 🗺 Regions Endpoints

Manage geographical regions (zones).

### POST `/regions/`
**Create new region**

**Request Body:**
```json
{
  "regionname": "Ibadan Zone"
}
```

---

### GET `/regions/`
**Get all regions (paginated)**

**Query Parameters:**
- `skip`: Pagination offset
- `limit`: Results limit

---

### GET `/regions/with-lgas`
**Get regions with LGA counts**

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "regionid": 1,
      "regionname": "Ibadan Zone",
      "lga_count": 5,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/regions/{region_id}/lgas`
**Get region with all its LGAs**

**Response:**
```json
{
  "success": true,
  "data": {
    "regionid": 1,
    "regionname": "Ibadan Zone",
    "lga_count": 5,
    "lgas": [
      {
        "lgaid": 1,
        "lganame": "Ibadan North"
      },
      {
        "lgaid": 2,
        "lganame": "Ibadan South"
      }
    ]
  },
  "tag": 1
}
```

---

### GET `/regions/search`
**Search regions by name**

**Query Parameters:**
- `q`: Search query

---

### PUT `/regions/{region_id}`
**Update region**

---

### DELETE `/regions/{region_id}`
**Delete region (soft delete)**

**Note:** Cannot delete if region has LGAs.

---

## 🏘 LGAs Endpoints

Manage Local Government Areas.

### POST `/lgas/`
**Create new LGA**

**Request Body:**
```json
{
  "lganame": "Ibadan North",
  "regionid": 1
}
```

**Validation:**
- Region must exist
- LGA name must be unique within region

---

### GET `/lgas/`
**Get all LGAs (paginated)**

**Query Parameters:**
- `skip`: Pagination offset
- `limit`: Results limit
- `region_id`: Filter by region (optional)

**Example:** `GET /lgas/?region_id=1&limit=50`

---

### GET `/lgas/by-region/{region_id}`
**Get all LGAs in a specific region**

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "lgaid": 1,
      "lganame": "Ibadan North",
      "regionid": 1,
      "region_name": "Ibadan Zone"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/lgas/{lga_id}/stats`
**Get LGA with statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "lgaid": 1,
    "lganame": "Ibadan North",
    "regionid": 1,
    "region_name": "Ibadan Zone",
    "farmer_count": 150,
    "farm_count": 180,
    "officer_count": 5
  },
  "tag": 1
}
```

---

### GET `/lgas/search`
**Search LGAs**

**Query Parameters:**
- `q`: Search query
- `region_id`: Filter by region (optional)

---

### PUT `/lgas/{lga_id}`
**Update LGA**

---

### DELETE `/lgas/{lga_id}`
**Delete LGA (soft delete)**

**Note:** Cannot delete if LGA has farmers, farms, or officers.

---

## 🌾 Seasons Endpoints

Manage farming seasons.

### POST `/seasons/`
**Create new season**

**Request Body:**
```json
{
  "name": "2025 Wet Season",
  "year": 2025,
  "startdate": "2025-04-01",
  "enddate": "2025-10-31"
}
```

**Validation:**
- End date must be after start date
- Year must match date range
- Seasons cannot overlap in same year

---

### GET `/seasons/`
**Get all seasons (paginated)**

**Query Parameters:**
- `skip`: Pagination offset
- `limit`: Results limit
- `year`: Filter by year (optional)

**Example:** `GET /seasons/?year=2025`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "seasonid": 1,
      "name": "2025 Wet Season",
      "year": 2025,
      "startdate": "2025-04-01",
      "enddate": "2025-10-31",
      "is_active": true,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/seasons/active`
**Get currently active season**

**Response:**
```json
{
  "success": true,
  "data": {
    "seasonid": 1,
    "name": "2025 Wet Season",
    "year": 2025,
    "startdate": "2025-04-01",
    "enddate": "2025-10-31",
    "is_active": true,
    "days_remaining": 120
  },
  "tag": 1
}
```

**Note:** Returns `is_active: false` if no active season.

---

### GET `/seasons/year/{year}`
**Get all seasons in a specific year**

**Example:** `GET /seasons/year/2025`

---

### GET `/seasons/{season_id}/stats`
**Get season with statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "seasonid": 1,
    "name": "2025 Wet Season",
    "year": 2025,
    "startdate": "2025-04-01",
    "enddate": "2025-10-31",
    "is_active": true,
    "days_remaining": 120,
    "crop_registry_count": 450,
    "livestock_registry_count": 200,
    "agroallied_registry_count": 50
  },
  "tag": 1
}
```

---

### GET `/seasons/search`
**Search seasons by name**

---

### PUT `/seasons/{season_id}`
**Update season**

---

### DELETE `/seasons/{season_id}`
**Delete season (soft delete)**

**Note:** Cannot delete if season has registries.

---

## 🚜 Farm Types Endpoints

Manage farm type classifications.

### POST `/farmtypes/`
**Create new farm type**

**Request Body:**
```json
{
  "typename": "Mixed Farming",
  "description": "Combination of crop and livestock farming"
}
```

---

### GET `/farmtypes/`
**Get all farm types (paginated)**

---

### GET `/farmtypes/with-counts`
**Get farm types with farm counts**

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "farmtypeid": 1,
      "typename": "Mixed Farming",
      "description": "Combination of crop and livestock farming",
      "farm_count": 120
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/farmtypes/{farmtype_id}/stats`
**Get farm type with statistics**

---

### GET `/farmtypes/search`
**Search farm types by name or description**

**Query Parameters:**
- `q`: Search query

---

### PUT `/farmtypes/{farmtype_id}`
**Update farm type**

---

### DELETE `/farmtypes/{farmtype_id}`
**Delete farm type (soft delete)**

**Note:** Cannot delete if farm type has farms.

---

## 👨‍🌾 Farmers Endpoints

Manage farmer registrations and profiles.

### POST `/farmers/`
**Register new farmer**

**Request Body:**
```json
{
  "firstname": "John",
  "middlename": "Ade",
  "lastname": "Farmer",
  "gender": "Male",
  "dateofbirth": "1985-05-15",
  "email": "john.farmer@example.com",
  "phonenumber": "08012345678",
  "associationid": 1,
  "householdsize": 5,
  "availablelabor": 3,
  "photourl": "https://example.com/photo.jpg",
  "address": {
    "streetaddress": "123 Farm Road",
    "town": "Ibadan",
    "postalcode": "200001",
    "lgaid": 1,
    "latitude": 7.3775,
    "longitude": 3.9470
  }
}
```

**Validation:**
- Age must be 18+
- Phone: 11 digits, starts with 0
- Email must be unique
- Phone must be unique
- Available labor ≤ household size
- LGA must exist

**Response:**
```json
{
  "success": true,
  "message": "Farmer created successfully",
  "data": {
    "farmerid": 1,
    "firstname": "John",
    "middlename": "Ade",
    "lastname": "Farmer",
    "fullname": "John Ade Farmer",
    "gender": "Male",
    "dateofbirth": "1985-05-15",
    "age": 40,
    "email": "john.farmer@example.com",
    "phonenumber": "08012345678",
    "associationid": 1,
    "association_name": "Oyo State Farmers Association",
    "householdsize": 5,
    "availablelabor": 3,
    "address": {
      "addressid": 1,
      "streetaddress": "123 Farm Road",
      "town": "Ibadan",
      "lgaid": 1,
      "lganame": "Ibadan North",
      "latitude": 7.3775,
      "longitude": 3.9470
    },
    "farm_count": 0,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/farmers/`
**Get all farmers (paginated)**

**Query Parameters:**
- `skip`: Pagination offset
- `limit`: Results limit
- `association_id`: Filter by association (optional)
- `lga_id`: Filter by LGA (optional)
- `user_id`: Filter by extension officer (optional)

**Example:** `GET /farmers/?lga_id=1&limit=50`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "farmerid": 1,
      "firstname": "John",
      "lastname": "Farmer",
      "fullname": "John Ade Farmer",
      "gender": "Male",
      "age": 40,
      "phonenumber": "08012345678",
      "association_name": "Oyo State Farmers Association",
      "lga": "Ibadan North",
      "farm_count": 2,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/farmers/statistics`
**Get farmer statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "total_farmers": 1500,
    "male_farmers": 900,
    "female_farmers": 600,
    "farmers_with_farms": 1200,
    "farmers_without_farms": 300
  },
  "tag": 1
}
```

---

### GET `/farmers/{farmer_id}`
**Get farmer by ID with full details**

**Response:**
```json
{
  "success": true,
  "data": {
    "farmerid": 1,
    "firstname": "John",
    "lastname": "Farmer",
    "fullname": "John Ade Farmer",
    "gender": "Male",
    "age": 40,
    "email": "john.farmer@example.com",
    "phonenumber": "08012345678",
    "associationid": 1,
    "association_name": "Oyo State Farmers Association",
    "householdsize": 5,
    "availablelabor": 3,
    "address": {
      "addressid": 1,
      "streetaddress": "123 Farm Road",
      "town": "Ibadan",
      "lgaid": 1,
      "lganame": "Ibadan North",
      "latitude": 7.3775,
      "longitude": 3.9470
    },
    "farm_count": 2,
    "crop_registry_count": 5,
    "livestock_registry_count": 3,
    "agroallied_registry_count": 1,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/farmers/search`
**Search farmers**

**Query Parameters:**
- `q`: Search query (searches name, phone, email)
- `association_id`: Filter by association (optional)
- `lga_id`: Filter by LGA (optional)

**Example:** `GET /farmers/search?q=John&lga_id=1`

---

### PUT `/farmers/{farmer_id}`
**Update farmer**

**Request Body:**
```json
{
  "householdsize": 6,
  "availablelabor": 4,
  "address": {
    "streetaddress": "456 New Road",
    "lgaid": 1
  }
}
```

**Note:** All fields are optional. Can update address separately.

---

### DELETE `/farmers/{farmer_id}`
**Delete farmer (soft delete)**

**Note:** Cannot delete if farmer has registered farms.

---

## 🌱 Farms Endpoints

Manage farm registrations and locations.

### POST `/farms/create`
**Register new farm**

**Request Body:**
```json
{
  "farmerid": 1,
  "farmtypeid": 1,
  "farmsize": 5.5,
  "address": {
    "streetaddress": "Farm Location Road",
    "town": "Ibadan",
    "postalcode": "200001",
    "lgaid": 1,
    "latitude": 7.3800,
    "longitude": 3.9500
  }
}
```

**Validation:**
- Farmer must exist
- Farm type must exist
- LGA must exist
- Farm size: 0-100,000 hectares
- Farm size rounded to 2 decimal places

**Response:**
```json
{
  "success": true,
  "message": "Farm created successfully",
  "data": {
    "farmid": 1,
    "farmerid": 1,
    "farmer_name": "John Farmer",
    "farmtypeid": 1,
    "farmtype_name": "Mixed Farming",
    "farmsize": 5.50,
    "address": {
      "addressid": 2,
      "streetaddress": "Farm Location Road",
      "town": "Ibadan",
      "lgaid": 1,
      "lganame": "Ibadan North",
      "latitude": 7.3800,
      "longitude": 3.9500
    },
    "crop_registry_count": 0,
    "livestock_registry_count": 0,
    "agroallied_registry_count": 0,
    "total_registries": 0,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/farms/`
**Get all farms (paginated)**

**Query Parameters:**
- `skip`: Pagination offset
- `limit`: Results limit
- `farmer_id`: Filter by farmer (optional)
- `farmtype_id`: Filter by farm type (optional)
- `lga_id`: Filter by LGA (optional)

**Example:** `GET /farms/?farmer_id=1&lga_id=1`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "farmid": 1,
      "farmerid": 1,
      "farmer_name": "John Farmer",
      "farmtypeid": 1,
      "farmtype_name": "Mixed Farming",
      "farmsize": 5.50,
      "lga": "Ibadan North",
      "registry_count": 8,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/farms/statistics`
**Get farm statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "total_farms": 1800,
    "total_farmsize_hectares": 5420.50,
    "average_farmsize_hectares": 3.01,
    "farms_by_type": [
      {
        "type": "Mixed Farming",
        "count": 800
      },
      {
        "type": "Crop Farming",
        "count": 600
      },
      {
        "type": "Livestock Farming",
        "count": 400
      }
    ],
    "farms_with_registries": 1200
  },
  "tag": 1
}
```

---

### GET `/farms/by-farmer/{farmer_id}`
**Get all farms for a specific farmer**

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "farmid": 1,
      "farmtypeid": 1,
      "farmtype_name": "Mixed Farming",
      "farmsize": 5.50,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/farms/{farm_id}`
**Get farm by ID with full details**

**Response:**
```json
{
  "success": true,
  "data": {
    "farmid": 1,
    "farmerid": 1,
    "farmer_name": "John Farmer",
    "farmtypeid": 1,
    "farmtype_name": "Mixed Farming",
    "farmsize": 5.50,
    "address": {
      "addressid": 2,
      "streetaddress": "Farm Location Road",
      "town": "Ibadan",
      "lgaid": 1,
      "lganame": "Ibadan North",
      "latitude": 7.3800,
      "longitude": 3.9500
    },
    "crop_registry_count": 3,
    "livestock_registry_count": 2,
    "agroallied_registry_count": 1,
    "total_registries": 6,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### PUT `/farms/{farm_id}`
**Update farm**

**Request Body:**
```json
{
  "farmsize": 7.5,
  "farmtypeid": 2,
  "address": {
    "streetaddress": "Updated Location",
    "lgaid": 1
  }
}
```

**Note:** All fields are optional.

---

### DELETE `/farms/{farm_id}`
**Delete farm (soft delete)**

**Note:** Cannot delete if farm has crop, livestock, or agro-allied registries.

---

## 🌾 Crops Endpoints (Reference Data)

Manage crop type classifications.

### POST `/crops/`
**Create new crop type**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Maize"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Crop created successfully",
  "data": {
    "croptypeid": 1,
    "name": "Maize",
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/crops/`
**Get all crops (paginated)**

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip`: Pagination offset
- `limit`: Results limit

---

### GET `/crops/with-counts`
**Get crops with registry counts**

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "croptypeid": 1,
      "name": "Maize",
      "registry_count": 450,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/crops/{crop_id}/stats`
**Get crop with statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "croptypeid": 1,
    "name": "Maize",
    "registry_count": 450,
    "total_area_planted": 2250.5,
    "total_yield": 56250.0,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/crops/search`
**Search crops by name**

**Query Parameters:**
- `q`: Search query (min 2 characters)

---

### PUT `/crops/{crop_id}`
**Update crop**

---

### DELETE `/crops/{crop_id}`
**Delete crop (soft delete)**

**Note:** Cannot delete if crop has registries.

---

## 🐄 Livestock Endpoints (Reference Data)

Manage livestock type classifications.

### POST `/livestock/`
**Create new livestock type**

**Request Body:**
```json
{
  "name": "Poultry (Chicken)"
}
```

---

### GET `/livestock/`
**Get all livestock types (paginated)**

---

### GET `/livestock/with-counts`
**Get livestock types with registry counts**

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "livestocktypeid": 1,
      "name": "Poultry (Chicken)",
      "registry_count": 200,
      "createdat": "2026-01-24T10:00:00"
    }
  ],
  "total": 1,
  "tag": 1
}
```

---

### GET `/livestock/{livestock_id}/stats`
**Get livestock type with statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "livestocktypeid": 1,
    "name": "Poultry (Chicken)",
    "registry_count": 200,
    "total_quantity": 10000,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/livestock/search`
**Search livestock types**

---

### PUT `/livestock/{livestock_id}`
**Update livestock type**

---

### DELETE `/livestock/{livestock_id}`
**Delete livestock type (soft delete)**

**Note:** Cannot delete if livestock type has registries.

---

## 🏭 Business Types Endpoints (Reference Data)

Manage agro-allied business type classifications.

### POST `/businesstypes/`
**Create new business type**

**Request Body:**
```json
{
  "name": "Processing"
}
```

---

### GET `/businesstypes/`
**Get all business types (paginated)**

---

### GET `/businesstypes/with-counts`
**Get business types with registry counts**

---

### GET `/businesstypes/search`
**Search business types**

---

### PUT `/businesstypes/{businesstype_id}`
**Update business type**

---

### DELETE `/businesstypes/{businesstype_id}`
**Delete business type (soft delete)**

---

## 📦 Primary Products Endpoints (Reference Data)

Manage primary product classifications for agro-allied businesses.

### POST `/primaryproducts/`
**Create new primary product**

**Request Body:**
```json
{
  "name": "Cassava Flour"
}
```

---

### GET `/primaryproducts/`
**Get all primary products (paginated)**

---

### GET `/primaryproducts/with-counts`
**Get primary products with registry counts**

---

### GET `/primaryproducts/search`
**Search primary products**

---

### PUT `/primaryproducts/{product_id}`
**Update primary product**

---

### DELETE `/primaryproducts/{product_id}`
**Delete primary product (soft delete)**

---

## 📊 Crop Registry Endpoints (Data Collection)

Track crop planting, harvesting, and yield data.

### POST `/cropregistry/`
**Register crop data**

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "farmid": 1,
  "seasonid": 1,
  "croptypeid": 1,
  "cropvariety": "Oba Super 2",
  "areaplanted": 5.5,
  "plantedquantity": 25.0,
  "plantingdate": "2025-04-15",
  "harvestdate": "2025-08-20",
  "areaharvested": 5.0,
  "yieldquantity": 2500.0
}
```

**Validation:**
- Farm, season, and crop must exist
- Harvest date must be after planting date
- Area harvested ≤ area planted
- Dates must be within season range
- Farm size: 0-100,000 hectares

**Response:**
```json
{
  "success": true,
  "message": "Crop registry created successfully",
  "data": {
    "cropregistryid": 1,
    "farmid": 1,
    "farmer_name": "John Farmer",
    "crop_name": "Maize",
    "cropvariety": "Oba Super 2",
    "season_name": "2025 Wet Season",
    "areaplanted": 5.50,
    "yieldquantity": 2500.00,
    "status": "Harvested",
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/cropregistry/`
**Get all crop registries (paginated)**

**Query Parameters:**
- `farm_id`: Filter by farm
- `season_id`: Filter by season
- `crop_id`: Filter by crop type
- `farmer_id`: Filter by farmer
- `skip`: Pagination offset
- `limit`: Results limit

**Example:** `GET /cropregistry/?season_id=1&crop_id=1`

---

### GET `/cropregistry/statistics`
**Get crop registry statistics**

**Query Parameters:**
- `season_id`: Filter by season (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_registries": 450,
    "total_area_planted": 2250.50,
    "total_area_harvested": 2100.00,
    "total_yield": 52500.00,
    "avg_yield_per_hectare": 25.00,
    "status_breakdown": {
      "pending": 50,
      "planted": 200,
      "harvested": 200
    }
  },
  "tag": 1
}
```

---

### GET `/cropregistry/{registry_id}`
**Get crop registry by ID with full details**

---

### PUT `/cropregistry/{registry_id}`
**Update crop registry**

---

### DELETE `/cropregistry/{registry_id}`
**Delete crop registry (soft delete)**

---

## 🐓 Livestock Registry Endpoints (Data Collection)

Track livestock quantities over time.

### POST `/livestockregistry/`
**Register livestock data**

**Request Body:**
```json
{
  "farmid": 1,
  "seasonid": 1,
  "livestocktypeid": 1,
  "quantity": 50,
  "startdate": "2025-04-01",
  "enddate": "2025-10-31"
}
```

**Validation:**
- Farm, season, and livestock type must exist
- End date must be after start date
- Dates must be within season range
- Quantity must be > 0

**Response:**
```json
{
  "success": true,
  "message": "Livestock registry created successfully",
  "data": {
    "livestockregistryid": 1,
    "farmid": 1,
    "farmer_name": "John Farmer",
    "livestock_name": "Poultry (Chicken)",
    "season_name": "2025 Wet Season",
    "quantity": 50,
    "startdate": "2025-04-01",
    "enddate": "2025-10-31",
    "status": "Active",
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/livestockregistry/`
**Get all livestock registries (paginated)**

**Query Parameters:**
- `farm_id`: Filter by farm
- `season_id`: Filter by season
- `livestock_id`: Filter by livestock type
- `farmer_id`: Filter by farmer

---

### GET `/livestockregistry/statistics`
**Get livestock registry statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "total_registries": 200,
    "total_quantity": 10000,
    "avg_quantity_per_registry": 50.00,
    "status_breakdown": {
      "active": 150,
      "completed": 50
    },
    "by_livestock_type": {
      "Poultry (Chicken)": {
        "count": 100,
        "total_quantity": 5000
      },
      "Cattle": {
        "count": 50,
        "total_quantity": 2500
      },
      "Goats": {
        "count": 50,
        "total_quantity": 2500
      }
    }
  },
  "tag": 1
}
```

---

### GET `/livestockregistry/{registry_id}`
**Get livestock registry by ID with full details**

---

### PUT `/livestockregistry/{registry_id}`
**Update livestock registry**

---

### DELETE `/livestockregistry/{registry_id}`
**Delete livestock registry (soft delete)**

---

## 🏢 Agro-Allied Registry Endpoints (Data Collection)

Track agro-allied business operations.

### POST `/agroalliedregistry/`
**Register agro-allied business data**

**Request Body:**
```json
{
  "farmid": 1,
  "seasonid": 1,
  "businesstypeid": 1,
  "primaryproducttypeid": 1,
  "productioncapacity": 1000.0
}
```

**Validation:**
- Farm, season, business type, and primary product must exist
- Production capacity must be > 0

**Response:**
```json
{
  "success": true,
  "message": "Agro-allied registry created successfully",
  "data": {
    "agroalliedregistryid": 1,
    "farmid": 1,
    "farmer_name": "John Farmer",
    "season_name": "2025 Wet Season",
    "business_type_name": "Processing",
    "primary_product_name": "Cassava Flour",
    "productioncapacity": 1000.00,
    "createdat": "2026-01-24T10:00:00"
  },
  "tag": 1
}
```

---

### GET `/agroalliedregistry/`
**Get all agro-allied registries (paginated)**

**Query Parameters:**
- `farm_id`: Filter by farm
- `season_id`: Filter by season
- `businesstype_id`: Filter by business type
- `product_id`: Filter by primary product
- `farmer_id`: Filter by farmer

---

### GET `/agroalliedregistry/statistics`
**Get agro-allied registry statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "total_registries": 50,
    "total_production_capacity": 50000.00,
    "avg_capacity_per_registry": 1000.00,
    "by_business_type": {
      "Processing": {
        "count": 25,
        "total_capacity": 25000.00
      },
      "Storage": {
        "count": 15,
        "total_capacity": 15000.00
      },
      "Marketing": {
        "count": 10,
        "total_capacity": 10000.00
      }
    },
    "by_primary_product": {
      "Cassava Flour": {
        "count": 20,
        "total_capacity": 20000.00
      },
      "Palm Oil": {
        "count": 20,
        "total_capacity": 20000.00
      },
      "Maize Flour": {
        "count": 10,
        "total_capacity": 10000.00
      }
    }
  },
  "tag": 1
}
```

---

### GET `/agroalliedregistry/{registry_id}`
**Get agro-allied registry by ID with full details**

---

### PUT `/agroalliedregistry/{registry_id}`
**Update agro-allied registry**

---

### DELETE `/agroalliedregistry/{registry_id}`
**Delete agro-allied registry (soft delete)**

---

## 🔒 Authentication & Authorization

### Authentication Flow

1. **Register or Login** to get JWT token
2. **Include token** in all subsequent requests
3. **Token expires** after configured time (default: 30 minutes)
4. **Refresh** by logging in again

### Authorization Header Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Role-Based Access

| Role | ID | Permissions |
|------|-----|-------------|
| Admin | 1 | Full access to all endpoints and data |
| Extension Officer | 2 | Access to own LGA data, can register farmers/farms |

### Access Control Examples

**Admin:**
- Can view all farmers across all LGAs
- Can manage all reference data
- Can create/update/delete any record

**Extension Officer:**
- Can only view farmers in assigned LGA
- Can register farmers/farms in assigned LGA
- Cannot access other LGAs' data

---

## 📊 Response Format

### Success Response

```json
{
  "success": true,
  "data": { /* payload */ },
  "message": "Operation successful",
  "total": 0,
  "tag": 1
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (Pydantic validation) |
| 500 | Internal Server Error |

---

## ⚠️ Error Handling

### Common Error Scenarios

**1. Validation Errors (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "phonenumber"],
      "msg": "Phone number must be 11 digits starting with 0",
      "type": "value_error"
    }
  ]
}
```

**2. Not Found (404)**
```json
{
  "detail": "Farmer with ID 999 not found"
}
```

**3. Duplicate Entry (400)**
```json
{
  "detail": "Farmer with phone number 08012345678 already exists"
}
```

**4. Authorization Error (401)**
```json
{
  "detail": "Could not validate credentials"
}
```

**5. Business Logic Error (400)**
```json
{
  "detail": "Cannot delete farm with registered crops"
}
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=src --cov-report=html
```

Coverage report will be in `htmlcov/index.html`

### Run Specific Module Tests

```bash
pytest tests/test_farmers.py -v
pytest tests/test_farms.py -v
```

### Test Markers

```bash
# Run only authentication tests
pytest tests/ -m auth

# Run only integration tests
pytest tests/ -m integration
```

---

## 💻 Development

### Project Structure

```
oyoagro-api/
├── main.py                 # Application entry point
├── src/
│   ├── auth/              # Authentication module
│   ├── associations/      # Associations module
│   ├── regions/           # Regions module
│   ├── lgas/              # LGAs module
│   ├── seasons/           # Seasons module
│   ├── farmtypes/         # Farm Types module
│   ├── farmers/           # Farmers module
│   ├── farms/             # Farms module
│   ├── core/              # Core utilities
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   ├── dependencies.py # Auth dependencies
│   │   └── security.py    # Security utilities
│   └── shared/
│       ├── models.py      # Database models
│       └── schemas.py     # Shared schemas
├── tests/                 # Test suite
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
└── README.md             # This file
```

### Module Pattern

Each module follows this structure:
```
module_name/
├── __init__.py           # Exports router
├── schemas.py            # Pydantic models
├── services.py           # Business logic
└── router.py             # API endpoints
```

### Adding New Modules

1. Create module directory in `src/`
2. Implement schemas, services, router
3. Register router in `main.py`
4. Create tests in `tests/`
5. Update this README

---

## 📝 API Best Practices

### 1. Always Use Pagination

```python
GET /farmers/?skip=0&limit=100
```

### 2. Use Filters to Reduce Data

```python
GET /farmers/?lga_id=1&association_id=2
```

### 3. Use Search for Text Queries

```python
GET /farmers/search?q=John
```

### 4. Use Statistics Endpoints for Dashboards

```python
GET /farmers/statistics
GET /farms/statistics
GET /seasons/{id}/stats
```

### 5. Handle Errors Gracefully

Always check `success` field and handle errors appropriately.

### 6. Validate Input on Client Side

Use the same validation rules as the API to provide better UX.

### 7. Cache Reference Data

Regions, LGAs, Farm Types rarely change - cache them client-side.

---

## 🔗 Useful Links

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📞 Support

For issues or questions:
- Check the Swagger documentation at `/docs`
- Review error messages carefully
- Check validation rules in schemas
- Ensure proper authentication headers

---

## 📄 License

[Your License Here]

---

## 👥 Contributors

- Oluwafemi Adejumobi

---

**Last Updated:** January 24, 2026  
**API Version:** 1.0.0  
**FastAPI Version:** 0.104+