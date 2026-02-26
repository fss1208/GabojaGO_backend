from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.location_model import LocationModel
from models.schedule_model import ScheduleLocationModel, ScheduleLocationFrontModel
from database.schedule.schedule_location_table import ScheduleLocationTable
from database.location_table import LocationTable

class ScheduleLocationView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> ScheduleLocationFrontModel:
        return ScheduleLocationFrontModel(
            iPK=row[0],
            iScheduleFK=row[1],
            iLocationFK=row[2],
            dtSchedule=row[3],
            strMemo=row[4],
            location=LocationModel(
                iPK=row[5],
                strName=row[6],
                strGroupCode=row[7],
                strGroupName=row[8],
                strGroupDetail=row[9],
                strAddress=row[10],
                strPhone=row[11],
                strLink=row[12],
                chCategory=row[13],
                ptLongitude=str(row[14]),
                ptLatitude=str(row[15])
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleLocationFrontModel]:
        return [ScheduleLocationView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iScheduleFK: int) -> str:
        return f"""
            SELECT
               slt.iPK,slt.iScheduleFK,slt.iLocationFK,slt.dtSchedule,slt.strMemo,
               lt.iPK,lt.strName,lt.strGroupCode,lt.strGroupName,lt.strGroupDetail,lt.strAddress,lt.strPhone,lt.strLink,lt.chCategory,ST_X(lt.ptLongLat),ST_Y(lt.ptLongLat)
            FROM {ScheduleLocationTable.NAME} AS slt
            JOIN {LocationTable.NAME} AS lt ON slt.iLocationFK = lt.iPK
            WHERE slt.iScheduleFK = {iScheduleFK}
            ORDER BY slt.dtSchedule"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, ScheduleLocationView.TO_SELECT_MODEL_QUERY(1))
            rows_tuple = cursor.fetchall()
            front_list = ScheduleLocationView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)

