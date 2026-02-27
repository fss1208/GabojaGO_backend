from models.favorite_model import FavoriteModel
from library.DB import DB, BaseTable
import logging

class FavoriteTable(BaseTable):

    NAME = "favorite"

    @staticmethod
    def TO_MODEL(row: tuple) -> FavoriteModel:
        return FavoriteModel(
            iPK=row[0],
            iUserFK=row[1],
            strName=row[2]
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[FavoriteModel]:
        return [FavoriteTable.TO_MODEL(row) for row in rows_tuple]

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return f"""
            CREATE TABLE {FavoriteTable.NAME} (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iUserFK INT NOT NULL,
                strName VARCHAR(128) NOT NULL,
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""

    @staticmethod
    def TO_SELECT_MODEL_QUERY(iFavoritePK: int) -> str:
        return f"SELECT iPK,iUserFK,strName FROM {FavoriteTable.NAME} WHERE iPK={iFavoritePK}"

    @staticmethod
    def TO_SELECT_LIST_QUERY(iUserPK: int) -> str:
        return f"SELECT iPK,iUserFK,strName FROM {FavoriteTable.NAME} WHERE iUserFK={iUserPK}"

    @staticmethod
    def TO_INSERT_QUERY(iUserFK: int, strName: str) -> str:
        return f"INSERT INTO {FavoriteTable.NAME} (iUserFK,strName) VALUES ({iUserFK},'{strName}')"

    @staticmethod
    def TO_DELETE_QUERY(iFavoritePK: int) -> str:
        return f"DELETE FROM {FavoriteTable.NAME} WHERE iPK={iFavoritePK}"

#############################################################################################################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, f"DROP TABLE IF EXISTS {FavoriteTable.NAME}")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, FavoriteTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)