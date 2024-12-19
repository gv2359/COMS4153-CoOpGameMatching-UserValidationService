from fastapi import APIRouter, Query, HTTPException, Header
from app.models.UserLogin import UserInfo, MessageResponse, ErrorResponse, UserInfoResponse, LoginResponse
from app.services.service_factory import ServiceFactory
from framework.exceptions.user_token_exceptions import TokenExpiredException, TokenNotValidException

router = APIRouter()
res = ServiceFactory.get_service("UserLoginResource")
@router.post("/login-google", response_model=LoginResponse, responses={400: {"model": ErrorResponse}})
async def login_google(authorization: str = Header(...)):
    """
    Handle login using Firebase ID Token.
    """
    try:
        id_token = authorization.split(" ")[1]  # Extract Firebase ID token

        login_response = res.login(id_token)

        return login_response

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@router.post("/logout", response_model=MessageResponse, responses={401: {"model": ErrorResponse}})
async def logout(authorization: str = Header(...)):

    try:
        token = authorization.split(" ")[1]  # Bearer <token>
        message_response = res.logout(token)

        return message_response

    except TokenExpiredException:
        raise HTTPException(status_code=401, detail="Token has expired")
    except TokenNotValidException:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.post("/validate-token", response_model=UserInfoResponse, responses={401: {"model": ErrorResponse}})
async def validate_token(authorization: str = Header(...)):

    try:
        token = authorization.split(" ")[1]  # Bearer <token>
        user_info = res.validate_token(token)

        return user_info

    except TokenExpiredException:
        raise HTTPException(status_code=401, detail="Token has expired")
    except TokenNotValidException:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")
