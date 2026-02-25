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
            dtSchedule=row[2],
            strMemo=row[3],
            location=LocationModel(
                iPK=row[4],
                strName=row[5],
                strGroupCode=row[6],
                strGroupName=row[7],
                strGroupDetail=row[8],
                strAddress=row[9],
                strPhone=row[10],
                strLink=row[11],
                chCategory=row[12],
                ptLongitude=str(row[13]),
                ptLatitude=str(row[14])
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[ScheduleLocationFrontModel]:
        return [ScheduleLocationView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iScheduleFK: int) -> str:
        return f"""
            SELECT
               slt.iPK,slt.iScheduleFK,slt.dtSchedule,slt.strMemo,
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
            rows_tuples = cursor.fetchall()
            front_list = ScheduleLocationView.TO_MODEL_LIST(rows_tuples)
            for front_model in front_list:
                print(front_model)

