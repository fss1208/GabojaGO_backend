from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import ScheduleModel

class ScheduleTable(BaseTable):

    NAME = "schedule"

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleModel:
        return ScheduleModel(
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
            dtCreate=row[15]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleModel]:
        return [ScheduleTable.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iUserFK INT NOT NULL,
                dtDate1 DATE NOT NULL,
                dtDate2 DATE NOT NULL,
                strWhere VARCHAR(128) NOT NULL,
                strWithWho VARCHAR(128) NOT NULL,
                strTripStyle VARCHAR(128) NOT NULL,
                strTransport VARCHAR(128) NOT NULL,
                nTotalPeople TINYINT UNSIGNED, 
                nTotalBudget INT UNSIGNED DEFAULT 0,
                nAlarmRatio TINYINT UNSIGNED DEFAULT 25,
                nTransportRatio TINYINT UNSIGNED DEFAULT 25,
                nLodgingRatio TINYINT UNSIGNED DEFAULT 25,
                nFoodRatio TINYINT UNSIGNED DEFAULT 25,
                chStatus CHAR(1) NOT NULL DEFAULT 'A',
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iUserFK) REFERENCES user(iPK)
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iSchedulePK: int) -> str:
        return f"SELECT * FROM {ScheduleTable.NAME} WHERE iPK={iSchedulePK}"

    @staticmethod
    def TO_SELECT_CREATE_USER_QUERY(iSchedulePK: int, iUserFK: int) -> str:
        return f"SELECT iUserFK FROM {ScheduleTable.NAME} WHERE iPK={iSchedulePK} AND iUserFK={iUserFK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iUserFK: int, chStatus: str) -> str:
        if (chStatus == 'A'):
            return f"SELECT * FROM {ScheduleTable.NAME} WHERE iUserFK={iUserFK} AND (dtDate1 >= CURRENT_DATE() OR dtDate2 >= CURRENT_DATE())"
        elif (chStatus == 'B'):
            return f"SELECT * FROM {ScheduleTable.NAME} WHERE iUserFK={iUserFK} AND (dtDate1 <= CURRENT_DATE() AND dtDate2 >= CURRENT_DATE())"
        elif (chStatus == 'C'):
            return f"SELECT * FROM {ScheduleTable.NAME} WHERE iUserFK={iUserFK} AND dtDate2 < CURRENT_DATE()"
        else:
            return f"SELECT * FROM {ScheduleTable.NAME} WHERE iUserFK={iUserFK}"
    
    @staticmethod
    def TO_INSERT_QUERY(sm: ScheduleModel) -> str:
        return f"INSERT INTO {ScheduleTable.NAME} (iUserFK,dtDate1,dtDate2,strWhere,strWithWho,strTripStyle,strTransport,nTotalPeople,nTotalBudget,nAlarmRatio,nTransportRatio,nLodgingRatio,nFoodRatio,chStatus) " + \
               f"VALUES ({sm.iUserFK},'{sm.dtDate1}','{sm.dtDate2}','{sm.strWhere}','{sm.strWithWho}','{sm.strTripStyle}','{sm.strTransport}',{sm.nTotalPeople},{sm.nTotalBudget},{sm.nAlarmRatio},{sm.nTransportRatio},{sm.nLodgingRatio},{sm.nFoodRatio},'{sm.chStatus}')"

    @staticmethod
    def TO_UPDATE_QUERY(sm: ScheduleModel) -> str:
        return f"UPDATE {ScheduleTable.NAME} " + \
               f"SET dtDate1='{sm.dtDate1}',dtDate2='{sm.dtDate2}',strWhere='{sm.strWhere}',strWithWho='{sm.strWithWho}',strTripStyle='{sm.strTripStyle}',strTransport='{sm.strTransport}',nTotalPeople={sm.nTotalPeople},nTotalBudget={sm.nTotalBudget},nAlarmRatio={sm.nAlarmRatio},nTransportRatio={sm.nTransportRatio},nLodgingRatio={sm.nLodgingRatio},nFoodRatio={sm.nFoodRatio},chStatus='{sm.chStatus}' " + \
               f"WHERE iPK={sm.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(iSchedulePK: int) -> str:
        return f"DELETE FROM {ScheduleTable.NAME} WHERE iPK={iSchedulePK}" 

#############################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {ScheduleTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ScheduleTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
