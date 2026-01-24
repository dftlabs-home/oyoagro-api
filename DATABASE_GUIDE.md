# Database Management Guide

## Overview

The OyoAgro API can work with both **existing databases** and **create new databases** from scratch.

---

## 🎯 Quick Start Options

### Option 1: Use Existing Database (Current System)
If you already have a PostgreSQL database with the schema:

```bash
# Just configure the connection
echo "DATABASE_URL=postgresql://user:password@localhost/oyoagrodb" > .env

# Start the API
uvicorn main:app --reload
```

The API will connect to your existing database and use the existing tables.

---

### Option 2: Create New Database (Automated Setup)

If you want to create a fresh database with all tables:

#### Step 1: Create Empty Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE oyoagrodb;

-- Create user (optional)
CREATE USER oyoagro WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE oyoagrodb TO oyoagro;
```

#### Step 2: Run Initialization Script
```bash
# Configure connection
echo "DATABASE_URL=postgresql://oyoagro:your_password@localhost/oyoagrodb" > .env

# Run initialization
python init_db.py
```

This will:
1. ✅ Create all 25+ database tables
2. ✅ Seed roles (Admin, Extension Officer)
3. ✅ Optionally seed sample data (regions, LGAs, farm types)
4. ✅ Optionally create default admin user

---

## 📋 Database Tables Created

The initialization creates these tables:

### User Management (3 tables)
- `useraccount` - User authentication
- `userprofile` - User profile details
- `passwordresettokens` - Password reset tokens

### Geographic (4 tables)
- `region` - Agricultural zones
- `lga` - Local Government Areas
- `addresses` - Location data for farmers/farms
- `userregion` - User-region assignments

### Farmer & Farm (4 tables)
- `association` - Farmer associations
- `farmer` - Farmer registrations
- `farmtype` - Farm type classifications
- `farm` - Farm registrations

### Data Collection (7 tables)
- `season` - Farming seasons
- `crop` - Crop types
- `cropregistry` - Crop data collection
- `livestock` - Livestock types
- `livestockregistry` - Livestock data
- `BusinessType` - Agro-allied business types
- `PrimaryProduct` - Primary products
- `AgroAlliedRegistry` - Agro-allied data

### System (7 tables)
- `notification` - System notifications
- `notificationtarget` - Notification targets
- `role` - User roles
- `profileactivityparent` - Permission categories
- `profileactivity` - Permissions
- `profileadditionalactivity` - User permissions
- `dashboardmetrics` - Dashboard metrics
- `synclog` - Sync logs for mobile apps

---

## 🔨 Database Management Commands

### Initialize Fresh Database
```bash
python init_db.py
```

### Check Database Connection
```python
from src.core.database import check_database_connection

if check_database_connection():
    print("✅ Database is connected")
```

### Drop All Tables (Reset)
```bash
python reset_db.py
```
**⚠️ WARNING: This deletes all data!**

---

## 🌱 Seeding Data

### Default Admin User
The initialization can create a default admin user:

**Username:** `admin`  
**Password:** `Admin@123`  
**Email:** `admin@oyoagro.gov.ng`

⚠️ **Important:** Change this password immediately in production!

### Sample Reference Data
The script can seed:
- 3 regions (Ibadan, Ogbomoso, Oyo zones)
- 3 LGAs in Ibadan zone
- 3 farm types (Crop, Livestock, Mixed)

---

## 🔄 Migration from Existing Database

If you have data in another system:

### Export from Old System
```bash
# Export data
pg_dump -U postgres -d old_database > backup.sql
```

### Import to New System
```bash
# Create tables first
python init_db.py

# Then import data
psql -U postgres -d oyoagrodb < backup.sql
```

---

## 🛠 Troubleshooting

### Connection Error
```
❌ Database connection failed
```

**Solutions:**
1. Check DATABASE_URL in `.env`
2. Verify PostgreSQL is running
3. Check user permissions
4. Verify database exists

### Table Already Exists
```
⊙ Tables already exist
```

**This is normal** - SQLModel only creates missing tables.

### Permission Denied
```
❌ Permission denied for table
```

**Solution:**
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oyoagro;
```

---

## 📊 Database Schema

### Key Relationships

```
Region (1) ──→ (N) LGA
LGA (1) ──→ (N) Farmer (via Address)
LGA (1) ──→ (N) Farm (via Address)
Farmer (1) ──→ (N) Farm
Farm (1) ──→ (N) CropRegistry
Farm (1) ──→ (N) LivestockRegistry
Farm (1) ──→ (N) AgroAlliedRegistry
Season (1) ──→ (N) CropRegistry
Season (1) ──→ (N) LivestockRegistry
Association (1) ──→ (N) Farmer
Farmtype (1) ──→ (N) Farm
```

### Soft Deletes

All main tables use soft delete:
- `deletedat` timestamp field
- `NULL` = active record
- `NOT NULL` = deleted record

Queries automatically filter: `WHERE deletedat IS NULL`

### Versioning

Tables with `version` field support optimistic locking:
- Version increments on each update
- Helps prevent concurrent update conflicts

---

## 🔐 Security Best Practices

### 1. Database User
Create dedicated database user:
```sql
CREATE USER oyoagro_app WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE oyoagrodb TO oyoagro_app;
GRANT USAGE ON SCHEMA public TO oyoagro_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO oyoagro_app;
```

### 2. Connection String
Use environment variables:
```env
DATABASE_URL=postgresql://oyoagro_app:password@localhost/oyoagrodb
```

### 3. SSL Connection (Production)
```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

---

## 📈 Performance Tips

### 1. Indexes
Important indexes are created automatically:
- Primary keys
- Foreign keys
- Common query fields

### 2. Connection Pooling
Configured in `database.py`:
```python
pool_size=10
max_overflow=20
```

### 3. Query Optimization
- Use pagination for large datasets
- Filter early in queries
- Use indexes for search fields

---

## 🔄 Backup and Restore

### Backup
```bash
# Full backup
pg_dump -U postgres oyoagrodb > backup_$(date +%Y%m%d).sql

# Schema only
pg_dump -U postgres -s oyoagrodb > schema.sql

# Data only
pg_dump -U postgres -a oyoagrodb > data.sql
```

### Restore
```bash
# Restore full backup
psql -U postgres -d oyoagrodb < backup_20260124.sql

# Restore schema then data
psql -U postgres -d oyoagrodb < schema.sql
psql -U postgres -d oyoagrodb < data.sql
```

---

## 📝 Environment Variables

Required in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/oyoagrodb
DATABASE_ECHO=False  # Set to True for SQL logging

# Security
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=OyoAgro API
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Initialize database | `python init_db.py` |
| Start API | `uvicorn main:app --reload` |
| Check connection | `python -c "from src.core.database import check_database_connection; check_database_connection()"` |
| Run tests | `pytest tests/` |
| Create backup | `pg_dump oyoagrodb > backup.sql` |

---

## 📞 Support

If you encounter issues:
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify connection: `psql -U postgres -d oyoagrodb`
3. Check logs in API console
4. Review error messages carefully