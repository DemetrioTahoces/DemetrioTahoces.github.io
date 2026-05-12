from fastapi.testclient import TestClient
from api.index import app
from core.config import settings

def test_rate_limit():
    client = TestClient(app)
    print(f"--- Testing Rate Limit for /api/health ---")
    print(f"Configured Limit: {settings.rate_limit_per_minute} requests per minute")
    
    # Send enough requests to trigger the limit
    # The limit is applied per IP, TestClient uses 'testclient' as IP
    for i in range(1, 10):
        response = client.get("/api/health")
        print(f"Request {i}: Status Code = {response.status_code}")
        if response.status_code == 429:
            print(f"  -> Rate limit reached! Response body: {response.json()}")
            break

if __name__ == "__main__":
    test_rate_limit()
