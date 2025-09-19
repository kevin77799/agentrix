# In backend/main.py

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import TypedDict, Optional
import httpx
from langgraph.graph import StateGraph, END
from bson import ObjectId
import datetime
import os

# Import the database collection
from database import advisory_collection

# --- 1. Define the State (with a new resource advice field) ---
class AgentState(TypedDict):
    inputs: dict
    weather_forecast: Optional[dict]
    recommended_crop: str
    market_price: float
    resource_advice: Optional[dict] # New field for resource advice
    disease_prediction: Optional[dict]
    final_advice: dict

# --- 2. Define the Agent Nodes ---

# Environment variables for microservice URLs
WEATHER_SERVICE_URL = os.getenv('WEATHER_SERVICE_URL', 'http://127.0.0.1:8004')
CROP_SERVICE_URL = os.getenv('CROP_SERVICE_URL', 'http://127.0.0.1:8002')
MARKET_SERVICE_URL = os.getenv('MARKET_SERVICE_URL', 'http://127.0.0.1:8003')
RESOURCE_SERVICE_URL = os.getenv('RESOURCE_SERVICE_URL', 'http://127.0.0.1:8005')
DISEASE_SERVICE_URL = os.getenv('DISEASE_SERVICE_URL', 'http://127.0.0.1:8001')

def weather_agent_node(state: AgentState):
    print("---CALLING WEATHER AGENT---")
    try:
        lat, lon = map(float, state["inputs"]["gps"].split(','))
        response = httpx.post(f"{WEATHER_SERVICE_URL}/get_forecast", json={"lat": lat, "lon": lon})
        response.raise_for_status()
        state["weather_forecast"] = response.json()
    except Exception as e:
        print(f"Weather agent failed: {e}")
        state["weather_forecast"] = None
    return state

def crop_advisor_node(state: AgentState):
    print("---CALLING CROP ADVISOR---")
    soil = state["inputs"]["soil_type"]
    response = httpx.post(f"{CROP_SERVICE_URL}/recommend_crop", json={"soil_type": soil})
    state["recommended_crop"] = response.json().get("recommended_crop")
    return state

def market_analyst_node(state: AgentState):
    print("---CALLING MARKET ANALYST---")
    crop = state.get("recommended_crop")
    response = httpx.post(f"{MARKET_SERVICE_URL}/predict_price", json={"crop": crop})
    state["market_price"] = response.json().get("predicted_price_per_quintal")
    return state

# NEW: Node to call the Resource Agent
def resource_agent_node(state: AgentState):
    print("---CALLING RESOURCE AGENT---")
    try:
        crop = state.get("recommended_crop")
        # The resource agent will run on port 8005
        response = httpx.post(f"{RESOURCE_SERVICE_URL}/get_resource_advice", json={"crop": crop})
        response.raise_for_status()
        state["resource_advice"] = response.json()
    except Exception as e:
        print(f"Resource agent failed: {e}")
        state["resource_advice"] = None
    return state

def disease_detection_node(state: AgentState):
    print("---CALLING DISEASE DETECTOR---")
    image = state["inputs"]["image_bytes"]
    files = {'file': ('leaf_image.jpg', image, 'image/jpeg')}
    response = httpx.post(f"{DISEASE_SERVICE_URL}/predict", files=files)
    state["disease_prediction"] = response.json()
    return state
        
