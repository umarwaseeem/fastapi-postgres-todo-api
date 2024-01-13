from fastapi import FastAPI
from utils._jwt_util import AuthHandler
from routes import _auth, _todo

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



