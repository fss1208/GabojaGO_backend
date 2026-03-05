from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule_table import ScheduleTable
from models.schedule_model import ScheduleModel, ScheduleListModel
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

@router.post("/append", summary="일정 추가", response_model=ScheduleModel)
def append_schedule(schedule_model: ScheduleModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자 요청에 의한 일정 수동 추가
    - **dtDate1: date** 필수 입력
    - **dtDate2: date** 필수 입력
    - **strWhere: str** 필수 입력
    - **strWithWho: str** 필수 입력
    - **strTripStyle: str** 필수 입력
    - **strTransport: str** 필수 입력
    - **nTotalPeople: int** 필수 입력
    - **nTotalBudget: int** 필수 입력
    - **nAlarmRatio: int** 필수 입력
    - **nTransportRatio: int** 필수 입력
    - **nLodgingRatio: int** 필수 입력
    - **nFoodRatio: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            schedule_model.iUserFK = login_user.iPK
            result = DB.EXECUTE(cursor, ScheduleTable.TO_INSERT_QUERY(schedule_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {schedule_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_model.to_log(), dt))
    return schedule_model

@router.post("/modify", summary="일정 수정", response_model=ScheduleModel)
def modify_schedule(schedule_model: ScheduleModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자 요청에 의한 일정 수정
    - **iPK: int** 필수 입력
    - **dtDate1: date** 수정 대상
    - **dtDate2: date** 수정 대상
    - **strWhere: str** 수정 대상
    - **strWithWho: str** 수정 대상
    - **strTripStyle: str** 수정 대상
    - **strTransport: str** 수정 대상
    - **nTotalPeople: int** 수정 대상
    - **nTotalBudget: int** 수정 대상
    - **nAlarmRatio: int** 수정 대상
    - **nTransportRatio: int** 수정 대상
    - **nLodgingRatio: int** 수정 대상
    - **nFoodRatio: int** 수정 대상
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleTable.TO_UPDATE_QUERY(schedule_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 수정 실패, {schedule_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_model.to_log(), dt))
    return schedule_model

@router.post("/remove", summary="일정 삭제", response_model=dict)
def remove_schedule(iSchedulePK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자 요청에 의한 일정 삭제
    - **iSchedulePK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iSchedulePK:{iSchedulePK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleTable.TO_DELETE_QUERY(iSchedulePK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iSchedulePK": iSchedulePK}

@router.get("/list", summary="일정 목록 조회", response_model=ScheduleListModel)
def list_schedule(chStatus: str, nFilter: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    여행 일정 목록 조회
    - **chStatus: str** 'A':예정, 'B':진행중, 'C':완료
    - **nFilter: int** 1:내가 생성한 일정만, 2:내가 동행하는 일정만, 3:전체
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"chStatus:{chStatus}, nFilter:{nFilter}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, ScheduleTable.TO_SELECT_LIST_QUERY(login_user.iPK, chStatus, nFilter))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_list_model = ScheduleListModel(schedule_list=ScheduleTable.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return schedule_list_model
