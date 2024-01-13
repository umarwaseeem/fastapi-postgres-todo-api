from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.database import  TodoModelDB , get_db
from models.pydantic_models import TodoModelPydantic 
from utils.jwt_util import AuthHandler


auth_handler = AuthHandler()

router = APIRouter(tags=['Todo'])

@router.get("/todos/", summary="Get all todos")
def get_todos(db: Session = Depends(get_db),user_id: str = Depends(auth_handler.get_user_id)):
    db_todos = db.query(TodoModelDB).filter(TodoModelDB.user_id == user_id).all()
    return db_todos

@router.post("/todos/", response_model=TodoModelPydantic)
def create_todo(todo: TodoModelPydantic, db: Session = Depends(get_db),user_id: str = Depends(auth_handler.get_user_id)):
    db_todo = TodoModelDB(
        title=todo.title,
        description=todo.description,
        user_id=user_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.put("/todos/{todo_id}", response_model=TodoModelPydantic)
def update_todo(todo_id: int, updated_todo: TodoModelPydantic, db: Session = Depends(get_db),user_id: str = Depends(auth_handler.get_user_id)):
    db_todo = db.query(TodoModelDB).filter(TodoModelDB.id == todo_id, TodoModelDB.user_id == user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    for key, value in updated_todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    return TodoModelPydantic(**db_todo.dict())

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), user_id: str = Depends(auth_handler.get_user_id)):
    db_todo = db.query(TodoModelDB).filter(TodoModelDB.id == todo_id, TodoModelDB.user_id == user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    db.delete(db_todo)
    db.commit()
    return {"message": f"Todo {todo_id} deleted"}