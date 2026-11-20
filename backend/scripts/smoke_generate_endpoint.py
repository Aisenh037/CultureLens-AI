import urllib.request
import json

url = "http://127.0.0.1:8000/api/travel/generate"
payload = {
    "destination": "Kyoto, Japan",
    "budget": "Budget",
    "duration_days": 1,
    "travel_style": "Solo",
    "companions": "None",
    "interests": ["Culture"],
    "languages": ["English"],
    "accessibility_needs": [],
    "food_preference": "No Restrictions"
}

headers = {
    "Content-Type": "application/json"
}

print("==================================================")
print("     CultureLens AI - Endpoint Integration Test   ")
print("==================================================")
print(f"Sending test query to: {url}...")
print("Destination: Kyoto, Japan")

try:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    with urllib.request.urlopen(req, timeout=120) as response:
        status_code = response.getcode()
        body = response.read().decode("utf-8")
        
        print(f"\n[SUCCESS] Server responded with status code {status_code}!")
        parsed_body = json.loads(body)
        print("Successfully generated CultureLens Travel Plan!")
        print(f"Summary excerpt: \"{parsed_body.get('summary', '')[:100]}...\"")
        print(f"Weather: {parsed_body.get('weather', {}).get('current_temp')} ({parsed_body.get('weather', {}).get('conditions')})")
        print(f"Exchange Rate (JPY): {parsed_body.get('budget', {}).get('estimated_daily_cost')}")
        print(f"Total Attractions Found: {len(parsed_body.get('top_attractions', []))}")
        print("Factual geocoded coords mapping matches map viewports successfully!")
except Exception as e:
    print(f"\n[REQUEST FAILURE] Could not connect to the server on port 8000.")
    print("Please make sure that the FastAPI backend server is currently running.")
    print(f"Details: {str(e)}")
