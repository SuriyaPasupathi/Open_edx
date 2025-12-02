#!/bin/bash
# Script to set up OAuth Login Service Application
# This fixes the "OAuth Client for the Login service is not configured" error

set -e

echo "=========================================="
echo "Setting up OAuth Login Service"
echo "=========================================="

# Create login service user if it doesn't exist
echo "Creating login_service_user..."
python manage.py lms manage_user login_service_user login_service_user@fake.email --unusable-password --settings=devstack || echo "User may already exist"

# Create OAuth application for login service
echo "Creating OAuth application for login service..."
python manage.py lms create_dot_application \
    "Login Service for JWT Cookies" \
    login_service_user \
    --grant-type password \
    --public \
    --client-id login-service-client-id \
    --scopes "read,email,profile,user_id" \
    --settings=devstack || echo "OAuth application may already exist"

echo "=========================================="
echo "OAuth Login Service setup complete"
echo "=========================================="

