from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime

class KakaoMapSearchRequestModel(BaseModel):
    query: str = Field(..., max_length=255, example="성산일출봉", description="검색어")
    category_group_code: Optional[str] = Field(None, example="AT4", description="AT4:관광명소, AD5:숙박, FD6:음식점, PK6:주차장, OL7:주유소, SW8:지하철역, CE7:카페, CS2:편의점, MT1:대형마트 ...")
    x: Optional[str] = Field(None, example="126.9194", description="경도 (Longitude)")
    y: Optional[str] = Field(None, example="33.4918", description="위도 (Latitude)")
    radius: Optional[int] = Field(None, example=1000, description="위경도 기준 검색 반경 (단위: meter, 최소:0, 최대:20,000)")
    rect: Optional[str] = Field(None, example="1.2,3.48,5.6,7.8", description="두 점의 좌표로 만든 범위 (좌측X, 좌측Y, 우측X, 우측Y)")
    page: Optional[int] = Field(None, example=1, description="결과 페이지 번호 (최소:1, 최대:45, 기본값:1)")
    size: Optional[int] = Field(None, ge=1, le=15, example=15, description="한 페이지에 보여질 문서의 개수 (최소:1, 최대:15, 기본값:15)")
    sort: Optional[str] = Field(None, example="accuracy", description="accuracy:정확도순(기본값), distance:거리순")

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

class LocationListModel(BaseModel):
    location_list: list[LocationModel] = Field(..., description="장소 정보 목록")

###############################################################################################################################################################

class LocationReviewModel(BaseModel):
    iPK: int = Field(..., example=0, description="LocationReviewTable.iPK")
    iLocationFK: int = Field(..., example=2062374957, description="LocationTable.iPK")
    iUserFK: int = Field(..., example=0, description="UserTable.iPK")
    nScore: int = Field(..., ge=0, le=5, example=5, description="평점 (0 ~ 5)")
    bRevisit: bool = Field(..., example=False, description="다시 방문할 계획 (True/False)")
    strReview: str = Field(..., max_length=1024, example="장소에 대한 소감", description="리뷰")
    dtCreate: datetime = Field(..., example="2026-02-28 10:20:30", description="리뷰 작성 시간")
    #
    @field_serializer('dtCreate')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    #
    def to_log(self) -> str:
        return f"{self.iPK}:{self.iLocationFK}:{self.iUserFK}:{self.nScore}:{self.bRevisit}"

class LocationReviewFrontModel(LocationReviewModel): # 미사용
    location: LocationModel = Field(..., description="장소 정보")

class LocationReviewListModel(BaseModel):
    review_list: list[LocationReviewModel] = Field(..., description="장소 리뷰 목록")

###############################################################################################################################################################

class LocationRequestItemModel(BaseModel):
    """
    장소 정보 요청  모델
    """
    place_name: str = Field(..., example="청년취업사관학교 도봉캠퍼스")
    category_group_code: Optional[str] = Field(None, example="FD6")

class LocationRequestListModel(BaseModel):
    """
    AI로 생성한 장소 이름 목록 
    """
    request_list: list[LocationRequestItemModel] = Field(..., example=[LocationRequestItemModel(place_name="섭지코지", category_group_code="AT4")], description="장소 이름 목록")
