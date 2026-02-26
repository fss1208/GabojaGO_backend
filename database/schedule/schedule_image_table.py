from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.schedule_model import ScheduleImageModel, ScheduleImageFrontModel

class ScheduleImageTable(BaseTable):

    NAME = "schedule_image"

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleImageFrontModel:
        return ScheduleImageFrontModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iUserFK=row[2],
            iLocationPK=row[3],
            dtImage=row[4],
            ptLongitude=str(row[5]),
            ptLatitude=str(row[6]),
            strFile=row[7],
            location=None
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleImageFrontModel]:
        return [ScheduleImageTable.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ScheduleImageTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iScheduleFK INT NOT NULL,
                iUserFK INT NOT NULL,
                iLocationPK INT DEFAULT 0,
                dtImage DATETIME NOT NULL,
                ptLongLat POINT NOT NULL,
                strFile VARCHAR(1024) NOT NULL,
                FOREIGN KEY (iScheduleFK) REFERENCES schedule(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iUserFK) REFERENCES user(iPK),
                SPATIAL INDEX(ptLongLat)
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iPK: int) -> str:
        return f"SELECT iPK,iScheduleFK,iUserFK,iLocationPK,dtImage,ST_X(ptLongLat),ST_Y(ptLongLat),strFile FROM {ScheduleImageTable.NAME} WHERE iPK={iPK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"SELECT iPK,iScheduleFK,iUserFK,iLocationPK,dtImage,ST_X(ptLongLat),ST_Y(ptLongLat),strFile FROM {ScheduleImageTable.NAME} WHERE iScheduleFK={iScheduleFK}"

    @staticmethod
    def TO_INSERT_QUERY(sim: ScheduleImageModel) -> str:
        return f"INSERT INTO {ScheduleImageTable.NAME} (iScheduleFK,iUserFK,iLocationPK,dtImage,ptLongLat,strFile) " + \
               f"VALUES ({sim.iScheduleFK},{sim.iUserFK},{sim.iLocationPK},'{sim.dtImage}',{DB.TO_POINT(sim.ptLongitude,sim.ptLatitude)},'{sim.strFile}')"

    @staticmethod
    def TO_UPDATE_QUERY(sim: ScheduleImageModel) -> str:
        return f"UPDATE {ScheduleImageTable.NAME} SET iLocationPK={sim.iLocationPK},dtImage='{sim.dtImage}' WHERE iPK={sim.iPK}"

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
