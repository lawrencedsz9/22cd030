from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from collections import deque
import asyncio


load_dotenv()

app = FastAPI(title="Number Average Calculator")

# Security
security = HTTPBearer()
TEST_SERVER_TOKEN = os.getenv("TEST_SERVER_TOKEN", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
WINDOW_SIZE = 10
NUMBER_TYPES = {
    'p': 'prime',
    'f': 'fibonacci',
    'e': 'even',
    'r': 'random'
}


number_storage: Dict[str, deque] = {
    number_type: deque(maxlen=WINDOW_SIZE)
    for number_type in NUMBER_TYPES.keys()
}

class NumberResponse(BaseModel):
    number: int
    type: str
    average: float

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the bearer token
    """
    if credentials.credentials != ACCESS_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

async def fetch_number(number_type: str) -> int:
    """
    Fetch a number from the test server based on the type
    """
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {TEST_SERVER_TOKEN}",
                "Content-Type": "application/json"
            }
            response = await client.get(
                f"http://test-server.com/numbers/{NUMBER_TYPES[number_type]}",
                headers=headers
            )
            if response.status_code == 200:
                return response.json()['number']
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid test server token")
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch number")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

def calculate_average(numbers: deque) -> float:
    """
    Calculate the average of numbers in the deque
    """
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

@app.get("/numbers/{number_type}", response_model=NumberResponse, dependencies=[Depends(verify_token)])
async def get_number_average(number_type: str):
    """
    Get a number and calculate its average with the window of previous numbers
    """
    if number_type not in NUMBER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid number type. Must be one of: {', '.join(NUMBER_TYPES.keys())}"
        )

    # Fetch new number
    new_number = await fetch_number(number_type)
    
    # Add to storage
    number_storage[number_type].append(new_number)
    
    # Calculate average
    average = calculate_average(number_storage[number_type])
    
    return NumberResponse(
        number=new_number,
        type=NUMBER_TYPES[number_type],
        average=average
    )

@app.get("/numbers/{number_type}/history", dependencies=[Depends(verify_token)])
async def get_number_history(number_type: str):
    """
    Get the history of numbers for a specific type
    """
    if number_type not in NUMBER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid number type. Must be one of: {', '.join(NUMBER_TYPES.keys())}"
        )
    
    return {
        "type": NUMBER_TYPES[number_type],
        "numbers": list(number_storage[number_type]),
        "average": calculate_average(number_storage[number_type])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 