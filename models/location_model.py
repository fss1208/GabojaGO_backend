from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB

class KakaoMapSearchRequestModel(BaseModel):
    query: str = Field(..., max_length=255, example="성산일출봉")   # 검색어
    x: Optional[str] = Field(None, example="126.9194")                          # 경도 (Longitude)
    y: Optional[str] = Field(None, example="33.4918")                           # 위도 (Latitude)
    radius: Optional[int] = Field(None, example=1000)                           # 반경 (미터)
    page: Optional[int] = Field(None, example=1)                                # 페이지 번호
    size: Optional[int] = Field(None, ge=0, le=15, example=15)                  # 결과 개수 (최대 15)

class LocationModel(BaseModel):
    pk: int = Field(..., example=0)
    id: int = Field(..., example=2062374957)
    name: str = Field(..., max_length=255, example="청년취업사관학교 도봉캠퍼스")
    longitude: str = Field(..., example="127.1005")
    latitude: str = Field(..., example="37.5115")
    category: str = Field(..., example="E")
    group_name: Optional[str] = Field(None, example="교육센터")
    group_detail: Optional[str] = Field(None, example="교육,학문 > 직업전문교육")
    address: Optional[str] = Field(None, max_length=255, example="서울특별시 도봉구 마들로13길 61 씨드큐브 창동 7층")
    phone: Optional[str] = Field(None, example="02-6249-7402")
    link: Optional[str] = Field(None, max_length=255, example="http://place.map.kakao.com/2062374957")
    datetime: Optional[str] = Field(None, example="2026-02-21 15:01:31")

    def __init__(self, row: tuple = None, **kwargs):
        if row is not None and isinstance(row, tuple):
            data = {
                "pk": row[0],
                "id": row[1],
                "longitude": row[2],
                "latitude": row[3],
                "name": row[4],
                "category": row[5],
                "group_name": row[6],
                "group_detail": row[7],
                "address": row[8],
                "phone": row[9],
                "link": row[10],
                "datetime": row[11]
            }
            super().__init__(**data)
        else:
            super().__init__(**kwargs)

    @staticmethod
    def CREATE_TABLE() -> str:
        return """
            CREATE TABLE location (
                iPK INT AUTO_INCREMENT PRIMARY KEY,
                iID INT NOT NULL UNIQUE,
                ptLongLat POINT NOT NULL,
                strName VARCHAR(128) NOT NULL,
                chCategory CHAR(1) NOT NULL,
                strGroupName VARCHAR(128),
                strGroupDetail VARCHAR(128),
                strAddress VARCHAR(128),
                strPhone VARCHAR(128),
                strLink VARCHAR(1024),
                dtCreate DATETIME DEFAULT CURRENT_TIMESTAMP,
                SPATIAL INDEX(ptLongLat)      
            );"""

    @staticmethod
    def SELECT_ID_QUERY(id: int) -> str:
        return "SELECT * FROM location WHERE iID = {0}".format(id)

    def insert_query(self) -> str:
        return "INSERT INTO location (iID,ptLongLat,strName,chCategory,strGroupName,strGroupDetail,strAddress,strPhone,strLink,dtCreate) VALUES ('{0}',{1},'{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(
            self.id, DB.TO_POINT(self.longitude, self.latitude), self.name, self.category, self.group_name, self.group_detail, self.address, self.phone, self.link, self.datetime)

####################################################################################################################################################

if (__name__ == "__main__"):
    from library.DB import DB
    from dotenv import load_dotenv
    load_dotenv(override=True)
    logging.basicConfig(level=logging.DEBUG)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, "DROP TABLE IF EXISTS location")
            DB.SHOW_TABLES(cursor)
            DB.EXECUTE(cursor, LocationModel.CREATE_TABLE())
            DB.SHOW_TABLES(cursor)