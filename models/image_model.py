from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime

class ImageModel(BaseModel):
    iPK: int = Field(..., example=0, description="ImageTable.iPK")
    iUserFK: int = Field(..., example=0, description="UserTable.iPK")
    iLocationPK: Optional[int] = Field(default=0, example=2062374957, description="LocationTable.iPK")
    strFile: str = Field(..., example="20260228123456.jpg", description="이미지 파일명")
    dtImage: datetime = Field(..., example="2026-02-28 11:22:33", description="이미지 촬영 일시")
    ptLongitude: str = Field(..., example="127.1005", description="경도")
    ptLatitude: str = Field(..., example="37.5115", description="위도")
    dtCreate: datetime = Field(..., example="2026-02-28 12:34:56", description="이미지 등록 일시")
    # 날짜 직렬화
    @field_serializer('dtImage')
    def serialize_dtImage(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    # 날짜 직렬화
    @field_serializer('dtCreate')
    def serialize_dtCreate(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    # 로그 출력
    def to_log(self) -> str:
        return f"{self.iPK}:{self.iUserFK}:{self.iLocationPK}:{self.dtImage}:{self.strFile}"
