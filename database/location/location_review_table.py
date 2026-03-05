from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.location_model import LocationReviewModel

class LocationReviewTable(BaseTable):

    NAME = "location_review"

    @staticmethod
    def TO_MODEL(row: tuple) -> LocationReviewModel:
        return LocationReviewModel(
            iPK=row[0],
            iLocationFK=row[1],
            iUserFK=row[2],
            nScore=row[3],
            bRevisit=row[4],
            strReview=row[5],
            dtCreate=row[6]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[LocationReviewModel]:
        return [LocationReviewTable.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {LocationReviewTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iLocationFK BIGINT UNSIGNED NOT NULL,
                iUserFK INT NOT NULL,
                nScore TINYINT UNSIGNED NOT NULL,
                bRevisit BOOLEAN NOT NULL,
                strReview VARCHAR(1024),
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iLocationFK) REFERENCES location(iPK),
                FOREIGN KEY (iUserFK) REFERENCES user(iPK)
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iLocationReviewPK: int) -> str:
        return f"SELECT * FROM {LocationReviewTable.NAME} WHERE iPK={iLocationReviewPK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iLocationFK: int, iUserFK: int, nLimitCount: int = 10) -> str:
        strUser = "" if (iUserFK == 0) else f"iUserFK={iUserFK}"
        strLocation = "" if (iLocationFK == 0) else f"iLocationFK={iLocationFK}"
        if ((iLocationFK != 0) and (iUserFK != 0)):
            return f"SELECT * FROM {LocationReviewTable.NAME} WHERE {strLocation} AND {strUser} ORDER BY dtCreate DESC"
        elif ((iLocationFK != 0) and (iUserFK == 0)):
            return f"SELECT * FROM {LocationReviewTable.NAME} WHERE {strLocation} ORDER BY dtCreate DESC"
        elif ((iLocationFK == 0) and (iUserFK != 0)):
            return f"SELECT * FROM {LocationReviewTable.NAME} WHERE {strUser} ORDER BY dtCreate DESC"
        # TODO: iLocationFK별 가장 평균 평점이 높은 순으로 정렬
        return f"SELECT iLocationFK, AVG(nScore) as nAvgScore FROM {LocationReviewTable.NAME} GROUP BY iLocationFK ORDER BY nAvgScore DESC LIMIT {nLimitCount}"

    @staticmethod
    def TO_INSERT_QUERY(lrm: LocationReviewModel) -> str:
        return f"INSERT INTO {LocationReviewTable.NAME} (iLocationFK,iUserFK,nScore,bRevisit,strReview) " + \
               f"VALUES ({lrm.iLocationFK},{lrm.iUserFK},{lrm.nScore},{lrm.bRevisit},'{lrm.strReview}')"

    @staticmethod
    def TO_UPDATE_QUERY(lrm: LocationReviewModel) -> str:
        return f"UPDATE {LocationReviewTable.NAME} SET nScore={lrm.nScore},bRevisit={lrm.bRevisit},strReview='{lrm.strReview}' WHERE iPK={lrm.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(iLocationReviewPK: int) -> str:
        return f"DELETE FROM {LocationReviewTable.NAME} WHERE iPK={iLocationReviewPK}"

####################################################################################################################################################

if (__name__ == "__main__"):
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {LocationReviewTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, LocationReviewTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)
