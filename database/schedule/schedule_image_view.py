from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.image_model import ImageModel
from models.schedule_model import ScheduleImageModel, ScheduleImageFrontModel
from database.schedule.schedule_image_table import ScheduleImageTable
from database.image_table import ImageTable

class ScheduleImageView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleImageFrontModel:
        return ScheduleImageFrontModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iImageFK=row[2],
            image=ImageModel(
                iPK=row[3],
                iUserFK=row[4],
                iLocationPK=row[5],
                strFile=row[6],
                dtImage=row[7],
                ptLongitude=str(row[8]),
                ptLatitude=str(row[9]),
                dtCreate=row[10]
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleImageFrontModel]:
        return [ScheduleImageView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_LIST_QUERY(iScheduleFK: int) -> str:
        return f"""
            SELECT
               sit.iPK,sit.iScheduleFK,sit.iImageFK,
               it.iPK,it.iUserFK,it.iLocationPK,it.strFile,it.dtImage,ST_X(it.ptLongLat),ST_Y(it.ptLongLat),it.dtCreate
            FROM {ScheduleImageTable.NAME} AS sit 
            JOIN {ImageTable.NAME} AS it ON sit.iImageFK = it.iPK
            WHERE sit.iScheduleFK = {iScheduleFK}
            ORDER BY it.dtImage"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, ScheduleImageView.TO_SELECT_MODEL_QUERY(1))
            rows_tuple = cursor.fetchall()
            front_list = ScheduleImageView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)

