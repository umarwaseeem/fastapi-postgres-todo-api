import traceback
from jose import jwt, ExpiredSignatureError
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv
load_dotenv()

class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = os.environ.get('JWT_SECRET_KEY')
    algorithm = os.environ.get('JWT_ALGORITHM')

    def __init__(self):
        if not self.secret or not self.algorithm:
            raise EnvironmentError("JWT_SECRET_KEY or JWT_ALGORITHM not found in environment variables")

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id: str):
        # encoded_id = user_id.copy()
        expiration_time = datetime.utcnow() + timedelta(minutes=30)
        payload = {
            'exp': expiration_time,
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm
        )

    # def encode_refresh_token(self, user_id: str):
    #     # encoded_id = user_id.copy()
    #     expiration_time = datetime.utcnow() + timedelta(minutes=120)
    #     payload = {
    #         'exp': expiration_time,
    #         'iat': datetime.utcnow(),
    #         'sub': user_id
    #     }
    #     return jwt.encode(
    #         payload,
    #         self.secret,
    #         algorithm=self.algorithm
    #     )

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token=token, key=self.secret, algorithms=[self.algorithm])
            id: str = payload.get('sub')
            print(id)
            return id
        except ExpiredSignatureError as e:
            print(e)
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Signature has expired")
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise HTTPException(status_code=401, detail="Invalid token")

    def get_user_id(self, auth: HTTPAuthorizationCredentials = Security(security)) -> str:
        return self.decode_token(auth.credentials)
