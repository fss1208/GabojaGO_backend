from pydantic import BaseModel, Field
from typing import Optional
import logging

from library.DB import DB, BaseTable

class KakaoMapSearchRequestModel(BaseModel):
    query: str = Field(..., max_length=255, example="성산일출봉")    # 검색어
    category_group_code: Optional[str] = Field(None, example="AT4") # 카테고리 그룹 코드
    x: Optional[str] = Field(None, example="126.9194")              # 경도 (Longitude)
    y: Optional[str] = Field(None, example="33.4918")               # 위도 (Latitude)
    radius: Optional[int] = Field(None, example=1000)               # 반경 (단위: meter, 최소:0, 최대:20,000)
    rect: Optional[str] = Field(None, example="1.2,3.48,5.6,7.8")   # 두 점의 좌표로 만든 범위 (좌측X, 좌측Y, 우측X, 우측Y)
    page: Optional[int] = Field(None, example=1)                    # 결과 페이지 번호 (최소:1, 최대:45, 기본값:1)
    size: Optional[int] = Field(None, ge=1, le=15, example=15)      # 한 페이지에 보여질 문서의 개수 (최소:1, 최대:15, 기본값:15)

class LocationModel(BaseModel):
    id: int = Field(..., example=2062374957)
    name: str = Field(..., max_length=255, example="청년취업사관학교 도봉캠퍼스")
    group_code: str = Field(..., example="FD6")
    group_name: str = Field(..., example="교육센터")
    group_detail: str = Field(..., example="교육,학문 > 직업전문교육")
    address: str = Field(..., max_length=255, example="서울특별시 도봉구 마들로13길 61 씨드큐브 창동 7층")
    phone: str = Field(..., example="02-6249-7402")
    link: str = Field(..., max_length=255, example="http://place.map.kakao.com/2062374957")
    category: str = Field(..., example="E")
    longitude: str = Field(..., example="127.1005")
    latitude: str = Field(..., example="37.5115")

    def to_log(self) -> str:
        return f"{self.id}:{self.name}"

class LocationTable(BaseTable):

    def to_models(self) -> list[LocationModel]:
        return [self.TO_MODEL(row) for row in self.rows_tuples]

    @staticmethod
    def TO_MODEL(row: tuple) -> LocationModel:
        return LocationModel(
            id=row[0],
            name=row[1],
            group_code=row[2],
            group_name=row[3],
            group_detail=row[4],
            address=row[5],
            phone=row[6],
            link=row[7],
            category=row[8],
            longitude=row[9],
            latitude=row[10]
        )

    @staticmethod
    def TO_CREATE_QUERY() -> str:
        return """
            CREATE TABLE location (
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
    def TO_SELECT_MODEL_QUERY(lm: LocationModel) -> str:
        return "SELECT iPK,strName,strGroupCode,strGroupName,strGroupDetail,strAddress,strPhone,strLink,chCategory,ST_X(ptLongLat),ST_Y(ptLongLat) FROM location WHERE iPK={0}".format(lm.id)

    @staticmethod
    def TO_SELECT_ID_QUERY(lm: LocationModel) -> str:
        return "SELECT iPK,strName FROM location WHERE iPK={0}".format(lm.id)

    @staticmethod
    def TO_INSERT_QUERY(lm: LocationModel) -> str:
        return "INSERT INTO location (iPK,strName,strGroupCode,strGroupName,strGroupDetail,strAddress,strPhone,strLink,chCategory,ptLongLat) " + \
                            f"VALUES ({lm.id},'{lm.name}','{lm.group_code}','{lm.group_name}','{lm.group_detail}','{lm.address}','{lm.phone}','{lm.link}','{lm.category}',{DB.TO_POINT(lm.longitude, lm.latitude)})"

    @staticmethod
    def TO_DELETE_QUERY(lm: LocationModel) -> str:
        return "DELETE FROM location WHERE iPK={0}".format(lm.id)

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
            DB.EXECUTE(cursor, LocationTable.TO_CREATE_QUERY())
            DB.SHOW_TABLES(cursor)