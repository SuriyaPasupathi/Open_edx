# Quick Fix for OAuth Application Error

## If you're running the command manually:

Run these commands **inside the LMS container** or with proper Django environment:

```bash
# Step 1: Create the user
python manage.py lms manage_user login_service_user login_service_user@fake.email --unusable-password --settings=devstack

# Step 2: Create the OAuth application (ALL ON ONE LINE - copy the entire line)
python manage.py lms create_dot_application 'Login Service for JWT Cookies' login_service_user --grant-type password --public --client-id login-service-client-id --scopes 'read,email,profile,user_id' --settings=devstack
```

## Important Notes:

1. **Make sure you're using `python manage.py lms`** (not just `python manage.py`)
2. **The command must be on a single line** - don't split it across multiple lines unless you use backslashes properly
3. **Use single quotes** around the application name and scopes
4. **Make sure you're in the correct directory** (usually `/app` in Docker containers)

## If you're inside a Docker container:

```bash
# Enter the container
docker exec -it edx_lms bash

# Then run the commands above
```

## Alternative: Use the script

You can also use the provided script:

```bash
docker exec -it edx_lms bash -c "/app/setup_oauth_login.sh"
```

Or if the script is in your current directory:

```bash
docker cp setup_oauth_login.sh edx_lms:/tmp/
docker exec -it edx_lms bash /tmp/setup_oauth_login.sh
```

