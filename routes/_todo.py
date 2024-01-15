from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services._database import  TodoModelDB , get_db
from models._pydantic_models import TodoModelPydantic ,TodoResponseModelPydantic
from utils._jwt_util import AuthHandler


auth_handler = AuthHandler()

router = APIRouter(tags=['Todo'])

@router.get("/todos/", summary="Get all todos for authenticated user", response_model=list[TodoResponseModelPydantic])
def get_todos(db: Session = Depends(get_db), user_id: str = Depends(auth_handler.get_user_id)):
    db_todos = db.query(TodoModelDB).filter(TodoModelDB.user_id == user_id).order_by(TodoModelDB.id).all()
    return db_todos

@router.post("/todos/", response_model=TodoResponseModelPydantic, summary="Create a new todo")
def create_todo(todo: TodoModelPydantic, db: Session = Depends(get_db),user_id: str = Depends(auth_handler.get_user_id)):
    db_todo = TodoModelDB(
        title=todo.title,
        description=todo.description,
        user_id=user_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    new_todo = TodoResponseModelPydantic(
        id=db_todo.id,
        title=db_todo.title,
        description=db_todo.description
    )
    return new_todo

@router.put("/todos/{todo_id}", response_model=TodoResponseModelPydantic, summary="Update a todo")
def update_todo(todo_id: int, updated_todo: TodoModelPydantic, db: Session = Depends(get_db),user_id: str = Depends(auth_handler.get_user_id)):
    db_todo = db.query(TodoModelDB).filter(TodoModelDB.id == todo_id, TodoModelDB.user_id == user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    for key, value in updated_todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()

    updated_todo = TodoResponseModelPydantic(
        id=db_todo.id,
        title=db_todo.title,
        description=db_todo.description
    )

    return updated_todo

@router.delete("/todos/{todo_id}", summary="Delete a todo")
def delete_todo(todo_id: int, db: Session = Depends(get_db), user_id: str = Depends(auth_handler.get_user_id)):
    db_todo = db.query(TodoModelDB).filter(TodoModelDB.id == todo_id, TodoModelDB.user_id == user_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    db.delete(db_todo)
    db.commit()
    return {"message": f"Todo {todo_id} deleted"}