from pydantic import BaseModel, Field
from typing import Optional
import logging

class LoginRequestModel(BaseModel):
    id: str = Field(..., min_length=3, max_length=255, example="KSH")
    pw: str = Field(..., min_length=3, max_length=255, example="123")

    def check_query(self):
        return f"SELECT * FROM user WHERE strUserID='{self.id.strip()}' AND strUserPW='{self.pw.strip()}'"

class LoginResponseModel(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    token_type: str = Field(..., example="bearer")

class UserModel(BaseModel):
    pk: Optional[int] = Field(0, example="0")
    id: str = Field(..., example="KSH")
    pw: str = Field(..., example="123")
    name: str = Field(..., example="김성호")
    email: str = Field(..., example="KSH@gmail.com")
    phone: Optional[str] = Field(None, example="010-1234-5678")
    address: Optional[str] = Field(None, example="서울특별시 도봉구")
    image_file: Optional[str] = Field(None, example="/profile/ksh.jpg")

    def __init__(self, row: tuple = None, **kwargs):
        if row is not None and isinstance(row, tuple):
            data = {
                "pk": row[0],
                "id": row[1],
                "pw": row[2],
                "name": row[3],
                "email": row[4],
                "phone": row[5],
                "address": row[6],
                "image_file": row[7]
            }
            super().__init__(**data)
        else:
            super().__init__(**kwargs)

    def check_validation(self):
        # if (self.id is None or self.pw is None or self.name is None or self.email is None or self.phone is None or self.address is None):
        #     return False
        return True

    @staticmethod
    def CREATE_TABLE() -> str:
        return """
            CREATE TABLE user (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                strUserID VARCHAR(255) NOT NULL UNIQUE,
                strUserPW VARCHAR(255) NOT NULL,
                strName VARCHAR(255) NOT NULL,
                strEmail VARCHAR(255) NOT NULL,
                strPhone VARCHAR(255),
                strAddress VARCHAR(255),
                strImageFile VARCHAR(255),
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""
    
    def select_query(self) -> str:
        return f"SELECT * FROM user WHERE strUserID='{self.id}'"

    def insert_query(self) -> str:
        return "INSERT INTO user (strUserID, strUserPW, strName, strEmail, strPhone, strAddress, strImageFile) " + \
                        f"VALUES ('{self.id}', '{self.pw}', '{self.name}', '{self.email}', '{self.phone}', '{self.address}', '{self.image_file}')"

####################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DATABASE
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DATABASE.CONNECT() as connection:
        with connection.cursor() as cursor:
            DATABASE.SHOW_TABLES(cursor)
            DATABASE.EXECUTE(cursor, "DROP TABLE IF EXISTS user")
            DATABASE.SHOW_TABLES(cursor)
            DATABASE.EXECUTE(cursor, UserModel.CREATE_TABLE())
            DATABASE.SHOW_TABLES(cursor)