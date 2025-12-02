# Registration Error Fixes

This document explains the fixes applied to resolve user registration errors in the Docker-based Open edX setup.

## Issues Fixed

### 1. OAuth Application Missing Error
**Error**: `oauth2_provider.models.Application.DoesNotExist: Application matching query does not exist.`

**Root Cause**: The OAuth2 application required for JWT cookie authentication (`login-service-client-id`) was not created during setup.

**Fix**: 
- Added OAuth application creation to `docker-compose.yml` LMS service startup sequence
- Creates `login_service_user` user if it doesn't exist
- Creates OAuth application "Login Service for JWT Cookies" with client_id `login-service-client-id`
- Also created standalone script `setup_oauth_login.sh` for manual setup if needed

### 2. Forum Service Connection Error
**Error**: `socket.gaierror: [Errno -2] Name or service not known` for `edx.devstack.forum:4567`

**Root Cause**: 
- The system was trying to connect to a forum service that doesn't exist in the Docker setup
- Even though `ENABLE_DISCUSSION_SERVICE: false` was set in config, the `COMMENTS_SERVICE_URL` was still pointing to a non-existent service

**Fix**:
- Updated `lms/envs/devstack.py` to set `COMMENTS_SERVICE_URL = ''` when `ENABLE_DISCUSSION_SERVICE` is False
- This prevents connection attempts when the discussion service is disabled

## Files Modified

1. **docker-compose.yml**: Added OAuth setup commands to LMS service startup
2. **lms/envs/devstack.py**: Added conditional `COMMENTS_SERVICE_URL` setting based on `ENABLE_DISCUSSION_SERVICE` feature flag
3. **setup_oauth_login.sh**: Created standalone script for manual OAuth setup

## How to Apply Fixes

### Option 1: Restart Docker Containers (Recommended)
The fixes are automatically applied when you restart the LMS container:

```bash
cd edx-platform
docker-compose restart lms
```

Or rebuild and restart:

```bash
docker-compose down
docker-compose up -d lms
```

### Option 2: Manual Setup (If containers are already running)
If you need to fix an existing running container without restarting:

```bash
# Enter the LMS container
docker exec -it edx_lms bash

# Run the OAuth setup script
python manage.py lms manage_user login_service_user login_service_user@fake.email --unusable-password --settings=devstack
python manage.py lms create_dot_application "Login Service for JWT Cookies" login_service_user --grant-type password --public --client-id login-service-client-id --scopes "read,email,profile,user_id" --settings=devstack
```

## Verification

After applying the fixes, user registration should work without errors. You can verify by:

1. Registering a new user through the web interface
2. Checking LMS logs for successful registration (no OAuth or forum errors)
3. Verifying the user can log in successfully

## Notes

- The forum service error was non-critical (just a warning in logs) but fixing it prevents log noise
- The OAuth application error was critical and prevented successful user registration
- Both fixes are now automated in the Docker startup sequence

