#!/usr/bin/env python
"""
Script to create test account, login, and add dummy app records for testing.
"""

import requests
import json
import time

BASE_URL = "http://localhost:7000"

def main():
    print("=" * 60)
    print("Creating Test Data for Fraud App Detection")
    print("=" * 60)
    
    # Step 1: Register a new account
    print("\n1. Registering new account...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password2": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
        if response.status_code == 201:
            print("   [OK] Account created successfully!")
            user_data = response.json()
            print(f"   User ID: {user_data.get('id')}, Username: {user_data.get('username')}")
        elif response.status_code == 400:
            print("   [WARN] Account might already exist, trying to login...")
        else:
            print(f"   [FAIL] Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        print(f"   Make sure the Django server is running on {BASE_URL}")
        return
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token/", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access")
            print("   [OK] Login successful!")
            print(f"   Access token: {access_token[:20]}...")
        else:
            print(f"   [FAIL] Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        print(f"   Make sure the Django server is running on {BASE_URL}")
        return
    
    # Set up headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 3: Create dummy apps
    print("\n3. Creating dummy apps...")
    
    apps_data = [
        {
            "name": "Suspicious Finance App",
            "package_name": "com.suspicious.finance",
            "store_url": "https://play.google.com/store/apps/details?id=com.suspicious.finance",
            "developer": "Unknown Developer",
            "category": "Finance"
        },
        {
            "name": "Legit Weather App",
            "package_name": "com.legit.weather",
            "store_url": "https://play.google.com/store/apps/details?id=com.legit.weather",
            "developer": "Trusted Weather Co.",
            "category": "Weather"
        },
        {
            "name": "Fraudulent Shopping App",
            "package_name": "com.fraud.shopping",
            "store_url": "https://play.google.com/store/apps/details?id=com.fraud.shopping",
            "developer": "Shady Retailer",
            "category": "Shopping"
        }
    ]
    
    created_apps = []
    for app_data in apps_data:
        try:
            response = requests.post(f"{BASE_URL}/api/apps/", json=app_data, headers=headers)
            if response.status_code == 201:
                app = response.json()
                created_apps.append(app)
                print(f"   [OK] Created: {app['name']} (ID: {app['id']})")
            elif response.status_code == 400:
                # Might already exist, try to get it
                print(f"   [WARN] App might exist: {app_data['name']}")
            else:
                print(f"   [FAIL] Failed to create {app_data['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   [ERROR] Error creating {app_data['name']}: {e}")
    
    if not created_apps:
        print("\n   Trying to fetch existing apps...")
        try:
            response = requests.get(f"{BASE_URL}/api/apps/", headers=headers)
            if response.status_code == 200:
                apps_response = response.json()
                created_apps = apps_response if isinstance(apps_response, list) else apps_response.get('results', [])
                print(f"   Found {len(created_apps)} existing app(s)")
        except Exception as e:
            print(f"   [ERROR] Error fetching apps: {e}")
            return
    
    # Step 4: Add reviews to apps
    print("\n4. Adding reviews to apps...")
    
    # Reviews for Suspicious Finance App
    suspicious_reviews = [
        {
            "text": "This app asked for my bank account details immediately after install. Very suspicious!",
            "rating": 1,
            "author": "ConcernedUser1",
            "source": "Google Play"
        },
        {
            "text": "App crashed multiple times and then asked for credit card info. Not safe!",
            "rating": 1,
            "author": "User123",
            "source": "Google Play"
        },
        {
            "text": "Seems like a scam. Uninstalled immediately.",
            "rating": 1,
            "author": "SafetyFirst",
            "source": "Google Play"
        },
        {
            "text": "Great app, works perfectly!",
            "rating": 5,
            "author": "HappyUser",
            "source": "Google Play"
        },
        {
            "text": "Excellent financial management tool.",
            "rating": 5,
            "author": "FinanceGuru",
            "source": "Google Play"
        }
    ]
    
    # Reviews for Legit Weather App
    legit_reviews = [
        {
            "text": "Accurate weather forecasts, clean interface. Highly recommend!",
            "rating": 5,
            "author": "WeatherFan",
            "source": "Google Play"
        },
        {
            "text": "Best weather app I've used. Very reliable.",
            "rating": 5,
            "author": "OutdoorEnthusiast",
            "source": "Google Play"
        },
        {
            "text": "Simple and effective. Does exactly what it says.",
            "rating": 4,
            "author": "SimpleUser",
            "source": "Google Play"
        },
        {
            "text": "Good app, but could use more features.",
            "rating": 4,
            "author": "FeatureSeeker",
            "source": "Google Play"
        },
        {
            "text": "Perfect for daily weather checks.",
            "rating": 5,
            "author": "DailyUser",
            "source": "Google Play"
        }
    ]
    
    # Reviews for Fraudulent Shopping App
    fraud_reviews = [
        {
            "text": "SCAM! Ordered products but never received them. Money stolen!",
            "rating": 1,
            "author": "Victim1",
            "source": "Google Play"
        },
        {
            "text": "Fake reviews everywhere. This is a fraudulent app. Stay away!",
            "rating": 1,
            "author": "WarnedUser",
            "source": "Google Play"
        },
        {
            "text": "Charged my card multiple times without authorization. REPORTED!",
            "rating": 1,
            "author": "AngryCustomer",
            "source": "Google Play"
        },
        {
            "text": "Best shopping app ever! Amazing deals!",
            "rating": 5,
            "author": "SatisfiedBuyer",
            "source": "Google Play"
        },
        {
            "text": "Love this app! Great prices!",
            "rating": 5,
            "author": "HappyShopper",
            "source": "Google Play"
        }
    ]
    
    review_sets = [
        (created_apps[0] if len(created_apps) > 0 else None, suspicious_reviews, "Suspicious Finance App"),
        (created_apps[1] if len(created_apps) > 1 else None, legit_reviews, "Legit Weather App"),
        (created_apps[2] if len(created_apps) > 2 else None, fraud_reviews, "Fraudulent Shopping App"),
    ]
    
    for app, reviews, app_name in review_sets:
        if not app:
            print(f"   [WARN] Skipping {app_name} - app not found")
            continue
        
        try:
            bulk_data = {
                "app_id": app["id"],
                "reviews": reviews
            }
            response = requests.post(f"{BASE_URL}/api/reviews/bulk/", json=bulk_data, headers=headers)
            if response.status_code == 201:
                result = response.json()
                count = result.get("created_count", len(reviews))
                print(f"   [OK] Added {count} reviews to {app_name} (App ID: {app['id']})")
            else:
                print(f"   [FAIL] Failed to add reviews to {app_name}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   [ERROR] Error adding reviews to {app_name}: {e}")
    
    print("\n" + "=" * 60)
    print("Test Data Creation Complete!")
    print("=" * 60)
    print(f"\nLogin credentials:")
    print(f"  Username: testuser")
    print(f"  Password: testpass123")
    print(f"\nCreated {len(created_apps)} app(s) with reviews.")
    print(f"\nYou can now:")
    print(f"  1. Login at http://localhost:8000/login/")
    print(f"  2. View apps at http://localhost:8000/dashboard/")
    print(f"  3. Run analysis on any app at http://localhost:8000/apps/<app_id>/")
    print("=" * 60)

if __name__ == "__main__":
    main()

