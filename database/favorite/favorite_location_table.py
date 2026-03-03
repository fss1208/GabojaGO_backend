from models.favorite_model import FavoriteLocationModel
from library.DB import DB, BaseTable
import logging

class FavoriteLocationTable(BaseTable):

    NAME = "favorite_location"
    MODEL_COLUMNS = "iPK,iFavoriteFK,iLocationFK,dtFavorite"

    @staticmethod
    def TO_MODEL(row: tuple) -> FavoriteLocationModel:
        return FavoriteLocationModel(
            iPK=row[0],
            iFavoriteFK=row[1],
            iLocationFK=row[2],
            dtFavorite=row[3]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {FavoriteLocationTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iFavoriteFK INT NOT NULL,
                iLocationFK BIGINT UNSIGNED NOT NULL,
                dtFavorite DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (iFavoriteFK) REFERENCES favorite(iPK) ON DELETE CASCADE,
                FOREIGN KEY (iLocationFK) REFERENCES location(iPK) ON DELETE CASCADE
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iFavoriteLocationPK: int) -> str:
        return f"SELECT {FavoriteLocationTable.MODEL_COLUMNS} FROM {FavoriteLocationTable.NAME} WHERE iPK={iFavoriteLocationPK}"

    @staticmethod
    def TO_SELECT_LOCATION_QUERY(iFavoriteFK: int, iLocationFK: int) -> str:
        return f"SELECT * FROM {FavoriteLocationTable.NAME} WHERE iFavoriteFK={iFavoriteFK} AND iLocationFK={iLocationFK}"

    @staticmethod
    def TO_INSERT_QUERY(iFavoriteFK: int, iLocationFK: int) -> str:
        return f"INSERT INTO {FavoriteLocationTable.NAME} (iFavoriteFK,iLocationFK) VALUES ({iFavoriteFK},{iLocationFK})"

    @staticmethod
    def TO_UPDATE_QUERY(iFavoriteLocationPK: int, iFavoriteFK: int) -> str:
        return f"UPDATE {FavoriteLocationTable.NAME} SET iFavoriteFK={iFavoriteFK} WHERE iPK={iFavoriteLocationPK}"

    @staticmethod
    def TO_DELETE_QUERY(iFavoriteLocationPK: int) -> str:
        return f"DELETE FROM {FavoriteLocationTable.NAME} WHERE iPK={iFavoriteLocationPK}"

#############################################################################################################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {FavoriteLocationTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, FavoriteLocationTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)