# UPDATED: Advice node now includes resource advice
def generate_advice_node(state: AgentState):
    print("---GENERATING FINAL ADVICE---")
    crop = state["recommended_crop"]
    price = state["market_price"]
    disease_info = state.get("disease_prediction")
    weather_info = state.get("weather_forecast")
    resource_info = state.get("resource_advice")

    # English Advice
    advice_en = ""
    if weather_info:
        advice_en += f"**Today's Forecast:** {weather_info['description']} at {weather_info['temperature_celsius']}°C.\n\n"
    advice_en += f"**Crop & Market:** Based on your soil, we recommend planting '{crop}'. The expected market price is ₹{price} per quintal.\n\n"
    if resource_info:
        advice_en += f"**Resource Advice:**\n* **Fertilizer:** {resource_info['fertilizer']}\n* **Irrigation:** {resource_info['irrigation']}\n\n"
    if disease_info:
        disease = disease_info.get('disease')
        confidence = disease_info.get('confidence', 0) * 100
        advice_en += f"**Leaf Analysis:** We detected '{disease}' with {confidence:.2f}% confidence."

    # Malayalam Advice
    advice_ml = ""
    if weather_info:
        advice_ml += f"**ഇന്നത്തെ കാലാവസ്ഥ:** {weather_info['temperature_celsius']}°C താപനിലയിൽ '{weather_info['description']}'.\n\n"
    advice_ml += f"**വിളയും വിപണിയും:** നിങ്ങളുടെ മണ്ണിന്റെ അടിസ്ഥാനത്തിൽ '{crop}' നടാൻ ഞങ്ങൾ ശുപാർശ ചെയ്യുന്നു. പ്രതീക്ഷിക്കുന്ന വിപണി വില ക്വിന്റലിന് ₹{price} ആണ്.\n\n"
    if resource_info:
        advice_ml += f"**വിഭവങ്ങൾക്കുള്ള ഉപദേശം:**\n* **വളം:** {resource_info['fertilizer_ml']}\n* **ജലസേചനം:** {resource_info['irrigation_ml']}\n\n"
    if disease_info:
        disease = disease_info.get('disease')
        confidence = disease_info.get('confidence', 0) * 100
        advice_ml += f"**ഇലകളുടെ വിശകലനം:** ഞങ്ങൾ '{disease}' {confidence:.2f}% കൃത്യതയോടെ കണ്ടെത്തി."
        
    state["final_advice"] = {"en": advice_en, "ml": advice_ml}
    return state

# --- 3. Build the Graph (with the new Resource Agent) ---
def should_run_disease_detection(state: AgentState):
    return "disease_detection_node" if state["inputs"]["image_bytes"] else "market_analyst_node"

workflow = StateGraph(AgentState)
workflow.add_node("weather_agent", weather_agent_node)
workflow.add_node("crop_advisor", crop_advisor_node)
workflow.add_node("disease_detection_node", disease_detection_node)
workflow.add_node("market_analyst_node", market_analyst_node) 
workflow.add_node("resource_agent_node", resource_agent_node) # Add new node
workflow.add_node("generate_advice", generate_advice_node)

workflow.set_entry_point("weather_agent")
workflow.add_edge("weather_agent", "crop_advisor")
workflow.add_conditional_edges("crop_advisor", should_run_disease_detection, {"disease_detection_node": "disease_detection_node", "market_analyst_node": "market_analyst_node"})
workflow.add_edge("disease_detection_node", "market_analyst_node")
workflow.add_edge("market_analyst_node", "resource_agent_node") # New edge
workflow.add_edge("resource_agent_node", "generate_advice") # New edge
workflow.add_edge("generate_advice", END)
app_graph = workflow.compile()

# --- 4. Setup FastAPI Server ---
app = FastAPI()
origins = ["http://localhost:3000", "http://192.168.0.102:3000", "http://192.168.56.1:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/api/get-advice")
async def get_advice(
    gps: str = Form(...),
    soil_type: str = Form(...),
    lang: str = Form("en"),
    leaf_photo: Optional[UploadFile] = File(None)
):
    image_data = await leaf_photo.read() if leaf_photo else None
    
    request_doc = { "gps": gps, "soil_type": soil_type, "lang": lang, "has_photo": image_data is not None, "status": "pending", "timestamp": datetime.datetime.now(datetime.UTC) }
    result = advisory_collection.insert_one(request_doc)
    request_id = result.inserted_id

    inputs = { "inputs": { "gps": gps, "soil_type": soil_type, "language": lang, "image_bytes": image_data } }
    final_state = app_graph.invoke(inputs)
    
    advisory_collection.update_one( {"_id": request_id}, {"$set": { "status": "complete", "results": { "weather_forecast": final_state.get("weather_forecast"), "recommended_crop": final_state.get("recommended_crop"), "market_price": final_state.get("market_price"), "resource_advice": final_state.get("resource_advice"), "disease_prediction": final_state.get("disease_prediction"), "advice_en": final_state.get("final_advice", {}).get("en"), "advice_ml": final_state.get("final_advice", {}).get("ml") } } } )
    
    return {"advice": final_state.get("final_advice")}