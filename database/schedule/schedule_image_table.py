from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import ScheduleImageModel, ScheduleImageModel

class ScheduleImageTable(BaseTable):

    NAME = "schedule_image"
    MODEL_COLUMNS = "iPK,iScheduleFK,iImageFK"

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleImageModel:
        return ScheduleImageModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iImageFK=row[2]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleImageTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                iImageFK INT NOT NULL,
                FOREIGN KEY (iScheduleFK) REFERENCES schedule(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iImageFK) REFERENCES image(iPK) ON DELETE CASCADE
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iScheduleImagePK: int) -> str:
        return f"SELECT {ScheduleImageTable.MODEL_COLUMNS} FROM {ScheduleImageTable.NAME} WHERE iPK={iScheduleImagePK}"

    @staticmethod
    def TO_INSERT_QUERY(iScheduleFK: int, iImageFK: int) -> str:
        return f"INSERT INTO {ScheduleImageTable.NAME} (iScheduleFK,iImageFK) VALUES ({iScheduleFK},{iImageFK})"

    @staticmethod
    def TO_DELETE_QUERY(iScheduleImagePK: int) -> str:
        return f"DELETE FROM {ScheduleImageTable.NAME} WHERE iPK={iScheduleImagePK}"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {ScheduleImageTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ScheduleImageTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
