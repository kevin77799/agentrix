# In backend/resource_agent/app.py

from fastapi import FastAPI, Body, HTTPException

app = FastAPI()

# A simple rule-based dictionary for recommendations
RESOURCE_GUIDELINES = {
    "Rice": {
        "fertilizer": "High in Nitrogen (e.g., Urea). Apply in split doses during the vegetative stage.",
        "irrigation": "Requires standing water. Maintain a consistent water level of 2-5 cm through most of the growing season.",
        "fertilizer_ml": "നൈട്രജൻ കൂടുതലുള്ള വളം (ഉദാ: യൂറിയ). കൃഷിയുടെ ആദ്യഘട്ടത്തിൽ പലതവണയായി പ്രയോഗിക്കുക.",
        "irrigation_ml": "പാടത്ത് വെള്ളം കെട്ടിനിർത്തേണ്ടത് ആവശ്യമാണ്. കൃഷിയുടെ ഭൂരിഭാഗം സമയത്തും 2-5 സെന്റിമീറ്റർ ജലനിരപ്പ് നിലനിർത്തുക."
    },
    "Millet": {
        "fertilizer": "Balanced NPK (Nitrogen, Phosphorus, Potassium) fertilizer. Less nitrogen is required compared to rice.",
        "irrigation": "Drought-tolerant. Water deeply but infrequently. Allow soil to dry between waterings.",
        "fertilizer_ml": "സന്തുലിതമായ NPK വളം. അരിയെ അപേക്ഷിച്ച് കുറഞ്ഞ നൈട്രജൻ മതിയാകും.",
        "irrigation_ml": "വരൾച്ചയെ അതിജീവിക്കാൻ കഴിവുള്ള വിള. ആഴത്തിൽ നനയ്ക്കുക, പക്ഷേ ഇടയ്ക്കിടെ മാത്രം. നനയ്ക്കുന്നതിന് മുമ്പ് മണ്ണ് ഉണങ്ങാൻ അനുവദിക്കുക."
    },
    "Groundnut": {
        "fertilizer": "Low nitrogen, but high in Phosphorus and Potassium. Gypsum is recommended during the pegging stage.",
        "irrigation": "Requires consistent moisture, especially during flowering and pod formation. Avoid waterlogging.",
        "fertilizer_ml": "നൈട്രജൻ കുറവും ഫോസ്ഫറസ്, പൊട്ടാസ്യം എന്നിവ കൂടുതലുള്ളതുമായ വളം. കായ് പിടിക്കുന്ന ഘട്ടത്തിൽ ജിപ്സം ശുപാർശ ചെയ്യുന്നു.",
        "irrigation_ml": "പൂവിടുന്ന സമയത്തും കായ് പിടിക്കുന്ന സമയത്തും ഈർപ്പം നിലനിർത്തേണ്ടത് അത്യാവശ്യമാണ്. വെള്ളക്കെട്ട് ഒഴിവാക്കുക."
    }
}

DEFAULT_ADVICE = {
    "fertilizer": "Use a balanced fertilizer suitable for your region. Consult a local agricultural expert for specific details.",
    "irrigation": "Ensure adequate watering based on soil type and weather conditions.",
    "fertilizer_ml": "നിങ്ങളുടെ പ്രദേശത്തിന് അനുയോജ്യമായ സന്തുലിത വളം ഉപയോഗിക്കുക. കൂടുതൽ വിവരങ്ങൾക്കായി ഒരു പ്രാദേശിക കൃഷി വിദഗ്ദ്ധനുമായി ബന്ധപ്പെടുക.",
    "irrigation_ml": "മണ്ണിന്റെ തരവും കാലാവസ്ഥയും അനുസരിച്ച് ആവശ്യത്തിന് നനയ്ക്കുക."
}


@app.post("/get_resource_advice")
async def get_resource_advice(
    crop: str = Body(..., embed=True)
):
    # Find the advice for the given crop, or use the default if not found
    advice = RESOURCE_GUIDELINES.get(crop, DEFAULT_ADVICE)
    return advice