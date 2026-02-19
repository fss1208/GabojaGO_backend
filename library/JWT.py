# pip install PyJWT

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.auth_model import UserModel
import jwt
import os

class AuthJWT:

    ALGORITHM = "HS256"
    
    @staticmethod
    def create_token(user: UserModel, minutes: int = 30):
        data = {
            "pk": user.pk, 
            "id": user.id, 
            "name": user.name, 
            "email": user.email, 
            "phone": user.phone, 
            "address": user.address, 
            "image_file": user.image_file
        }
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes) # 정해진 시간동안 유효한 토큰 생성
        to_encode.update({"exp": expire})
        secret_key = os.getenv("SECRET_KEY")
        return jwt.encode(to_encode, secret_key, algorithm=AuthJWT.ALGORITHM)

    @staticmethod
    def get_user_model(auth: HTTPAuthorizationCredentials) -> UserModel:
        token = auth.credentials
        try:
            SECRET_KEY = os.getenv("SECRET_KEY")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[AuthJWT.ALGORITHM])
            user_model = UserModel(
                pk=payload.get("pk"),
                id=payload.get("id"),
                pw="***************",
                name=payload.get("name"),
                email=payload.get("email"),
                phone=payload.get("phone"),
                address=payload.get("address"),
                image_file=payload.get("image_file")
            )
            return user_model
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")