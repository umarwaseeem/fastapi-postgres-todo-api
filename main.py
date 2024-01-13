# 3rd party imports
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
# local imports
from services.database import  TodoModelDB , get_db
from models.pydantic_models import TodoModelPydantic 
from utils.jwt_util import AuthHandler
# router imports
from routes import auth, todo


auth_handler = AuthHandler()
app = FastAPI()

app.include_router(auth.router)
app.include_router(todo.router)

@app.get("/", summary="Root page")
def root():
    return {"message": "TODO API"}

