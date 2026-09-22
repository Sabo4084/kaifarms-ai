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
