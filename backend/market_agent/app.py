# In backend/market_agent/app.py
from fastapi import FastAPI, Body

app = FastAPI()

@app.post("/predict_price")
async def predict_price(crop: str = Body(..., embed=True)):
    print(f"Market Agent received crop: {crop}")
    # Dummy logic: return a fake price forecast
    price_forecast = {
        "Rice": 2100,
        "Groundnut": 5500,
        "Millet": 1800
    }

    price = price_forecast.get(crop, 2000) # Default price

    return {"crop": crop, "predicted_price_per_quintal": price}