import os
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="KAIFARMS AI API", version="0.1.0")

class Farmer(BaseModel):
    full_name: str
    phone: str
    location: str
    farm_type: str

class FarmRecord(BaseModel):
    activity: str
    crop_or_livestock: str
    notes: str = ""

class AIRequest(BaseModel):
    question: str
    context: Optional[str] = None

@app.get("/health")
def health():
    return {"status":"ok","service":"kaifarms-ai-api","version":"0.1.0"}

@app.post("/api/farmers")
def create_farmer(farmer: Farmer):
    return {"id":"demo-farmer-1", **farmer.model_dump()}

@app.post("/api/farm-records")
def create_record(record: FarmRecord):
    return {"id":"demo-record-1", **record.model_dump()}

@app.post("/api/ai/chat")
def ai_chat(request: AIRequest):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return {"answer":"I can help you assess the farming question. For a reliable recommendation, provide the crop or animal, age/growth stage, location, visible symptoms, when the problem started, and any treatment already used.","mode":"safe-demo"}
    from openai import OpenAI
    client = OpenAI(api_key=key)
    system = "You are KAIFARMS AI, an agricultural assistant for African farmers. Give practical, cautious guidance. Do not claim certainty when evidence is insufficient. Do not prescribe restricted medicines. For serious animal illness or uncertain diagnosis, recommend a qualified veterinarian/agricultural expert."
    response = client.responses.create(model="gpt-5-mini", input=[{"role":"system","content":system},{"role":"user","content":request.question + ("\nContext: " + request.context if request.context else "")}])
    return {"answer":response.output_text,"mode":"ai"}
