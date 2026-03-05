from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.location_model import LocationModel, LocationReviewFrontModel
from database.location.location_review_table import LocationReviewTable
from database.location_table import LocationTable

# 미사용 (LocationReviewTable 사용)
class LocationReviewView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> LocationReviewFrontModel:
        return LocationReviewFrontModel(
            iPK=row[0],
            iLocationFK=row[1],
            iUserFK=row[2],
            nScore=row[3],
            bRevisit=row[4],
            strReview=row[5],
            dtCreate=row[6],
            location=LocationModel(
                iPK=row[7],
                strName=row[8],
                strGroupCode=row[9],
                strGroupName=row[10],
                strGroupDetail=row[11],
                strAddress=row[12],
                strPhone=row[13],
                strLink=row[14],
                chCategory=row[15],
                ptLongitude=str(row[16]),
                ptLatitude=str(row[17])
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[LocationReviewFrontModel]:
        return [LocationReviewView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iLocationPK: int) -> str:
        return f"""
            SELECT
               lrt.iPK,lrt.iLocationFK,lrt.iUserFK,lrt.nScore,lrt.bRevisit,lrt.strReview,lrt.dtCreate,
               lt.iPK,lt.strName,lt.strGroupCode,lt.strGroupName,lt.strGroupDetail,lt.strAddress,lt.strPhone,lt.strLink,lt.chCategory,ST_X(lt.ptLongLat),ST_Y(lt.ptLongLat)
            FROM {LocationReviewTable.NAME} AS lrt
            JOIN {LocationTable.NAME} AS lt ON lrt.iLocationFK = lt.iPK
            WHERE lrt.iLocationFK = {iLocationPK}
            ORDER BY lrt.nScore DESC, lrt.dtCreate DESC"""

    @staticmethod
    def TO_SELECT_TOP_LIST_QUERY(nLimitCount: int = 10, category_group_code: str = None) -> str:
        return f"""
            SELECT lrt.iLocationFK,AVG(lrt.nScore) as nAvgScore,lt.iPK,lt.strName,lt.strGroupCode
            FROM {LocationReviewTable.NAME} AS lrt JOIN {LocationTable.NAME} AS lt ON lrt.iLocationFK = lt.iPK
            {f"WHERE lt.strGroupCode='{category_group_code}'" if (category_group_code) else ""}
            GROUP BY lrt.iLocationFK
            ORDER BY nAvgScore DESC LIMIT {nLimitCount}"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, LocationReviewView.TO_SELECT_MODEL_QUERY(1))
            rows_tuple = cursor.fetchall()
            front_list = LocationReviewView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)

