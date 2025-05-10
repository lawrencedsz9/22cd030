import httpx
from services.auth import get_token

async def fetch():
    token = get_token()
    if token:
        print(f"Token: {token}")
    else:
        print("token not found")

    url = "http://20.244.56.144/evaluation-service/primes"
    headers  = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient(timeout=0.5) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()  
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Error fetching numbers: {e}")
        return None
