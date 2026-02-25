from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime
import logging

from models.location_model import LocationModel

class ScheduleModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example="1", description="일정 ID")
    iUserFK: int = Field(..., example="1", description="사용자 정보")
    dtDate1: str = Field(..., example="2026-02-23", description="시작일자")
    dtDate2: str = Field(..., example="2026-02-25", description="종료일자")
    strWhere: str = Field(..., example="제주도", description="여행지")
    strWithWho: str = Field(..., example="친구", description="누구와")
    strTransport: str = Field(..., example="차량", description="교통수단")
    nTotalPeople: int = Field(..., example="2", description="인원")
    nTotalBudget: int = Field(..., example="1000000", description="예산")
    nAlarmRatio: int = Field(..., example="25", description="알람 비율")
    nTransportRatio: int = Field(..., example="25", description="교통비 비율")
    nLodgingRatio: int = Field(..., example="25", description="숙박비 비율")
    nFoodRatio: int = Field(..., example="25", description="식비 비율")
    chStatus: Optional[str] = Field(None, example="P", description="상태 (P:준비, A:여행중, C:완료)")
    dtCreate: Optional[str] = Field(None, example="2026-02-23 15:11:23", description="yyyy-MM-dd HH:mm:ss")

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iUserFK}:{self.dtDate1}:{self.dtDate2}:{self.strWhere}"

class ScheduleRequestModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example="1", description="ScheduleModel.iPK")

###############################################################################################################################################################

class ScheduleLocationModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example="1", description="일정 ID")
    iScheduleFK: int = Field(..., example="1", description="일정 ID")
    iLocationFK: int = Field(..., example="2062374957", description="장소 ID")
    dtSchedule: datetime = Field(..., example="2026-02-23 15:11:23", description="yyyy-MM-dd HH:mm:ss")
    strMemo: Optional[str] = Field(None, example="장소 메모", description="메모")

    @field_serializer('dtSchedule')
    def serialize_dt(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def to_log(self) -> str:
        return f"{self.iPK}:{self.iScheduleFK}:{self.iLocationFK}:{self.dtSchedule}"

# class ScheduleLocationListModel(BaseModel):
#     location_list: list[ScheduleLocationModel] = Field(..., description="일정 장소 목록", 
#         example="[{'iPK': 1, 'iScheduleFK': 1, 'iLocationFK': 2062374957, 'dtSchedule': '2026-02-23 15:11:23', 'strMemo': '장소 메모'}, ...]")

class ScheduleLocationFrontModel(BaseModel):
    iPK: int = Field(..., example="1", description="ScheduleLocationTable.iPK")
    iScheduleFK: int = Field(..., example="1", description="ScheduleTable.iPK")
    dtSchedule: datetime = Field(..., example="2026-02-23 15:11:23", description="yyyy-MM-dd HH:mm:ss")
    strMemo: Optional[str] = Field(None, example="장소 메모", description="메모")
    location: LocationModel = Field(..., description="장소 정보")

class ScheduleLocationResponseModel(BaseModel):
    location_list: list[ScheduleLocationFrontModel] = Field(..., description="일정 장소 목록")

###############################################################################################################################################################

class ScheduleUserModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example="1")
    iScheduleFK: int = Field(..., example="1", description="사용자가 참석하는 일정")
    iUserFK: int = Field(..., example="1", description="일정 생성자가 아닌 참석하는 사용자")
    dtCreate: datetime = Field(..., example="2026-02-23 15:11:23", description="등록 일시")

    @field_serializer('dtCreate')
    def serialize_dt(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iScheduleFK}:{self.iUserFK}"

class ScheduleUserListModel(BaseModel):
    user_list: list[ScheduleUserModel] = Field(..., description="일정에 등록된 사용자 목록", 
        example="[{'iPK': 1, 'iScheduleFK': 1, 'iUserFK': 1, 'dtCreate': '2026-02-23 15:11:23'}, ...]")

###############################################################################################################################################################

class ScheduleExpenseModel(BaseModel):
    iPK: Optional[int] = Field(default=0, example="0")
    iScheduleFK: int = Field(..., example="1", description="지출한 일정")
    iUserFK: int = Field(..., example="1", description="지출한 사용자")
    dtExpense: datetime = Field(..., example="2026-02-23 15:11:23", description="지출 일시")
    chCategory: str = Field(..., example="F", description="지출 카테고리")
    nMoney: int = Field(..., example="100000", description="지출 금액")
    iLocation: int = Field(..., example="2062374957", description="장소 ID (없으면 0)")
    strMemo: Optional[str] = Field(None, example="메모", description="메모")

    @field_serializer('dtExpense')
    def serialize_dt(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def to_log(self) -> str:
        return f"{self.iPK}:{self.iScheduleFK}:{self.iUserFK}"

class ScheduleExpenseListModel(BaseModel):
    expense_list: list[ScheduleExpenseModel] = Field(..., description="일정에 등록된 지출 목록", 
        example="[{'iPK': 1, 'iScheduleFK': 1, 'iUserFK': 1, 'dtExpense': '2026-02-23 15:11:23', 'chCategory': '식비', 'nMoney': 100000, 'iLocation': 2062374957, 'strMemo': '메모'}, ...]")
