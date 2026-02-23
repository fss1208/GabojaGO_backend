from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule_table import ScheduleTable
from database.schedule_table_location import ScheduleLocationTable
from models.schedule_model import ScheduleModel, ScheduleLocationModel
from models.location_model import LocationModel
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

@router.post("/schedule/create", summary="일정 생성", response_model=ScheduleModel)
def create_schedule(schedule_model: ScheduleModel):
    """
    여행 일정 생성 (수동)
    """
    dt = datetime.now()
    logger.info(f"일정 생성 요청 ({schedule_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleTable.TO_INSERT_QUERY(schedule_model))
            if (result != 1):
                msg = f"일정 생성 실패! (DB 등록 실패, {schedule_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            schedule_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"일정 생성 완료 ({schedule_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return schedule_model

@router.post("/schedule/location/append", summary="일정 장소 추가", response_model=ScheduleLocationModel)
def append_location(schedule_location_model: ScheduleLocationModel):
    """
    여행 일정에 장소 추가 (수동)
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
