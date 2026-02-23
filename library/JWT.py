# pip install PyJWT

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.auth_model import UserModel
import jwt
import os

class AUTH_JWT:

    ALGORITHM = "HS256"
    
    @staticmethod
    def CREATE_TOKEN(user: UserModel, minutes: int = 30):
        data = {
            "iPK": user.iPK, 
            "strUserID": user.strUserID, 
            "strName": user.strName, 
            "strEmail": user.strEmail
        }
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes) # 정해진 시간동안 유효한 토큰 생성
        to_encode.update({"exp": expire})
        secret_key = os.getenv("SECRET_KEY")
        return jwt.encode(to_encode, secret_key, algorithm=AUTH_JWT.ALGORITHM)

    @staticmethod
    def TO_USER_MODEL(auth: HTTPAuthorizationCredentials) -> UserModel:
        token = auth.credentials
        try:
            SECRET_KEY = os.getenv("SECRET_KEY")
            payload = jwt.decode(token, SECRET_KEY, algorithms=[AUTH_JWT.ALGORITHM])
            user_model = UserModel(
                iPK=payload.get("iPK"),
                strUserID=payload.get("strUserID"),
                strUserPW="",
                strName=payload.get("strName"),
                strEmail=payload.get("strEmail"),
                strPhone="",
                strAddress="",
                strImageFile=""
            )
            return user_model
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")