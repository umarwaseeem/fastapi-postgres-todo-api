from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    description: str

class UserModel(BaseModel):
    username: str
    password: str
    email: str

class FormLoginSchema(BaseModel):
    email   : str
    password: str

class SignupResponseModel(BaseModel):
    access_token : str
    refresh_token: str