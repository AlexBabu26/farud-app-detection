#!/usr/bin/env python
"""
Add test apps and reviews using existing account: username=test, password=test@123.
Run with server at http://localhost:7000
"""

import requests

BASE_URL = "http://localhost:7000"
USERNAME = "test"
PASSWORD = "test@123"


def main():
    print("=" * 60)
    print("Adding Test Data (logged in as test)")
    print("=" * 60)

    # Login
    print("\n1. Logging in...")
    try:
        r = requests.post(
            f"{BASE_URL}/api/auth/token/",
            json={"username": USERNAME, "password": PASSWORD},
            timeout=10,
        )
    except Exception as e:
        print(f"   [ERROR] {e}. Is the server running on {BASE_URL}?")
        return
    if r.status_code != 200:
        print(f"   [FAIL] Login failed: {r.status_code} - {r.text[:200]}")
        return
    token = r.json().get("access")
    print("   [OK] Login successful.")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Create apps
    print("\n2. Creating apps...")
    apps_data = [
        {"name": "Suspicious Finance App", "package_name": "com.suspicious.finance", "store_url": "https://play.google.com/store/apps/details?id=com.suspicious.finance", "developer": "Unknown Developer", "category": "Finance"},
        {"name": "Legit Weather App", "package_name": "com.legit.weather", "store_url": "https://play.google.com/store/apps/details?id=com.legit.weather", "developer": "Trusted Weather Co.", "category": "Weather"},
        {"name": "Fraudulent Shopping App", "package_name": "com.fraud.shopping", "store_url": "https://play.google.com/store/apps/details?id=com.fraud.shopping", "developer": "Shady Retailer", "category": "Shopping"},
    ]
    created_apps = []
    for app_data in apps_data:
        r = requests.post(f"{BASE_URL}/api/apps/", json=app_data, headers=headers, timeout=10)
        if r.status_code == 201:
            created_apps.append(r.json())
            print(f"   [OK] {app_data['name']} (ID: {r.json()['id']})")
        elif r.status_code == 400 and "package_name" in r.text.lower():
            # Fetch existing apps to get IDs
            get_r = requests.get(f"{BASE_URL}/api/apps/", headers=headers, timeout=10)
            if get_r.status_code == 200:
                existing = get_r.json() if isinstance(get_r.json(), list) else get_r.json().get("results", [])
                for a in existing:
                    if a.get("package_name") == app_data["package_name"]:
                        created_apps.append(a)
                        print(f"   [EXISTS] {app_data['name']} (ID: {a['id']})")
                        break
        else:
            print(f"   [SKIP] {app_data['name']}: {r.status_code}")

    if not created_apps:
        r = requests.get(f"{BASE_URL}/api/apps/", headers=headers, timeout=10)
        if r.status_code == 200:
            created_apps = r.json() if isinstance(r.json(), list) else r.json().get("results", [])
            print(f"   Using {len(created_apps)} existing app(s).")
    if not created_apps:
        print("   [FAIL] No apps available. Create an app first.")
        return

    # Add reviews
    print("\n3. Adding reviews...")
    reviews_by_app = [
        (0, [
            {"text": "This app asked for my bank account details immediately after install. Very suspicious!", "rating": 1, "author": "ConcernedUser1", "source": "Google Play"},
            {"text": "App crashed and asked for credit card info. Not safe!", "rating": 1, "author": "User123", "source": "Google Play"},
            {"text": "Seems like a scam. Uninstalled immediately.", "rating": 1, "author": "SafetyFirst", "source": "Google Play"},
            {"text": "Great app, works perfectly!", "rating": 5, "author": "HappyUser", "source": "Google Play"},
        ]),
        (1, [
            {"text": "Accurate weather forecasts, clean interface. Highly recommend!", "rating": 5, "author": "WeatherFan", "source": "Google Play"},
            {"text": "Best weather app I've used. Very reliable.", "rating": 5, "author": "OutdoorEnthusiast", "source": "Google Play"},
            {"text": "Simple and effective. Does exactly what it says.", "rating": 4, "author": "SimpleUser", "source": "Google Play"},
        ]),
        (2, [
            {"text": "SCAM! Ordered products but never received them. Money stolen!", "rating": 1, "author": "Victim1", "source": "Google Play"},
            {"text": "Fake reviews everywhere. This is a fraudulent app. Stay away!", "rating": 1, "author": "WarnedUser", "source": "Google Play"},
            {"text": "Charged my card multiple times without authorization. REPORTED!", "rating": 1, "author": "AngryCustomer", "source": "Google Play"},
        ]),
    ]
    for idx, reviews in reviews_by_app:
        if idx >= len(created_apps):
            continue
        app = created_apps[idx]
        bulk = {"app_id": app["id"], "reviews": reviews}
        r = requests.post(f"{BASE_URL}/api/reviews/bulk/", json=bulk, headers=headers, timeout=10)
        if r.status_code == 201:
            n = r.json().get("created_count", len(reviews))
            print(f"   [OK] Added {n} reviews to {app['name']} (ID: {app['id']})")
        else:
            print(f"   [FAIL] {app['name']}: {r.status_code} - {r.text[:100]}")

    print("\n" + "=" * 60)
    print("Done. You can run analysis on any app at:")
    print(f"  {BASE_URL}/apps/<app_id>/")
    print("=" * 60)


if __name__ == "__main__":
    main()
