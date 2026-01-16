#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')
django.setup()

from django.test import Client
client = Client()

try:
    response = client.get('/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Home page loads successfully")
    else:
        print(f"Error: {response.status_code}")
        print(response.content[:500])
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
