from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name:str=Field(min_length=2,max_length=150)
    email:EmailStr
    phone:str=Field(min_length=7,max_length=30)
    password:str=Field(min_length=8,max_length=128)

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class FarmCreate(BaseModel):
    name:str
    location:str
    farm_type:str
    size_hectares:float|None=None
    primary_activity:str

class RecordCreate(BaseModel):
    activity:str
    crop_or_livestock:str
    notes:str=""

class AIRequest(BaseModel):
    question:str=Field(min_length=3)
    context:str|None=None
    farm_id:int|None=None
    assistant_mode:str="auto"


class ReferralCreate(BaseModel):
    farm_id:int|None=None
    consultation_id:int|None=None
    category:str=Field(min_length=3,max_length=30)
    issue_summary:str=Field(min_length=10,max_length=4000)
    urgency:str="routine"
    contact_method:str="in_app"
    contact_details:str|None=Field(default=None,max_length=255)
