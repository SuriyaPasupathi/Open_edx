#!/bin/bash
# Script to clear rate limit cache in Open edX

echo "Clearing rate limit cache..."

cd /home/ubuntu/manaual/edx-platform

# Activate virtual environment (adjust path if needed)
source ../env/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null || echo "Virtual environment not found, using system Python"

# Clear cache using Django shell
python manage.py shell << EOF
from django.core.cache import cache

# Clear all cache (including rate limits)
cache.clear()
print("✅ Rate limit cache cleared!")

# Also clear specific rate limit keys for common IPs
ip_addresses = ["103.186.120.7", "127.0.0.1", "localhost"]
for ip in ip_addresses:
    keys = [
        f"ratelimit:login:{ip}",
        f"ratelimit:register:{ip}",
        f"ratelimit:login_ajax:{ip}",
        f"rl:login:{ip}",
        f"rl:register:{ip}",
    ]
    for key in keys:
        cache.delete(key)
        print(f"Deleted: {key}")

print("✅ All rate limit caches cleared!")
EOF

echo ""
echo "Rate limit cache cleared successfully!"
echo "You can now restart Open edX LMS server."

