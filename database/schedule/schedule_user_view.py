from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.auth_model import UserModel
from models.schedule_model import ScheduleUserModel, ScheduleUserFrontModel
from database.schedule.schedule_user_table import ScheduleUserTable
from database.user_table import UserTable

class ScheduleUserView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleUserFrontModel:
        return ScheduleUserFrontModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iUserFK=row[2],
            dtCreate=row[3],
            user=UserModel(
                iPK=row[4],
                strUserID=row[5],
                strUserPW="",
                strName=row[6],
                strEmail=row[7]
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleUserFrontModel]:
        return [ScheduleUserView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"""
            SELECT
               sut.iPK,sut.iScheduleFK,sut.iUserFK,sut.dtCreate,
               ut.iPK,ut.strUserID,ut.strName,ut.strEmail
            FROM {ScheduleUserTable.NAME} AS sut 
            JOIN {UserTable.NAME} AS ut ON sut.iUserFK = ut.iPK
            WHERE sut.iScheduleFK = {iScheduleFK}
            ORDER BY sut.dtCreate"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, ScheduleUserView.TO_SELECT_LIST_QUERY(61))
            rows_tuple = cursor.fetchall()
            front_list = ScheduleUserView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)

