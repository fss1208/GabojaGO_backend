from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable
from models.image_model import ImageModel
from models.favorite_model import FavoriteImageFrontModel
from database.favorite.favorite_image_table import FavoriteImageTable
from database.image_table import ImageTable

class FavoriteImageView(BaseTable):

    @staticmethod
    def TO_MODEL(row: tuple) -> FavoriteImageFrontModel:
        return FavoriteImageFrontModel(
            iPK=row[0],
            iFavoriteFK=row[1],
            iImageFK=row[2],
            dtFavorite=row[3],
            image=ImageModel(
                iPK=row[4],
                iUserFK=row[5],
                iLocationPK=row[6],
                strFile=row[7],
                dtImage=row[8],
                ptLongitude=str(row[9]),
                ptLatitude=str(row[10]),
                dtCreate=row[11]
            )
        )

    @staticmethod
    def TO_MODEL_LIST(rows_tuple: tuple) -> list[FavoriteImageFrontModel]:
        return [FavoriteImageView.TO_MODEL(row_tuple) for row_tuple in rows_tuple]

    @staticmethod
    def TO_SELECT_LIST_QUERY(iFavoritePK: int) -> str:
        return f"""
            SELECT
               fit.iPK,fit.iFavoriteFK,fit.iImageFK,fit.dtFavorite,
               it.iPK,it.iUserFK,it.iLocationPK,it.strFile,it.dtImage,ST_X(it.ptLongLat),ST_Y(it.ptLongLat),it.dtCreate
            FROM {FavoriteImageTable.NAME} AS fit
            JOIN {ImageTable.NAME} AS it ON fit.iImageFK = it.iPK
            WHERE fit.iFavoriteFK = {iFavoritePK} 
            ORDER BY fit.dtFavorite DESC"""

####################################################################################################################################################

if (__name__ == "__main__"):
    import json
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.EXECUTE(cursor, FavoriteImageView.TO_SELECT_LIST_QUERY(1))
            rows_tuple = cursor.fetchall()
            front_list = FavoriteImageView.TO_MODEL_LIST(rows_tuple)
            for front_model in front_list:
                print(front_model)
