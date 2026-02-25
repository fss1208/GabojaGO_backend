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
            strTransport=row[6],
            nTotalPeople=row[7],
            nTotalBudget=row[8],
            nAlarmRatio=row[9],
            nTransportRatio=row[10],
            nLodgingRatio=row[11],
            nFoodRatio=row[12],
            chStatus=row[13],
            dtCreate=row[14]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuples: tuple) -> list[ScheduleModel]:
        return [ScheduleTable.TO_MODEL(row) for row in rows_tuples]

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
    def TO_SELECT_MODEL_QUERY(sm: ScheduleModel) -> str:
        return f"SELECT * FROM {ScheduleTable.NAME} WHERE iPK={sm.iPK}"

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
        return f"INSERT INTO {ScheduleTable.NAME} (iUserFK,dtDate1,dtDate2,strWhere,strWithWho,strTransport,nTotalPeople,nTotalBudget,nAlarmRatio,nTransportRatio,nLodgingRatio,nFoodRatio,chStatus) " + \
            f"VALUES ({sm.iUserFK},'{sm.dtDate1}','{sm.dtDate2}','{sm.strWhere}','{sm.strWithWho}','{sm.strTransport}',{sm.nTotalPeople},{sm.nTotalBudget},{sm.nAlarmRatio},{sm.nTransportRatio},{sm.nLodgingRatio},{sm.nFoodRatio},'{sm.chStatus}')"

    @staticmethod
    def TO_UPDATE_QUERY(sm: ScheduleModel) -> str:
        return f"""UPDATE {ScheduleTable.NAME} 
                    SET dtDate1='{sm.dtDate1}',dtDate2='{sm.dtDate2}',strWhere='{sm.strWhere}',strWithWho='{sm.strWithWho}',strTransport='{sm.strTransport}',nTotalPeople={sm.nTotalPeople},nTotalBudget={sm.nTotalBudget},nAlarmRatio={sm.nAlarmRatio},nTransportRatio={sm.nTransportRatio},nLodgingRatio={sm.nLodgingRatio},nFoodRatio={sm.nFoodRatio},chStatus='{sm.chStatus}' 
                    WHERE iPK={sm.iPK}"""

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
