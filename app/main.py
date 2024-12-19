
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.resources.user_login_resource import UserLoginResource

# it loads from the .env file
load_dotenv()

from app.routers import user_login

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_login.router)

@app.get("/health")
async def health():
    return {"message": "Service is up and running"}

if __name__ == "__main__":
    uvicorn.run(app, port=8001)
