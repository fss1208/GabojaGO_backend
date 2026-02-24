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

@router.post("/append", summary="일정에 장소 등록", response_model=ScheduleLocationModel)
def append_location(schedule_location_model: ScheduleLocationModel):
    """
    여행 일정에 장소 등록 (수동)
    """
    dt = datetime.now()
    logger.info(f"일정에 장소 추가 요청 ({schedule_location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_INSERT_QUERY(schedule_location_model))
            if (result != 1):
                msg = f"일정 장소 추가 실패! (DB 등록 실패, {schedule_location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_location_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"일정에 장소 추가 완료 ({schedule_location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_model

@router.post("/modify", summary="일정에 등록된 장소의 일시 및 메모 수정", response_model=ScheduleLocationModel)
def modify_location(schedule_location_model: ScheduleLocationModel):
    """
    여행 일정에 등록된 장소의 일시 및 메모 수정
    """
    dt = datetime.now()
    logger.info(f"일정에 등록된 장소 수정 요청 ({schedule_location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_UPDATE_QUERY(schedule_location_model))
            if (result != 1):
                msg = f"일정에 등록된 장소 수정 실패! (DB 수정 실패, {schedule_location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"일정에 등록된 장소 수정 완료 ({schedule_location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_model

@router.post("/remove", summary="일정에 등록된 장소 삭제", response_model=ScheduleLocationModel)
def remove_location(schedule_location_model: ScheduleLocationModel):
    """
    여행 일정에 등록된 장소 삭제 (수동)
    """
    dt = datetime.now()
    logger.info(f"일정에 장소 삭제 요청 ({schedule_location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_DELETE_QUERY(schedule_location_model))
            if (result != 1):
                msg = f"일정 장소 삭제 실패! (DB 삭제 실패, {schedule_location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"일정에 장소 삭제 완료 ({schedule_location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_model

@router.get("/list", summary="일정에 등록된 장소 목록 조회", response_model=ScheduleLocationListModel)
def list_schedule(iSchedulePK: int):
    """
    여행 일정에 등록된 장소 목록 조회
    """
    dt = datetime.now()
    req_log = f"일정:{iSchedulePK}"
    text_log = "일정에 등록된 장소 목록 조회"
    logger.info(f"{text_log} 요청 ({req_log})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_SELECT_LIST_QUERY(iSchedulePK))
            rows_tuples = cursor.fetchall()
            if (result != len(rows_tuples)):
                msg = f"{text_log} 실패! (데이터 개수 불일치, {req_log}, 요청:{result}, 실제:{len(rows_tuples)})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_location_list_model = ScheduleLocationListModel(location_list=ScheduleLocationTable.TO_MODEL_LIST(rows_tuples))
    logger.info(f"{text_log} 완료 ({req_log}:{result}개, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_location_list_model
