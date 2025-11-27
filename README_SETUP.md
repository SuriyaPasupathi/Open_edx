# Open edX Platform Setup Guide

## 🚀 Complete Setup from Start to End

### Prerequisites
- Python 3.11
- MySQL 8.0
- MongoDB 7.x
- Node.js
- Virtual environment activated

### Step 1: Environment Setup
```bash
# Navigate to the project directory
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"

# Activate virtual environment
source ../env/bin/activate
```

### Step 2: Database Services
Ensure MySQL and MongoDB are running:
```bash
# Check MySQL status
sudo systemctl status mysql

# Check MongoDB status
sudo systemctl status mongod

# Start services if needed
sudo systemctl start mysql
sudo systemctl start mongod
```

### Step 3: Run All Migrations (One Command)
```bash
# Run all migrations at once
./run_migrations.sh
```

**OR** Run migrations individually:
```bash
# Set environment variables
source set_env.sh

# Run LMS migrations
./manage.py lms migrate

# Run LMS student module history migrations
./manage.py lms migrate --database=student_module_history

# Run CMS migrations
./manage.py cms migrate
```

### Step 4: Start Services
```bash
# Start both LMS and CMS services
./start_services.sh
```

**OR** Start services manually:
```bash
# Set environment variables
source set_env.sh

# Start LMS (port 18000)
python manage.py lms runserver 18000 --settings=devstack &

# Start CMS (port 18010)
python manage.py cms runserver 18010 --settings=devstack &
```

### Step 5: Access the Platform
- **LMS (Learning Management System)**: http://localhost:18000
- **CMS (Content Management System/Studio)**: http://localhost:18010

### Step 6: Stop Services
```bash
# Stop all services
pkill -f 'manage.py.*runserver'
```

## 📁 Configuration Files

### Environment Files
- `lms.env.json` - LMS configuration
- `cms.env.json` - CMS configuration

### Scripts
- `run_migrations.sh` - Run all migrations
- `start_services.sh` - Start both services
- `set_env.sh` - Set environment variables

## 🔧 Troubleshooting

### Common Issues
1. **MongoDB auth_source error**: Fixed by removing authSource parameters
2. **Student module history error**: Fixed by adding database configuration
3. **Missing environment variables**: Use `source set_env.sh`

### Quick Fixes
```bash
# If services won't start, check environment variables
source set_env.sh

# If migrations fail, check database connections
sudo systemctl status mysql
sudo systemctl status mongod

# If ports are busy, kill existing processes
pkill -f 'manage.py.*runserver'
```

## ✅ Success Indicators
- All migrations complete without errors
- LMS accessible at http://localhost:18000
- CMS accessible at http://localhost:18010
- No MongoDB authentication errors
- No missing database connection errors

## 🎯 Quick Start (TL;DR)
```bash
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"
source ../env/bin/activate
./run_migrations.sh
./start_services.sh
```

**Access URLs:**
- LMS: http://localhost:18000
- CMS: http://localhost:18010
