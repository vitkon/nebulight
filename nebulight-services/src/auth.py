# src/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from supabase import create_client, Client
from .config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = supabase.auth.get_user(token).user
        print(user)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": request.email, "password": request.password})
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    return {
        "access_token": auth_response.session.access_token,
        "token_type": "bearer"
    }

    # if auth_response.get('error'):
    #     raise HTTPException(status_code=401, detail=auth_response['error']['message'])
    # if not auth_response.get('data') or not auth_response['data'].get('access_token'):
    #     raise HTTPException(status_code=401, detail="Invalid email or password")

    # return {
    #     "access_token": auth_response['data']['access_token'],
    #     "token_type": "bearer"
    # }
