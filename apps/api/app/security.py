import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

password_hash=PasswordHash.recommended()
SECRET=os.getenv("JWT_SECRET","change-this-secret-in-production")
ALGORITHM="HS256"

def hash_password(password:str)->str: return password_hash.hash(password)
def verify_password(password:str, hashed:str)->bool: return password_hash.verify(password,hashed)
def create_token(user_id:int)->str:
    exp=datetime.now(timezone.utc)+timedelta(days=7)
    return jwt.encode({"sub":str(user_id),"exp":exp},SECRET,algorithm=ALGORITHM)
def decode_token(token:str)->int:
    payload=jwt.decode(token,SECRET,algorithms=[ALGORITHM])
    return int(payload["sub"])
