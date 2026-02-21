from pydantic import BaseModel, Field
from typing import Optional
import logging

class KakaoMapSearchRequestModel(BaseModel):
    query: str = Field(..., max_length=255, example="성산일출봉")   # 검색어
    x: Optional[str] = Field(None, example="126.9194")                          # 경도 (Longitude)
    y: Optional[str] = Field(None, example="33.4918")                           # 위도 (Latitude)
    radius: Optional[int] = Field(None, example=1000)                           # 반경 (미터)
    page: Optional[int] = Field(None, example=1)                                # 페이지 번호
    size: Optional[int] = Field(None, ge=0, le=15, example=15)                  # 결과 개수 (최대 15)

class LocationModel(BaseModel):
    pk: int = Field(..., example=1)
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
                "link": row[10]
            }
            super().__init__(**data)
        else:
            super().__init__(**kwargs)
