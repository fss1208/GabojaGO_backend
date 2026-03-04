from models.location_model import LocationModel
from library.DB import DB, BaseTable
import logging

class LocationTable(BaseTable):

    NAME = "location"
    MODEL_COLUMNS = "iPK,strName,strGroupCode,strGroupName,strGroupDetail,strAddress,strPhone,strLink,chCategory,ST_X(ptLongLat),ST_Y(ptLongLat)"

    @staticmethod
    def TO_MODEL(row: tuple) -> LocationModel:
        return LocationModel(
            iPK=row[0],
            strName=row[1],
            strGroupCode=row[2],
            strGroupName=row[3],
            strGroupDetail=row[4],
            strAddress=row[5],
            strPhone=row[6],
            strLink=row[7],
            chCategory=row[8],
            ptLongitude=str(row[9]),
            ptLatitude=str(row[10])
        )
    
    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[LocationModel]:
        return [LocationTable.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {LocationTable.NAME} (
                iPK BIGINT UNSIGNED PRIMARY KEY,
                strName VARCHAR(128) NOT NULL,
                strGroupCode CHAR(3),
                strGroupName VARCHAR(128),
                strGroupDetail VARCHAR(128),
                strAddress VARCHAR(128),
                strPhone VARCHAR(128),
                strLink VARCHAR(1024),
                chCategory CHAR(1) NOT NULL DEFAULT 'E',
                ptLongLat POINT NOT NULL,
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                SPATIAL INDEX(ptLongLat)      
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iLocationPK: int) -> str:
        return f"SELECT {LocationTable.MODEL_COLUMNS} FROM {LocationTable.NAME} WHERE iPK={iLocationPK}"

    @staticmethod
    def TO_INSERT_QUERY(lm: LocationModel) -> str:
        return f"INSERT INTO {LocationTable.NAME} (iPK,strName,strGroupCode,strGroupName,strGroupDetail,strAddress,strPhone,strLink,chCategory,ptLongLat) " + \
               f"VALUES ({lm.iPK},'{lm.strName}','{lm.strGroupCode}','{lm.strGroupName}','{lm.strGroupDetail}','{lm.strAddress}','{lm.strPhone}','{lm.strLink}','{lm.chCategory}',{DB.TO_POINT(lm.ptLongitude, lm.ptLatitude)})"

    @staticmethod
    def TO_DELETE_QUERY(iLocationPK: int) -> str:
        return f"DELETE FROM {LocationTable.NAME} WHERE iPK={iLocationPK}"

#############################################################################################################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {LocationTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, LocationTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)