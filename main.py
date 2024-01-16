from fastapi import Depends, FastAPI
from utils._jwt_util import AuthHandler
from routes import _auth, _todo
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from services._database import  get_db, UserModelDB

auth_handler = AuthHandler()
app = FastAPI(
    docs_url="/",
    title="Todo API With Postgres, SQLAlchemy, FastAPI and JWT Authentication",
    description="""
    This is a simple todo API with CRUD operations to demonstrate the use of FastAPI with SQLAlchemy and Postgres.
    \nCan easily be integrated with a front end application.
    """,
)

app.include_router(_auth.router)
app.include_router(_todo.router)

@app.get("/users", tags=["Users"])
async def get_users(db: Session = Depends(get_db)):
    usernames = db.query(UserModelDB.username).all()
    return [username[0] for username in usernames]

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://todo-manage-app.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




