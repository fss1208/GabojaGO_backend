from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.schedule.schedule_preparation_table import SchedulePreparationTable
from models.schedule_model import SchedulePreparationModel, SchedulePreparationListModel
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

@router.post("/append", summary="준비물 정보 추가", response_model=SchedulePreparationModel)
def append_preparation(schedule_preparation_model: SchedulePreparationModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 준비물 추가
    - **SchedulePreparationModel.iSchedulePK: int** 필수 입력
    - **SchedulePreparationModel.strName: str** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_preparation_model.to_log()))
    if (login_user.iPK != schedule_preparation_model.iUserFK):
        msg = f"사용자 정보 불일치로 추가 불가, {schedule_preparation_model.to_log()}"
        logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
        raise HTTPException(status_code=500, detail=msg)  
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, SchedulePreparationTable.TO_INSERT_QUERY(schedule_preparation_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, result={result}, {schedule_preparation_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_preparation_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_preparation_model.to_log(), dt))
    return schedule_preparation_model

@router.post("/modify", summary="준비물 정보 수정", response_model=SchedulePreparationModel)
def modify_preparation(schedule_preparation_model: SchedulePreparationModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 준비물 정보 수정
    - **SchedulePreparationModel.iPK: int** 필수 입력
    - **SchedulePreparationModel.bCheck: bool** 수정 항목
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", schedule_preparation_model.to_log()))
    if (login_user.iPK != schedule_preparation_model.iUserFK):
        msg = f"사용자 정보 불일치로 수정 불가, {schedule_preparation_model.to_log()}"
        logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
        raise HTTPException(status_code=500, detail=msg)      
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, SchedulePreparationTable.TO_UPDATE_QUERY(schedule_preparation_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 수정 실패, result={result}, {schedule_preparation_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", schedule_preparation_model.to_log(), dt))
    return schedule_preparation_model

@router.post("/remove", summary="준비물 정보 삭제", response_model=dict)
def remove_preparation(iSchedulePreparationPK: int, iUserPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 준비물 정보 삭제
    - **iSchedulePreparationPK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"{iSchedulePreparationPK}:{iUserPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    if (login_user.iPK != iUserPK):
        msg = f"사용자 정보 불일치로 삭제 불가, {request_log}"
        logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
        raise HTTPException(status_code=500, detail=msg)      
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, SchedulePreparationTable.TO_DELETE_QUERY(iSchedulePreparationPK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, result={result}, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iSchedulePreparationPK": iSchedulePreparationPK}

@router.get("/list", summary="준비물 정보 조회", response_model=SchedulePreparationListModel)
def list_preparation(iSchedulePK: int, iUserPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 일정에 등록된 준비물 정보 목록 조회
    - **iSchedulePK: int** 필수 입력
    - **iUserPK: int** 필수 입력 (iUserPK = 0 : 전체 사용자 준비물, iUserPK > 0 : 특정 사용자 준비물)
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"{iSchedulePK}:{iUserPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, SchedulePreparationTable.TO_SELECT_LIST_QUERY(iSchedulePK, iUserPK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuple)}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            schedule_preparation_list_model = SchedulePreparationListModel(preparation_list=SchedulePreparationTable.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return schedule_preparation_list_model
