from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule.schedule_location_view import ScheduleLocationView
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
def append_location(schedule_location_model: ScheduleLocationModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 장소를 일정에 등록
    - **ScheduleLocationModel.iSchedulePK: int** 필수 입력
    - **ScheduleLocationModel.iLocationPK: int** 필수 입력
    - **ScheduleLocationModel.dtSchedule: datetime** 필수 입력
    - **ScheduleLocationModel.strMemo: str** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_location_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_INSERT_QUERY(schedule_location_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {schedule_location_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_location_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_location_model.to_log(), dt))
    return schedule_location_model

@router.post("/modify", summary="장소의 일시 및 메모 수정", response_model=ScheduleLocationModel)
def modify_location(schedule_location_model: ScheduleLocationModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 장소의 일시 및 메모 수정
    - **ScheduleLocationModel.iPK: int** 필수 입력
    - **ScheduleLocationModel.dtSchedule: datetime** 수정 항목
    - **ScheduleLocationModel.strMemo: str** 수정 항목
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_location_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_UPDATE_QUERY(schedule_location_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 수정 실패, {schedule_location_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_location_model.to_log(), dt))
    return schedule_location_model

@router.post("/remove", summary="장소 삭제", response_model=dict)
def remove_location(iScheduleLocationPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 장소 삭제
    - **iScheduleLocationPK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iScheduleLocationPK:{iScheduleLocationPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationTable.TO_DELETE_QUERY(iScheduleLocationPK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iScheduleLocationPK": iScheduleLocationPK}

@router.get("/list", summary="장소 목록 조회", response_model=ScheduleLocationListModel)
def list_schedule_location(iSchedulePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 장소 목록 조회
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleLocationView.TO_SELECT_MODEL_QUERY(iSchedulePK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"DB 조회 실패, {request_log} (데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuple)})"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_location_list_model = ScheduleLocationListModel(location_list=ScheduleLocationView.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return schedule_location_list_model
