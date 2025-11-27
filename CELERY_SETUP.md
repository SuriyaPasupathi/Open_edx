# Open edX Celery Setup Guide

This guide provides step-by-step instructions for setting up and running Celery workers for your Open edX platform.

## 🎯 Overview

Celery is used in Open edX for handling background tasks such as:
- User registration processing
- Email notifications
- Certificate generation
- Grade calculations
- Content processing
- And many more...

## 📋 Prerequisites

- Virtual environment activated
- Open edX platform properly configured
- Environment variables set up

## 🚀 Quick Start

### 1. Navigate to the Project Directory
```bash
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"
```

### 2. Activate Virtual Environment
```bash
source /home/suriya-vcw/Desktop/suriya\ work/env/bin/activate
```

### 3. Set Environment Variables
```bash
source set_env.sh
```

### 4. Start Celery Workers

#### Start LMS Celery Worker
```bash
celery -A lms worker --loglevel=info --concurrency=2
```

#### Start CMS Celery Worker (in a new terminal)
```bash
celery -A cms worker --loglevel=info --concurrency=2
```

#### Start Celery Beat Scheduler (in a new terminal)
```bash
celery -A lms beat --loglevel=info
```

## 🔧 Configuration Details

### Environment Files
- **LMS Configuration**: `lms.env.yml`
- **CMS Configuration**: `cms.env.yml`

### Celery Settings
```yaml
# Celery configuration for development
CELERY_ALWAYS_EAGER: true
BROKER_URL: "memory://"
CELERY_BROKER_TRANSPORT: "memory"
CELERY_BROKER_HOSTNAME: "localhost"
CELERY_RESULT_BACKEND: "cache+memory://"
CELERY_TASK_ALWAYS_EAGER: true
CELERY_EAGER_PROPAGATES_EXCEPTIONS: true
```

### Transport Configuration
- **Broker**: `memory://localhost//` (for development)
- **Result Backend**: `memory:///`
- **Concurrency**: 2 workers per service

## 📊 Available Tasks

### LMS Tasks (100+ tasks)
- User authentication tasks
- Certificate generation
- Grade calculations
- Email notifications
- Content processing
- Discussion tasks
- And more...

### CMS Tasks (80+ tasks)
- Content management
- Course publishing
- Library operations
- Search indexing
- Export/import operations
- And more...

## 🖥️ Running in Background

### Using `&` (Background Process)
```bash
# Start LMS worker in background
celery -A lms worker --loglevel=info --concurrency=2 &

# Start CMS worker in background
celery -A cms worker --loglevel=info --concurrency=2 &

# Start Beat scheduler in background
celery -A lms beat --loglevel=info &
```

### Using `screen` or `tmux` (Recommended)
```bash
# Create a new screen session
screen -S celery-lms
celery -A lms worker --loglevel=info --concurrency=2
# Press Ctrl+A, then D to detach

# Create another screen session for CMS
screen -S celery-cms
celery -A cms worker --loglevel=info --concurrency=2
# Press Ctrl+A, then D to detach

# Create screen session for Beat
screen -S celery-beat
celery -A lms beat --loglevel=info
# Press Ctrl+A, then D to detach
```

## 🔍 Monitoring Celery

### Check Running Processes
```bash
ps aux | grep celery
```

### View Celery Logs
```bash
# If running in screen sessions
screen -r celery-lms
screen -r celery-cms
screen -r celery-beat
```

### Celery Flower (Web-based Monitoring)
```bash
celery -A lms flower --port=5555
```
Access at: http://localhost:5555

## 🛠️ Troubleshooting

### Common Issues

#### 1. "No such transport" Error
**Problem**: `KeyError: 'No such transport: '`
**Solution**: Ensure `CELERY_BROKER_TRANSPORT` is set in your environment files:
```yaml
CELERY_BROKER_TRANSPORT: "memory"
```

#### 2. "set_env.sh: No such file or directory"
**Problem**: Running commands from wrong directory
**Solution**: Make sure you're in the `edx-platform` directory:
```bash
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"
```

#### 3. Workers Not Starting
**Problem**: Environment variables not set
**Solution**: Always run `source set_env.sh` before starting Celery

### Verification Steps

1. **Check Environment Variables**:
   ```bash
   echo $LMS_CFG
   echo $CMS_CFG
   ```

2. **Verify Celery Configuration**:
   ```bash
   celery -A lms inspect stats
   ```

3. **Test Task Execution**:
   ```bash
   celery -A lms inspect active
   ```

## 📝 Service Management

### Start All Services
```bash
# Terminal 1: LMS Worker
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"
source /home/suriya-vcw/Desktop/suriya\ work/env/bin/activate
source set_env.sh
celery -A lms worker --loglevel=info --concurrency=2

# Terminal 2: CMS Worker
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"
source /home/suriya-vcw/Desktop/suriya\ work/env/bin/activate
source set_env.sh
celery -A cms worker --loglevel=info --concurrency=2

# Terminal 3: Beat Scheduler
cd "/home/suriya-vcw/Desktop/suriya work/edx-platform"
source /home/suriya-vcw/Desktop/suriya\ work/env/bin/activate
source set_env.sh
celery -A lms beat --loglevel=info
```

### Stop All Celery Processes
```bash
pkill -f 'celery.*worker'
pkill -f 'celery.*beat'
pkill -f 'celery.*flower'
```

## 🎯 Expected Output

When Celery starts successfully, you should see:

```
celery@suriya-vcw-Precision-5520 v5.5.3 (immunity)
--- ***** ----- 
-- ******* ---- Linux-6.14.0-27-generic-x86_64-with-glibc2.39
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         proj:0x...
- ** ---------- .> transport:   memory://localhost//
- ** ---------- .> results:     memory:///
- *** --- * --- .> concurrency: 2 (prefork)
-- ******* ---- .> task events: ON
--- ***** ----- 
 -------------- [queues]
                .> edx.lms.core.default exchange=edx.lms.core(direct) key=edx.lms.core.default
                .> edx.lms.core.high exchange=edx.lms.core(direct) key=edx.lms.core.high
                .> edx.lms.core.high_mem exchange=edx.lms.core(direct) key=edx.lms.core.high_mem

[tasks]
  . openedx.core.djangoapps.user_authn.tasks.check_pwned_password_and_send_track_event
  . lms.djangoapps.certificates.tasks.generate_certificate
  . lms.djangoapps.grades.tasks.compute_grades_for_course
  ... (100+ tasks)

[2025-09-15 16:03:12,444: INFO/MainProcess] Connected to memory://localhost//
[2025-09-15 16:03:12,475: INFO/MainProcess] celery@suriya-vcw-Precision-5520 ready.
```

## ✅ Success Indicators

- ✅ Workers show "ready" status
- ✅ Connected to memory broker
- ✅ Tasks are discovered and listed
- ✅ No error messages in logs
- ✅ User registration works without Celery errors

## 🔄 Next Steps

After Celery is running:
1. Start your Open edX LMS server
2. Start your Open edX CMS server
3. Test user registration to verify the original bug is fixed
4. Monitor Celery logs for any issues

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all environment variables are set
3. Ensure you're running commands from the correct directory
4. Check Celery logs for specific error messages

---

**Note**: This setup is configured for development. For production, consider using Redis or RabbitMQ as the broker instead of memory transport.
