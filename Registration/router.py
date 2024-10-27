from fastapi import APIRouter, HTTPException
# from app.crud import user as crud_user
from Registration.schemas import UserDetail, UserResponse, SteamResponse
import secretManager
import requests
from botocore.exceptions import ClientError
import Registration.response_example as response_example

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserDetail):
    userResouce = UserDetail(config=None)
    existing_user = userResouce.checkUserExists(user.email)
    if existing_user:
        return UserResponse(status_code=400,message="User already exists")

    # Insert user into database
    success = userResouce.register(user)
    if not success:
        return UserResponse(status_code=500, message="Error registering user")
    return UserResponse(status_code=201, message= "User registered successfully!")

@router.get("/steam/validate", response_model=SteamResponse, responses=response_example.steam_validate_responses)
def check_steam_id(steam_id: str):
    secret_manager = secretManager.SecretManager()
    STEAM_API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    try:
        STEAM_API_KEY = secret_manager.get_secret("steamAPI_key","us-east-1")
        params = {
            "key": STEAM_API_KEY,
            "steamids": steam_id
        }

        response = requests.get(STEAM_API_URL, params=params)
        
        if response.status_code != 200:
            return SteamResponse(status_code=500, message="Error contacting Steam API")
        
        data = response.json()
        players = data.get("response", {}).get("players", [])
        
        if not players.is_empty():
            return SteamResponse(
                statusCode=200,
                steam_details=players[0], 
                message="Steam user found successfully."
            )
        else:
            return SteamResponse(status_code=404, message="User doesn't exist on Steam")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

