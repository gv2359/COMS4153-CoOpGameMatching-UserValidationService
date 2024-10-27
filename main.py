# main.py
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from Registration import router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.include_router(router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)