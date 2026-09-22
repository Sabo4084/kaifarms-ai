import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import Farm, FarmRecord, User, Consultation
from .schemas import RegisterRequest, LoginRequest, FarmCreate, RecordCreate, AIRequest
from .security import hash_password, verify_password, create_token, decode_token

Base.metadata.create_all(bind=engine)
app = FastAPI(title="KAIFARMS AI API", version="0.4.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
bearer = HTTPBearer(auto_error=False)

ASSISTANT_MODES = {
    "crop": {
        "label": "Crop Assistant",
        "focus": "crop production, agronomy, soil, nutrients, weeds, pests, diseases, irrigation, planting, harvesting and post-harvest handling",
        "intake": "Ask for crop/variety, growth stage or days after planting, field size, location, symptoms, weather/irrigation, recent inputs and farm records when relevant."
    },
    "poultry": {
        "label": "Poultry Assistant",
        "focus": "broilers, layers, chicks, housing, brooding, feeding, water, vaccination, biosecurity, production performance, egg quality and poultry disease risk",
        "intake": "Ask for bird type, age, flock size, housing conditions, feed/water, vaccination history, mortality, production rate and symptoms when relevant."
    },
    "livestock": {
        "label": "Livestock Assistant",
        "focus": "cattle, goats, sheep and other farm livestock, nutrition, housing, breeding, parasites, herd health and animal welfare",
        "intake": "Ask for species, age/sex, number affected, body condition, symptoms, duration, feeding, housing, vaccination/deworming history and treatments already used."
    }
}

def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials: raise HTTPException(401, "Authentication required")
    try: user_id = decode_token(credentials.credentials)
    except Exception: raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "User not found")
    return user

@app.get("/health")
def health(): return {"status":"ok","service":"kaifarms-ai-api","version":"0.4.0"}

@app.post("/api/auth/register")
def register(data:RegisterRequest,db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==str(data.email).lower()).first(): raise HTTPException(409,"Email already registered")
    user=User(full_name=data.full_name,email=str(data.email).lower(),phone=data.phone,password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"token":create_token(user.id),"user":{"id":user.id,"full_name":user.full_name,"email":user.email,"phone":user.phone}}

