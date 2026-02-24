from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule.schedule_location_table import ScheduleLocationTable
from models.schedule_model import ScheduleLocationModel, ScheduleLocationListModel
from library.JWT import AUTH_JWT
from library.LOG import LOG
from library.DB import DB

from datetime import datetime, timedelta
import logging
import json
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

#################################################################################################################

@router.post("/append", summary="장소 등록", response_model=ScheduleLocationModel)
def append_location(schedule_location_model: ScheduleLocationModel, request: Request):
    """
    사용자가 요청하는 장소를 일정에 등록
    - **ScheduleLocationModel.iSchedulePK: int** 필수 입력
    - **ScheduleLocationModel.iLocationPK: int** 필수 입력
    - **ScheduleLocationModel.dtSchedule: datetime** 필수 입력
    - **ScheduleLocationModel.strMemo: str** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_INSERT_QUERY(schedule_location_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 등록 실패, {schedule_location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_location_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_model

@router.post("/modify", summary="장소의 일시 및 메모 수정", response_model=ScheduleLocationModel)
def modify_location(schedule_location_model: ScheduleLocationModel, request: Request):
    """
    사용자가 요청하는 일정에 등록된 장소의 일시 및 메모 수정
    - **ScheduleLocationModel.iPK: int** 필수 입력
    - **ScheduleLocationModel.dtSchedule: datetime** 수정 항목
    - **ScheduleLocationModel.strMemo: str** 수정 항목
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_location_model.model_dump()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_UPDATE_QUERY(schedule_location_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 수정 실패, {schedule_location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_model

@router.post("/remove", summary="장소 삭제", response_model=ScheduleLocationModel)
def remove_location(schedule_location_model: ScheduleLocationModel, request: Request):
    """
    사용자가 요청하는 일정에 등록된 장소 삭제
    - **ScheduleLocationModel.iPK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({schedule_location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_DELETE_QUERY(schedule_location_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 삭제 실패, {schedule_location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"{text_log} 완료 ({schedule_location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_model

@router.get("/list", summary="장소 목록 조회", response_model=ScheduleLocationListModel)
def list_schedule(iSchedulePK: int, request: Request):
    """
    사용자가 요청하는 일정에 등록된 장소 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(f"{text_log} 요청 ({request_log})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_SELECT_LIST_QUERY(iSchedulePK))
            rows_tuples = cursor.fetchall()
            if (result != len(rows_tuples)):
                msg = f"{text_log} 실패! (데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuples)})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_location_list_model = ScheduleLocationListModel(location_list=ScheduleLocationTable.TO_MODEL_LIST(rows_tuples))
    logger.info(f"{text_log} 완료 ({request_log}:{result}개, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_list_model
