#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

client = Client()

print("=" * 60)
print("Testing Signup & Login Pages")
print("=" * 60)

# Test 1: Signup page GET
print("\n1. Testing GET /register/")
try:
    response = client.get('/register/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   [OK] Signup page loads successfully")
    else:
        print(f"   [FAIL] Error: {response.status_code}")
except Exception as e:
    print(f"   [FAIL] Exception: {e}")

# Test 2: Register new user
print("\n2. Testing POST /register/ (User Registration)")
try:
    response = client.post('/register/', {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123'
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:  # Redirect means success
        print("   [OK] User registered successfully")
    else:
        print(f"   [FAIL] Response: {response.status_code}")
        if response.status_code == 500:
             print(f"   [DEBUG] Content: {response.content.decode()[:500]}")
except Exception as e:
    print(f"   [FAIL] Exception: {e}")

# Test 3: Login page GET
print("\n3. Testing GET /login/")
try:
    response = client.get('/login/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   [OK] Login page loads successfully")
    else:
        print(f"   [FAIL] Error: {response.status_code}")
except Exception as e:
    print(f"   [FAIL] Exception: {e}")

# Test 4: Login with credentials
print("\n4. Testing POST /login/ (User Login)")
try:
    # Create a test user first
    User.objects.filter(username='logintest').delete()
    User.objects.create_user(username='logintest', email='login@example.com', password='pass123')
    
    response = client.post('/login/', {
        'username': 'logintest',
        'password': 'pass123'
    })
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:  # Redirect means success
        print("   [OK] User logged in successfully")
    else:
        print(f"   [FAIL] Response: {response.status_code}")
        if response.status_code == 500:
             print(f"   [DEBUG] Content: {response.content.decode()[:500]}")
except Exception as e:
    print(f"   [FAIL] Exception: {e}")

# Test 5: Dashboard (requires login)
print("\n5. Testing GET /dashboard/ (Protected - No auth)")
try:
    response = client.get('/dashboard/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:  # Should redirect to login
        print("   [OK] Correctly redirects to login (protected page)")
    else:
        print(f"   [FAIL] Status: {response.status_code}")
except Exception as e:
    print(f"   [FAIL] Exception: {e}")

# Test 6: Dashboard with authenticated user
print("\n6. Testing GET /dashboard/ (Protected - With auth)")
try:
    client.login(username='logintest', password='pass123')
    response = client.get('/dashboard/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   [OK] Dashboard loads for authenticated user")
    else:
        print(f"   [FAIL] Error: {response.status_code}")
        if response.status_code == 500:
             print(f"   [DEBUG] Content: {response.content.decode()[:500]}")
except Exception as e:
    print(f"   [FAIL] Exception: {e}")

print("\n" + "=" * 60)
print("Testing Complete")
print("=" * 60)
