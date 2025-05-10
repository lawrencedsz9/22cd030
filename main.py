from fastapi import FastAPI, HTTPException
from collections import deque
from services.number import fetch

app = FastAPI(title="Number Average Calci")

WINDOW_SIZE = 10
number_storage = deque(maxlen=WINDOW_SIZE)

@app.get("/numbers/{numberid}")
async def get_numbers(numberid: str):
    if numberid != 'p':  
        raise HTTPException(status_code=400)
    
    
    window_prev_state = list(number_storage)
    numbers = await fetch()
    if not numbers:
        raise HTTPException(status_code=500,)
    
    for num in numbers:
        if num not in number_storage:
            number_storage.append(num) 
    
    window_curr_state = list(number_storage)
    avg = sum(number_storage) / len(number_storage) if number_storage else 0.0
    
    return {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": numbers,
        "avg": round(avg, 2)
    }
