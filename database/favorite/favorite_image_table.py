from models.favorite_model import FavoriteImageModel
from library.DB import DB, BaseTable
import logging

class FavoriteImageTable(BaseTable):

    NAME = "favorite_image"
    MODEL_COLUMNS = "iPK,iFavoriteFK,iImageFK,dtFavorite"

    @staticmethod
    def TO_MODEL(row: tuple) -> FavoriteImageModel:
        return FavoriteImageModel(
            iPK=row[0],
            iFavoriteFK=row[1],
            iImageFK=row[2],
            dtFavorite=row[3]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {FavoriteImageTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iFavoriteFK INT NOT NULL,
                iImageFK INT NOT NULL,
                dtFavorite DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iFavoriteFK) REFERENCES favorite(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iImageFK) REFERENCES image(iPK) ON DELETE CASCADE
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iFavoriteImagePK: int) -> str:
        return f"SELECT {FavoriteImageTable.MODEL_COLUMNS} FROM {FavoriteImageTable.NAME} WHERE iPK={iFavoriteImagePK}"

    @staticmethod
    def TO_INSERT_QUERY(iFavoriteFK: int, iImageFK: int) -> str:
        return f"INSERT INTO {FavoriteImageTable.NAME} (iFavoriteFK,iImageFK) VALUES ({iFavoriteFK},{iImageFK})"

    @staticmethod
    def TO_DELETE_QUERY(iFavoriteImagePK: int) -> str:
        return f"DELETE FROM {FavoriteImageTable.NAME} WHERE iPK={iFavoriteImagePK}"

#############################################################################################################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {FavoriteImageTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, FavoriteImageTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)