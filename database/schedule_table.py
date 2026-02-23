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
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iUserFK INT NOT NULL,
                dtDate1 DATE NOT NULL,
                dtDate2 DATE NOT NULL,
                strWhere VARCHAR(128) NOT NULL,                     -- ex: 제주도,경주,부산
                strWithWho VARCHAR(128) NOT NULL,
                strTransport VARCHAR(128) NOT NULL,
                nTotalPeople TINYINT UNSIGNED, 
                nTotalBudget INT UNSIGNED DEFAULT 0,
                nAlarmRatio TINYINT UNSIGNED DEFAULT 25,            -- 알람 비율
                nTransportRatio TINYINT UNSIGNED DEFAULT 25,        -- 교통비 비율
                nLodgingRatio TINYINT UNSIGNED DEFAULT 25,          -- 숙박비 비율
                nFoodRatio TINYINT UNSIGNED DEFAULT 25,             -- 식비 비율
                chStatus CHAR(1) NOT NULL DEFAULT 'P',              -- P:준비, A:여행중, C:완료
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iUserFK) REFERENCES user(iPK)
            );
        """

    @staticmethod
    def TO_SELECT_MODEL_QUERY(sm: ScheduleModel) -> str:
        return f"SELECT * FROM {ScheduleTable.NAME} WHERE iPK={sm.iPK}"
    
    @staticmethod
    def TO_INSERT_QUERY(sm: ScheduleModel) -> str:
        return f"INSERT INTO {ScheduleTable.NAME} (iUserFK,dtDate1,dtDate2,strWhere,strWithWho,strTransport,nTotalPeople,nTotalBudget,nAlarmRatio,nTransportRatio,nLodgingRatio,nFoodRatio,chStatus) " + \
            f"VALUES ({sm.iUserFK},'{sm.dtDate1}','{sm.dtDate2}','{sm.strWhere}','{sm.strWithWho}','{sm.strTransport}',{sm.nTotalPeople},{sm.nTotalBudget},{sm.nAlarmRatio},{sm.nTransportRatio},{sm.nLodgingRatio},{sm.nFoodRatio},'{sm.chStatus}')"


####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, "DROP TABLE IF EXISTS schedule")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ScheduleTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
