from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import ScheduleLocationModel

class ScheduleLocationTable(BaseTable):

    NAME = "schedule_location"

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleLocationModel:
        return ScheduleLocationModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iLocationFK=row[2],
            dtSchedule=row[3],
            strMemo=row[4]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleLocationTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                iLocationFK BIGINT UNSIGNED NOT NULL,
                dtSchedule DATETIME,
                strMemo VARCHAR(1024),
                FOREIGN KEY (iScheduleFK) REFERENCES schedule(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iLocationFK) REFERENCES location(iPK)
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(slm: ScheduleLocationModel) -> str:
        return f"SELECT * FROM {ScheduleLocationTable.NAME} WHERE iPK={slm.iPK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"SELECT * FROM {ScheduleLocationTable.NAME} WHERE iScheduleFK={iScheduleFK} ORDER BY dtSchedule"

    @staticmethod
    def TO_INSERT_QUERY(slm: ScheduleLocationModel) -> str:
        return f"INSERT INTO {ScheduleLocationTable.NAME} (iScheduleFK,iLocationFK,dtSchedule,strMemo) " + \
               f"VALUES ({slm.iScheduleFK},{slm.iLocationFK},'{slm.dtSchedule}','{slm.strMemo}')"

    @staticmethod
    def TO_UPDATE_QUERY(slm: ScheduleLocationModel) -> str:
        return f"UPDATE {ScheduleLocationTable.NAME} SET dtSchedule='{slm.dtSchedule}',strMemo='{slm.strMemo}' WHERE iPK={slm.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(nScheduleLocationPK: int) -> str:
        return f"DELETE FROM {ScheduleLocationTable.NAME} WHERE iPK={nScheduleLocationPK}"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {ScheduleLocationTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ScheduleLocationTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
