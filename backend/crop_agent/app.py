# In backend/crop_agent/app.py
from fastapi import FastAPI, Body

app = FastAPI()

@app.post("/recommend_crop")
async def recommend_crop(soil_type: str = Body(..., embed=True)):
    print(f"Crop Agent received soil type: {soil_type}")
    # Dummy logic: recommend crops based on soil type
    if "alluvial" in soil_type.lower():
        recommendation = "Rice"
    elif "sandy" in soil_type.lower():
        recommendation = "Groundnut"
    else:
        recommendation = "Millet"

    return {"recommended_crop": recommendation, "predicted_yield_tons_per_acre": 2.5}