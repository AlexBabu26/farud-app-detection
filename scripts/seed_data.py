#!/usr/bin/env python3
"""
Comprehensive data seeding script for Fraud App Detection.
Creates users, apps, reviews, watchlist items, and community reports via API.
Usage: python scripts/seed_data.py
"""
import requests
import sys
import time
import random

BASE_URL = "http://127.0.0.1:8000"

def print_header(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

def print_step(msg):
    print(f"\n-> {msg}")

def create_user(username, email, password):
    url = f"{BASE_URL}/api/auth/register/"
    data = {"username": username, "email": email, "password": password, "password2": password}
    try:
        r = requests.post(url, json=data, timeout=5)
        if r.status_code == 201:
            print(f"   [OK] Created user: {username}")
            return True
        elif r.status_code == 400 and "already exists" in r.text:
            print(f"   [SKIP] User {username} already exists")
            return True
        else:
            print(f"   [FAIL] Could not create user {username}: {r.status_code} {r.text}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def get_token(username, password):
    url = f"{BASE_URL}/api/auth/token/"
    data = {"username": username, "password": password}
    try:
        r = requests.post(url, json=data, timeout=5)
        if r.status_code == 200:
            return r.json().get("access")
        print(f"   [FAIL] Login failed for {username}: {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] Login error: {e}")
    return None

def create_app(token, app_data):
    headers = {"Authorization": f"Bearer {token}"}
    # Check if exists first (by package_name)
    # Since we don't have a direct search by package_name in standard viewset list without filter,
    # we'll just try create and handle 400.
    try:
        r = requests.post(f"{BASE_URL}/api/apps/", json=app_data, headers=headers, timeout=5)
        if r.status_code == 201:
            print(f"   [OK] Created app: {app_data['name']}")
            return r.json()
        elif r.status_code == 400 and "package_name" in r.text:
            print(f"   [SKIP] App {app_data['name']} already exists")
            # Fetch it to return ID
            r2 = requests.get(f"{BASE_URL}/api/apps/", headers=headers, timeout=5)
            if r2.status_code == 200:
                for a in r2.json().get('results', []):
                    if a['package_name'] == app_data['package_name']:
                        return a
        else:
            print(f"   [FAIL] Create app {app_data['name']}: {r.status_code} {r.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    return None

def add_reviews(token, app_id, reviews):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"app_id": app_id, "reviews": reviews}
    try:
        r = requests.post(f"{BASE_URL}/api/reviews/bulk/", json=data, headers=headers, timeout=10)
        if r.status_code == 201:
            count = r.json().get("created_count", 0)
            print(f"   [OK] Added {count} reviews to app {app_id}")
        else:
            print(f"   [FAIL] Add reviews: {r.status_code} {r.text}")
    except Exception as e:
        print(f"   [ERROR] {e}")

def add_watchlist(token, app_id):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(f"{BASE_URL}/api/watchlist/toggle/", json={"app_id": app_id}, headers=headers, timeout=5)
        if r.status_code == 200:
            status = r.json().get("status")
            print(f"   [OK] Watchlist toggle for app {app_id}: {status}")
    except Exception as e:
        print(f"   [ERROR] Watchlist: {e}")

def add_report(token, app_id, reason, desc):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"app": app_id, "reason": reason, "description": desc}
    try:
        r = requests.post(f"{BASE_URL}/api/reports/", json=data, headers=headers, timeout=5)
        if r.status_code == 201:
            print(f"   [OK] Reported app {app_id} as {reason}")
        else:
            print(f"   [FAIL] Report app: {r.status_code} {r.text}")
    except Exception as e:
        print(f"   [ERROR] Report: {e}")

def main():
    print_header("Seeding Fraud App Detection System")

    # 1. Users
    print_step("Creating Users")
    create_user("admin", "admin@example.com", "admin123")
    create_user("testuser", "test@example.com", "testpass123")
    create_user("analyst", "analyst@example.com", "securepass")

    # Login as testuser for most operations
    token = get_token("testuser", "testpass123")
    if not token:
        print("Aborting: Could not get token for testuser")
        sys.exit(1)

    # 2. Apps
    print_step("Creating Apps")
    apps_def = [
        {
            "name": "SafeCalc Pro",
            "package_name": "com.safecalc.pro",
            "developer": "Trusted Tools Inc.",
            "category": "Productivity",
            "description": "A simple calculator with no ads.",
            "store_url": "https://play.google.com/store/apps/details?id=com.safecalc.pro"
        },
        {
            "name": "Super Flashlight 2026",
            "package_name": "com.super.flashlight.free",
            "developer": "Unknown Dev",
            "category": "Tools",
            "description": "Brightest flashlight app. Requires contacts permission.",
            "store_url": "https://play.google.com/store/apps/details?id=com.super.flashlight.free"
        },
        {
            "name": "Crypto Miner X",
            "package_name": "com.crypto.miner.x",
            "developer": "CryptoKing",
            "category": "Finance",
            "description": "Mine bitcoin on your phone fast!",
            "store_url": "https://play.google.com/store/apps/details?id=com.crypto.miner.x"
        },
        {
            "name": "Daily Yoga",
            "package_name": "com.daily.yoga.fitness",
            "developer": "Health Corp",
            "category": "Health & Fitness",
            "description": "Yoga poses for everyone.",
            "store_url": "https://play.google.com/store/apps/details?id=com.daily.yoga.fitness"
        }
    ]

    created_apps = {}
    for ad in apps_def:
        app = create_app(token, ad)
        if app:
            created_apps[ad["package_name"]] = app["id"]

    # 3. Reviews
    print_step("Adding Reviews")
    
    # Legit App Reviews
    if "com.safecalc.pro" in created_apps:
        reviews = [
            {"text": "Works great, no ads as promised.", "rating": 5, "author": "UserA"},
            {"text": "Simple and clean.", "rating": 4, "author": "UserB"},
            {"text": "Best calculator.", "rating": 5, "author": "UserC"},
        ]
        add_reviews(token, created_apps["com.safecalc.pro"], reviews)

    # Suspicious App Reviews (Flashlight)
    if "com.super.flashlight.free" in created_apps:
        reviews = [
            {"text": "Why does a flashlight need my contacts?", "rating": 1, "author": "PrivacyNut"},
            {"text": "Too many ads, phone gets hot.", "rating": 2, "author": "HotPhone"},
            {"text": "It works but suspicious permissions.", "rating": 3, "author": "Anon"},
            {"text": "Good light.", "rating": 5, "author": "Bot1"},
        ]
        add_reviews(token, created_apps["com.super.flashlight.free"], reviews)

    # Fraud App Reviews (Crypto)
    if "com.crypto.miner.x" in created_apps:
        reviews = [
            {"text": "SCAM! I paid for upgrade and got nothing.", "rating": 1, "author": "VictimX"},
            {"text": "Fake app, does not mine anything.", "rating": 1, "author": "Miner1"},
            {"text": "Stole my data.", "rating": 1, "author": "AngryUser"},
            {"text": "Amazing app! Earned 1 BTC in a day!", "rating": 5, "author": "FakeBot"},
        ]
        add_reviews(token, created_apps["com.crypto.miner.x"], reviews)

    # 4. Watchlist
    print_step("Updating Watchlist")
    if "com.crypto.miner.x" in created_apps:
        add_watchlist(token, created_apps["com.crypto.miner.x"])
    if "com.super.flashlight.free" in created_apps:
        add_watchlist(token, created_apps["com.super.flashlight.free"])

    # 5. Community Reports
    print_step("Submitting Community Reports")
    if "com.crypto.miner.x" in created_apps:
        add_report(token, created_apps["com.crypto.miner.x"], "FRAUD", "Users reporting stolen money and fake mining functionality.")
    if "com.super.flashlight.free" in created_apps:
        add_report(token, created_apps["com.super.flashlight.free"], "PRIVACY", "Requests unnecessary permissions (Contacts, Location).")

    print_header("Seeding Complete. System ready for testing.")

if __name__ == "__main__":
    main()
