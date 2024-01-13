import traceback
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Todo , UserModelDB
from pydantic_models import TodoCreate , UserModel, FormLoginSchema, SignupResponseModel
from utils import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

app = FastAPI()

##### DEPENDENCIES #####
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

##### ROOT PAGE #####

@app.get("/", summary="Root page")
def root():
    return {"message": "TODO API"}


##### AUTHENTICATION #####

@app.post("/signup/", summary="Create new user", response_model=SignupResponseModel)
async def signup_user(data: UserModel, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(UserModelDB).filter(UserModelDB.email == data.email).first()

        # If user with a particular email already exists, raise an exception
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        print("1111")
        # Create a new user
        new_user = UserModelDB(
            username=data.username,
            email=data.email,
            password_hash=get_hashed_password(data.password),
        )

        print("2222")

        # Save the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Refresh to get the updated user from the database

        return {
            "access_token": create_access_token(new_user.email),  # Accessing the 'email' attribute
            "refresh_token": create_refresh_token(new_user.email),  # Accessing the 'email' attribute
        }
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        )

@app.post('/login/', summary="Login and create access and refresh tokens for user")
async def login(form_data: FormLoginSchema, db: Session = Depends(get_db)):
    user = db.query(UserModelDB).filter(UserModelDB.email == form_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    hashed_pass = user.password_hash  # Accessing the 'password' attribute using dot notation
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "message": "Logged in successfully",
    }


##### USER TODOS HANDLING #####

@app.get("/todos/", summary="Get all todos")
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

@app.post("/todos/", response_model=TodoCreate)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{todo_id}", response_model=TodoCreate)
def update_todo(todo_id: int, updated_todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in updated_todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    return TodoCreate(**db_todo.dict())

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": f"Todo {todo_id} deleted"}