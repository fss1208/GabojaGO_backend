from pydantic import BaseModel, Field
from typing import Optional

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
    iPK: int = Field(..., example=2062374957)
    strName: str = Field(..., max_length=255, example="청년취업사관학교 도봉캠퍼스")
    strGroupCode: str = Field(..., example="FD6")
    strGroupName: str = Field(..., example="교육센터")
    strGroupDetail: str = Field(..., example="교육,학문 > 직업전문교육")
    strAddress: str = Field(..., max_length=255, example="서울특별시 도봉구 마들로13길 61 씨드큐브 창동 7층")
    strPhone: str = Field(..., example="02-6249-7402")
    strLink: str = Field(..., max_length=255, example="http://place.map.kakao.com/2062374957")
    chCategory: str = Field(..., example="E")
    ptLongitude: str = Field(..., example="127.1005")
    ptLatitude: str = Field(..., example="37.5115")

    def to_log(self) -> str:
        return f"{self.iPK}:{self.strName}"
