from fastapi import  HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from services.database import  UserModelDB, get_db
from models.pydantic_models import UserModelPydantic, FormLoginSchema, SignupResponseModel,LoginResponseModel
from utils.jwt_util import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(tags=['Authentication'])


@router.post("/signup/", summary="Create new user", response_model=SignupResponseModel)
async def signup_user(data: UserModelPydantic, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(UserModelDB).filter(UserModelDB.email == data.email).first()

    # If user with a particular email already exists, raise an exception
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create a new user
    new_user = UserModelDB(
        username=data.username,
        email=data.email,
        password_hash=auth_handler.get_password_hash(data.password),
    )

    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the updated user from the database

    return SignupResponseModel(
        user_id=new_user.user_id,
    )


@router.post('/login/', summary="Login and create token for user", response_model=LoginResponseModel)
async def login(form_data: FormLoginSchema, db: Session = Depends(get_db)):
    
    # Check if user exists
    user = db.query(UserModelDB).filter(UserModelDB.email == form_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    # Check if password is correct for existing user
    hashed_pass = user.password_hash 
    if not auth_handler.verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    # Return access, refresh tokens and user_id
    return LoginResponseModel(
        access_token=auth_handler.encode_token(str(user.user_id)),
    )