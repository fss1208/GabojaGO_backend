from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable

class LoginRequestModel(BaseModel):
    id: str = Field(..., min_length=3, max_length=255, example="KSH")
    pw: str = Field(..., min_length=3, max_length=255, example="123")

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

    def check_validation(self):
        # if (self.id is None or self.pw is None or self.name is None or self.email is None or self.phone is None or self.address is None):
        #     return False
        return True

class UserTable(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> UserModel:
        return UserModel(
            pk=row[0],
            id=row[1],
            pw=row[2],
            name=row[3],
            email=row[4],
            phone=row[5],
            address=row[6],
            image_file=row[7]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
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

    @staticmethod
    def TO_SELECT_LOGIN_QUERY(login_model: LoginRequestModel) -> str:
        return f"SELECT * FROM user WHERE strUserID='{login_model.id.strip()}' AND strUserPW='{login_model.pw.strip()}'"
    
    @staticmethod
    def TO_SELECT_MODEL_QUERY(user_model: UserModel) -> str:
        return "SELECT * FROM user WHERE strUserID='{0}'".format(user_model.id)

    @staticmethod
    def TO_INSERT_QUERY(user_model: UserModel) -> str:
        return "INSERT INTO user (strUserID,strUserPW,strName,strEmail,strPhone,strAddress,strImageFile) " + \
                        f"VALUES ('{user_model.id}','{user_model.pw}','{user_model.name}','{user_model.email}','{user_model.phone}','{user_model.address}','{user_model.image_file}')"

####################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, "DROP TABLE IF EXISTS user")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, UserTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)