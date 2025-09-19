# In backend/weather_agent/app.py

from fastapi import FastAPI, Body, HTTPException
import httpx

app = FastAPI()

# Your OpenWeatherMap API key is now integrated
API_KEY = "1b36f29a31fd319954801a586d775f2c"

@app.post("/get_forecast")
async def get_forecast(
    lat: float = Body(..., embed=True),
    lon: float = Body(..., embed=True)
):
    if API_KEY == "YOUR_API_KEY_HERE":
        raise HTTPException(status_code=500, detail="OpenWeatherMap API key not set.")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            
            # Extract relevant weather information
            forecast = {
                "description": data["weather"][0]["description"].title(),
                "temperature_celsius": data["main"]["temp"],
                "humidity_percent": data["main"]["humidity"],
                "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 2)
            }
            return forecast
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse weather data: {e}")