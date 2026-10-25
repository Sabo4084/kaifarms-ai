from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterRequest(BaseModel):
    full_name:str=Field(min_length=2,max_length=150)
    email:EmailStr
    phone:str=Field(min_length=7,max_length=30)
    password:str=Field(min_length=8,max_length=128)

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class FarmCreate(BaseModel):
    name:str=Field(min_length=2,max_length=150)
    location:str=Field(min_length=2,max_length=150)
    farm_type:str=Field(pattern="^(crop|poultry|livestock|mixed)$")
    size_hectares:float|None=Field(default=None,ge=0,le=1000000)
    primary_activity:str=Field(min_length=2,max_length=150)

class RecordCreate(BaseModel):
    activity:str=Field(min_length=2,max_length=100)
    crop_or_livestock:str=Field(min_length=1,max_length=100)
    notes:str=Field(default="",max_length=5000)

class AIRequest(BaseModel):
    question:str=Field(min_length=3,max_length=8000)
    context:str|None=Field(default=None,max_length=8000)
    farm_id:int|None=Field(default=None,gt=0)
    assistant_mode:str=Field(default="auto",max_length=20)


class ReferralCreate(BaseModel):
    farm_id:int|None=Field(default=None,gt=0)
    consultation_id:int|None=Field(default=None,gt=0)
    category:str=Field(min_length=3,max_length=30)
    issue_summary:str=Field(min_length=10,max_length=4000)
    urgency:str=Field(default="routine",max_length=20)
    contact_method:str=Field(default="in_app",max_length=30)
    contact_details:str|None=Field(default=None,max_length=255)
