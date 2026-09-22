import os
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import Farm, FarmRecord, User
from .schemas import RegisterRequest, LoginRequest, FarmCreate, RecordCreate, AIRequest
from .security import hash_password, verify_password, create_token, decode_token

Base.metadata.create_all(bind=engine)
app = FastAPI(title="KAIFARMS AI API", version="0.2.0")
bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(401, "Authentication required")
    try: user_id = decode_token(credentials.credentials)
    except Exception: raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "User not found")
    return user

@app.get("/health")
def health():
    return {"status":"ok","service":"kaifarms-ai-api","version":"0.2.0"}

@app.post("/api/auth/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, "Email already registered")
    user = User(full_name=data.full_name,email=str(data.email).lower(),phone=data.phone,password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"token":create_token(user.id),"user":{"id":user.id,"full_name":user.full_name,"email":user.email,"phone":user.phone}}

@app.post("/api/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user=db.query(User).filter(User.email==str(data.email).lower()).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid email or password")
    return {"token":create_token(user.id),"user":{"id":user.id,"full_name":user.full_name,"email":user.email,"phone":user.phone}}

@app.get("/api/me")
def me(user: User = Depends(current_user)):
    return {"id":user.id,"full_name":user.full_name,"email":user.email,"phone":user.phone}

@app.post("/api/farms")
def create_farm(data: FarmCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    farm=Farm(user_id=user.id,**data.model_dump()); db.add(farm); db.commit(); db.refresh(farm)
    return farm_payload(farm)

def farm_payload(farm: Farm):
    return {"id":farm.id,"name":farm.name,"location":farm.location,"farm_type":farm.farm_type,"size_hectares":farm.size_hectares,"primary_activity":farm.primary_activity}

@app.get("/api/farms")
def list_farms(user: User = Depends(current_user), db: Session = Depends(get_db)):
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

@app.post("/api/ai/chat")
def ai_chat(request: AIRequest, user: User = Depends(current_user)):
    key=os.getenv("OPENAI_API_KEY")
    if not key:
        return {"answer":"I can help assess the farming question. Please provide the crop or animal, age/growth stage, location, visible symptoms, when the problem started, and any treatment already used.","mode":"safe-demo"}
    from openai import OpenAI
    client=OpenAI(api_key=key)
    system="You are KAIFARMS AI, an agricultural assistant for African farmers. Give practical, cautious guidance. Do not claim certainty when evidence is insufficient. Do not prescribe restricted medicines. For serious animal illness or uncertain diagnosis, recommend a qualified veterinarian or agricultural expert."
    prompt=request.question + ("\\nContext: "+request.context if request.context else "")
    response=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.6-luna"),input=[{"role":"system","content":system},{"role":"user","content":prompt}])
    return {"answer":response.output_text,"mode":"ai"}
