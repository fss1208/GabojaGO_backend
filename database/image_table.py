from models.image_model import ImageModel
from library.DB import DB, BaseTable
import logging

class ImageTable(BaseTable):

    NAME = "image"
    MODEL_COLUMNS = "iPK,iUserFK,iLocationPK,strFile,dtImage,ST_X(ptLongLat),ST_Y(ptLongLat),dtCreate"

    @staticmethod
    def TO_MODEL(row: tuple) -> ImageModel:
        return ImageModel(
            iPK=row[0],
            iUserFK=row[1],
            iLocationPK=row[2],
            strFile=row[3],
            dtImage=row[4],
            ptLongitude=str(row[5]),
            ptLatitude=str(row[6]),
            dtCreate=row[7]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {ImageTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iUserFK INT NOT NULL,
                iLocationPK BIGINT UNSIGNED NOT NULL DEFAULT 0,
                strFile VARCHAR(128) NOT NULL,
                dtImage DATETIME NOT NULL,
                ptLongLat POINT NOT NULL,
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iUserFK) REFERENCES user(iPK) ON DELETE CASCADE,
                SPATIAL INDEX(ptLongLat)      
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iImagePK: int) -> str:
        return f"SELECT {ImageTable.MODEL_COLUMNS} FROM {ImageTable.NAME} WHERE iPK={iImagePK}"

    @staticmethod
    def TO_INSERT_QUERY(im: ImageModel) -> str:
        return f"INSERT INTO {ImageTable.NAME} (iUserFK,iLocationPK,strFile,dtImage,ptLongLat) " + \
               f"VALUES ({im.iUserFK},{im.iLocationPK},'{im.strFile}','{im.dtImage}',{DB.TO_POINT(im.ptLongitude,im.ptLatitude)})"

    @staticmethod
    def TO_UPDATE_QUERY(im: ImageModel) -> str:
        return f"UPDATE {ImageTable.NAME} SET iLocationPK={im.iLocationPK},strFile='{im.strFile}',dtImage='{im.dtImage}',ptLongLat={DB.TO_POINT(im.ptLongitude,im.ptLatitude)} WHERE iPK={im.iPK}"

    @staticmethod
    def TO_DELETE_QUERY(iImagePK: int) -> str:
        return f"DELETE FROM {ImageTable.NAME} WHERE iPK={iImagePK}"

#############################################################################################################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {ImageTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, ImageTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)