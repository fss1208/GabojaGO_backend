from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.auth_model import UserModel
from models.schedule_model import ScheduleFrontModel
from database.schedule.schedule_user_table import ScheduleUserTable
from database.schedule_table import ScheduleTable
from database.user_table import UserTable

class ScheduleView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleFrontModel:
        return ScheduleFrontModel(
            iPK=row[0],
            iUserFK=row[1],
            dtDate1=row[2],
            dtDate2=row[3],
            strWhere=row[4],
            strWithWho=row[5],
            strTripStyle=row[6],
            strTransport=row[7],
            nTotalPeople=row[8],
            nTotalBudget=row[9],
            nAlarmRatio=row[10],
            nTransportRatio=row[11],
            nLodgingRatio=row[12],
            nFoodRatio=row[13],
            chStatus=row[14],
            dtCreate=row[15],
            user_model=UserModel(
                iPK=row[16],
                strUserID=row[17],
                strUserPW="",
                strName=row[18],
                strEmail=row[19],
                strPhone="",
                strAddress="",
                strImageFile=""
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleFrontModel]:
        return [ScheduleView.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_SELECT_LIST_QUERY(iUserFK: int, nFilter: int, chStatus: str) -> str:
        strFilter = ""
        if (nFilter == 1): # 내가 생성한 일정
            strFilter = f"(st.iUserFK={iUserFK})"
        elif (nFilter == 2): # 내가 동행한 일정
            strFilter = f"(st.iPK IN (SELECT sut.iScheduleFK FROM {ScheduleUserTable.NAME} AS sut WHERE sut.iUserFK IN ({iUserFK})))"
        else: # (nFilter == 3) 둘 다
            strFilter = f"(st.iUserFK={iUserFK} OR st.iPK IN (SELECT sut.iScheduleFK FROM {ScheduleUserTable.NAME} AS sut WHERE sut.iUserFK IN ({iUserFK})))"
        strStatus = ""
        if (chStatus == 'A'):
            strStatus = f"AND (st.dtDate1 >= CURRENT_DATE() OR st.dtDate2 >= CURRENT_DATE())"
        elif (chStatus == 'B'):
            strStatus = f"AND (st.dtDate1 <= CURRENT_DATE() AND st.dtDate2 >= CURRENT_DATE())"
        elif (chStatus == 'C'):
            strStatus = f"AND st.dtDate2 < CURRENT_DATE()"
        return f"""
            SELECT
               st.iPK,st.iUserFK,st.dtDate1,st.dtDate2,st.strWhere,st.strWithWho,st.strTripStyle,st.strTransport,st.nTotalPeople,st.nTotalBudget,st.nAlarmRatio,st.nTransportRatio,st.nLodgingRatio,st.nFoodRatio,st.chStatus,st.dtCreate,
               ut.iPK,ut.strUserID,ut.strName,ut.strEmail
            FROM {ScheduleTable.NAME} AS st 
            JOIN {UserTable.NAME} AS ut ON st.iUserFK = ut.iPK
            WHERE {strFilter} {strStatus}
            ORDER BY st.dtCreate"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, ScheduleView.TO_SELECT_LIST_QUERY(1, 3, 'C'))
            rows_tuple = cursor.fetchall()
            front_list = ScheduleView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)

