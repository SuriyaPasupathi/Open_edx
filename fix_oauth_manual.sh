#!/bin/bash
# Manual fix for OAuth Login Service
# Run this inside the LMS container or with proper Django settings

# Make sure you're in the right directory and have the right settings
cd /app || cd /edx/app/edxapp/edx-platform || pwd

# Create the user first
python manage.py lms manage_user login_service_user login_service_user@fake.email --unusable-password --settings=devstack

# Create the OAuth application - using single quotes and ensuring proper spacing
python manage.py lms create_dot_application \
    'Login Service for JWT Cookies' \
    login_service_user \
    --grant-type password \
    --public \
    --client-id login-service-client-id \
    --scopes 'read,email,profile,user_id' \
    --settings=devstack

echo "OAuth Login Service setup complete!"