@app.post("/api/auth/login")
def login(data:LoginRequest,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==str(data.email).lower()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid email or password")
    return {"token":create_token(user.id),"user":{"id":user.id,"full_name":user.full_name,"email":user.email,"phone":user.phone}}

@app.get("/api/me")
def me(user:User=Depends(current_user)): return {"id":user.id,"full_name":user.full_name,"email":user.email,"phone":user.phone}

def farm_payload(farm:Farm):
    return {"id":farm.id,"name":farm.name,"location":farm.location,"farm_type":farm.farm_type,"size_hectares":farm.size_hectares,"primary_activity":farm.primary_activity}

@app.post("/api/farms")
def create_farm(data:FarmCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    farm=Farm(user_id=user.id,**data.model_dump()); db.add(farm); db.commit(); db.refresh(farm); return farm_payload(farm)

@app.get("/api/farms")
def list_farms(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return [farm_payload(f) for f in db.query(Farm).filter(Farm.user_id==user.id).all()]

@app.post("/api/farms/{farm_id}/records")
def create_record(farm_id:int,data:RecordCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    farm=db.query(Farm).filter(Farm.id==farm_id,Farm.user_id==user.id).first()
    if not farm: raise HTTPException(404,"Farm not found")
    record=FarmRecord(farm_id=farm.id,**data.model_dump()); db.add(record); db.commit(); db.refresh(record)
    return {"id":record.id,"farm_id":record.farm_id,"activity":record.activity,"crop_or_livestock":record.crop_or_livestock,"notes":record.notes}

@app.get("/api/farms/{farm_id}/records")
def list_records(farm_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    farm=db.query(Farm).filter(Farm.id==farm_id,Farm.user_id==user.id).first()
    if not farm: raise HTTPException(404,"Farm not found")
    return [{"id":r.id,"activity":r.activity,"crop_or_livestock":r.crop_or_livestock,"notes":r.notes} for r in farm.records]

def farm_context(user:User,db:Session,farm_id:int|None):
    if not farm_id: return ""
    farm=db.query(Farm).filter(Farm.id==farm_id,Farm.user_id==user.id).first()
    if not farm: raise HTTPException(404,"Farm not found")
    records=db.query(FarmRecord).filter(FarmRecord.farm_id==farm.id).order_by(FarmRecord.id.desc()).limit(10).all()
    details=[f"Farm: {farm.name}",f"Location: {farm.location}",f"Type: {farm.farm_type}",f"Size: {farm.size_hectares} ha",f"Primary activity: {farm.primary_activity}"]
    if records:
        details.append("Recent farm records: "+" | ".join(f"{r.activity}: {r.crop_or_livestock} - {r.notes}" for r in records))
    return "\n".join(details)

def route_mode(requested:str,farm_type:str|None,question:str):
    if requested in ASSISTANT_MODES: return requested
    q=question.lower()
    if any(x in q for x in ["chicken","poultry","broiler","layer","chick","egg","flock"]): return "poultry"
    if any(x in q for x in ["cattle","cow","goat","sheep","ram","livestock","calf","herd"]): return "livestock"
    if farm_type in ASSISTANT_MODES: return farm_type
    return "crop"

@app.post("/api/ai/chat")
def ai_chat(request:AIRequest,user:User=Depends(current_user),db:Session=Depends(get_db)):
    context=farm_context(user,db,request.farm_id)
    farm_type=None
    if request.farm_id:
        farm=db.query(Farm).filter(Farm.id==request.farm_id,Farm.user_id==user.id).first()
        farm_type=farm.farm_type if farm else None
    mode=route_mode(request.assistant_mode,farm_type,request.question)
    profile=ASSISTANT_MODES[mode]
    if request.context: context += ("\nFarmer context: "+request.context) if context else request.context
    key=os.getenv("OPENAI_API_KEY")
    if not key:
        answer=f"{profile['label']} selected. I can help with {profile['focus']}. {profile['intake']}"
        mode_status="safe-demo"
    else:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        system=f"""You are KAIFARMS AI — {profile['label']} for African farmers.
Primary focus: {profile['focus']}.
Use the farmer's farm context below whenever provided. The farmer may be in Nigeria, including North-Central conditions, so use practical locally relevant reasoning without inventing local facts.
Intake guidance: {profile['intake']}
Explain what is known, what is uncertain, and the next practical steps. Prefer integrated crop/poultry/livestock management and prevention.
For animal cases, do not claim a definitive diagnosis from text alone, do not prescribe restricted medicines, and do not give unsafe dosing. For severe illness, rapid deaths, neurological signs, poisoning, severe dehydration, or other urgent cases, recommend prompt assessment by a qualified veterinarian.
For crop cases, distinguish likely causes from confirmed diagnosis and recommend field checks before costly treatment.
Never fabricate a farm record, weather observation, laboratory result, diagnosis, or treatment history."""
        prompt=request.question + ("\nFarm context:\n"+context if context else "")
        response=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.6-luna"),input=[{"role":"system","content":system},{"role":"user","content":prompt}])
        answer=response.output_text
        mode_status="ai"
    consultation=Consultation(user_id=user.id,farm_id=request.farm_id,question=request.question,answer=answer,mode=mode)
    db.add(consultation); db.commit(); db.refresh(consultation)
    return {"id":consultation.id,"answer":answer,"mode":mode,"status":mode_status,"farm_id":request.farm_id}

@app.get("/api/ai/modes")
def ai_modes(): return [{"id":k,"label":v["label"],"focus":v["focus"]} for k,v in ASSISTANT_MODES.items()]

@app.get("/api/ai/history")
def ai_history(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.query(Consultation).filter(Consultation.user_id==user.id).order_by(Consultation.created_at.desc()).limit(50).all()
    return [{"id":r.id,"farm_id":r.farm_id,"question":r.question,"answer":r.answer,"mode":r.mode,"created_at":r.created_at.isoformat()} for r in rows]
