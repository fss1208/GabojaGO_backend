from models.auth_model import UserModel, LoginRequestModel
from library.DB import DB, BaseTable
import logging

class UserTable(BaseTable):

    NAME = "user"

    @staticmethod
    def TO_MODEL(row: tuple) -> UserModel:
        return UserModel(
            iPK=row[0],
            strUserID=row[1],
            strUserPW=row[2],
            strName=row[3],
            strEmail=row[4],
            strPhone=row[5],
            strAddress=row[6],
            strImageFile=row[7]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[UserModel]:
        user_model_list = [UserTable.TO_MODEL(row) for row in rows_tuple]
        for user_model in user_model_list:
            user_model.strUserPW = ""
            user_model.strPhone = ""
            user_model.strAddress = ""
            user_model.strImageFile = ""
        return user_model_list

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {UserTable.NAME} (
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
    def TO_SELECT_LOGIN_QUERY(lrm: LoginRequestModel) -> str:
        return f"SELECT * FROM {UserTable.NAME} WHERE strUserID='{lrm.strUserID.strip()}' AND strUserPW='{lrm.strUserPW.strip()}'"
    
    @staticmethod
    def TO_SELECT_MODEL_QUERY(strUserID: str) -> str:
        return f"SELECT * FROM {UserTable.NAME} WHERE strUserID='{strUserID}'"

    @staticmethod
    def TO_SELECT_SUB_QUERY(query: str) -> str:
        return f"SELECT * FROM {UserTable.NAME} WHERE iPK IN ({query})"

    @staticmethod
    def TO_SELECT_NAME_QUERY(strUserName: str) -> str:
        return f"SELECT * FROM {UserTable.NAME} WHERE strName LIKE '%{strUserName}%'"

    @staticmethod
    def TO_INSERT_QUERY(um: UserModel) -> str:
        return f"INSERT INTO {UserTable.NAME} (strUserID,strUserPW,strName,strEmail,strPhone,strAddress,strImageFile) " + \
               f"VALUES ('{um.strUserID}','{um.strUserPW}','{um.strName}','{um.strEmail}','{um.strPhone}','{um.strAddress}','{um.strImageFile}')"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {UserTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, UserTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)