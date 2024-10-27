from pydantic import BaseModel, EmailStr
from typing import Dict, Any

class UserDetail(BaseModel):
    userId: str = None
    password: str
    email: EmailStr
    displayName: str
    steamID: str

class BaseResponse(BaseModel):
    statusCode: int
    message: str

class UserResponse(BaseResponse):
    pass

class SteamResponse(BaseResponse):
    steam_details: Dict[str, Any]
    
