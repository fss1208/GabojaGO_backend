from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.location_model import LocationModel
from models.favorite_model import FavoriteLocationFrontModel
from database.favorite.favorite_location_table import FavoriteLocationTable
from database.location_table import LocationTable

class FavoriteLocationView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> FavoriteLocationFrontModel:
        return FavoriteLocationFrontModel(
            iPK=row[0],
            iFavoriteFK=row[1],
            iLocationFK=row[2],
            location=LocationModel(
                iPK=row[3],
                strName=row[4],
                strGroupCode=row[5],
                strGroupName=row[6],
                strGroupDetail=row[7],
                strAddress=row[8],
                strPhone=row[9],
                strLink=row[10],
                chCategory=row[11],
                ptLongitude=str(row[12]),
                ptLatitude=str(row[13])
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[FavoriteLocationFrontModel]:
        return [FavoriteLocationView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_LIST_QUERY(iFavoritePK: int) -> str:
        return f"""
            SELECT
               flt.iPK,flt.iFavoriteFK,flt.iLocationFK,
               lt.iPK,lt.strName,lt.strGroupCode,lt.strGroupName,lt.strGroupDetail,lt.strAddress,lt.strPhone,lt.strLink,lt.chCategory,ST_X(lt.ptLongLat),ST_Y(lt.ptLongLat)
            FROM {FavoriteLocationTable.NAME} AS flt
            JOIN {LocationTable.NAME} AS lt ON flt.iLocationFK = lt.iPK
            WHERE flt.iFavoriteFK = {iFavoritePK}"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, FavoriteLocationView.TO_SELECT_MODEL_QUERY(1))
            rows_tuple = cursor.fetchall()
            front_list = FavoriteLocationView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)
