from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import SchedulePreparationModel

class SchedulePreparationTable(BaseTable):

    NAME = "schedule_preparation"

    @staticmethod
    def TO_MODEL(row: tuple) -> SchedulePreparationModel:
        return SchedulePreparationModel(
            iPK=row[0],
            iScheduleFK=row[1],
            strName=row[2],
            bCheck=row[3]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[SchedulePreparationModel]:
        return [SchedulePreparationTable.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {SchedulePreparationTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                strName VARCHAR(1024) NOT NULL,
                bCheck BOOLEAN NOT NULL DEFAULT FALSE,
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iScheduleFK) REFERENCES schedule(iPK) ON DELETE CASCADE
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iSchedulePreparationPK: int) -> str:
        return f"SELECT iPK,iScheduleFK,strName,bCheck FROM {SchedulePreparationTable.NAME} WHERE iPK={iSchedulePreparationPK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"SELECT iPK,iScheduleFK,strName,bCheck FROM {SchedulePreparationTable.NAME} WHERE iScheduleFK={iScheduleFK}"

    @staticmethod
    def TO_INSERT_QUERY(spm: SchedulePreparationModel) -> str:
        return f"INSERT INTO {SchedulePreparationTable.NAME} (iScheduleFK,strName) VALUES ({spm.iScheduleFK},'{spm.strName}')"

    @staticmethod
    def TO_UPDATE_QUERY(spm: SchedulePreparationModel) -> str:
        return f"UPDATE {SchedulePreparationTable.NAME} SET bCheck={spm.bCheck} WHERE iPK={spm.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(iSchedulePreparationPK: int) -> str:
        return f"DELETE FROM {SchedulePreparationTable.NAME} WHERE iPK={iSchedulePreparationPK}"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {SchedulePreparationTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, SchedulePreparationTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
