from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.location.location_review_table import LocationReviewTable
from models.location_model import LocationReviewModel, LocationReviewListModel
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

@router.post("/append", summary="장소 리뷰 추가", response_model=LocationReviewModel)
def append_location_review(location_review_model: LocationReviewModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 장소에 대한 리뷰 추가
    - **LocationReviewModel.iLocationFK: int** 필수 입력
    - **LocationReviewModel.nScore: int** 필수 입력
    - **LocationReviewModel.bRevisit: bool** 필수 입력
    - **LocationReviewModel.strReview: str** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", location_review_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            location_review_model.iUserFK = login_user.iPK
            result = DB.EXECUTE(cursor, LocationReviewTable.TO_INSERT_QUERY(location_review_model))
            if (result != 1):
                connection.rollback()
                msg = f"DB 등록 실패, {location_review_model.to_log()}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            location_review_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", location_review_model.to_log(), dt))
    return location_review_model

@router.post("/modify", summary="장소 리뷰 수정", response_model=LocationReviewModel)
def modify_location_review(location_review_model: LocationReviewModel, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 장소 리뷰 수정
    - **LocationReviewModel.iPK: int** 필수 입력
    - **LocationReviewModel.nScore: int** 수정 항목
    - **LocationReviewModel.bRevisit: bool** 수정 항목
    - **LocationReviewModel.strReview: str** 수정 항목
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", location_review_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationReviewTable.TO_UPDATE_QUERY(location_review_model))
            if (result != 1):
                count = DB.EXECUTE(cursor, LocationReviewTable.TO_SELECT_MODEL_QUERY(location_review_model.iPK))
                if (count == 0):
                    connection.rollback()
                    msg = f"존재하지 않은 iPK, {location_review_model.to_log()}"
                    logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                    raise HTTPException(status_code=500, detail=msg)
                else: # (count == 1)
                    logger.debug(LOG.TO_MESSAGE(request, login_user.to_log(), "데이터 변경사항 없음", location_review_model.to_log()))
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", location_review_model.to_log(), dt))
    return location_review_model

@router.post("/remove", summary="장소 리뷰 삭제", response_model=dict)
def remove_location_review(iLocationReviewPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 장소 리뷰 삭제
    - **iLocationReviewPK: int** 필수 입력
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iLocationReviewPK:{iLocationReviewPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationReviewTable.TO_DELETE_QUERY(iLocationReviewPK))
            if (result != 1):
                connection.rollback()
                msg = f"DB 삭제 실패, {request_log}"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", request_log, dt))
    return {"iLocationReviewPK": iLocationReviewPK}

@router.get("/list", summary="장소 리뷰 목록 조회", response_model=LocationReviewListModel)
def list_location_review(iLocationPK: int, iUserPK: int, request: Request, auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    사용자가 요청하는 장소에 대한 리뷰 목록 조회 (iLocationPK=0, iUserPK=0 : 사용 불가)
    - **iLocationPK: int** 필수 입력 (iLocationPK=0 : 모든 장소 조회, iLocationPK>0 : 특정 장소만 조회)
    - **iUserPK: int** 필수 입력 (iUserPK=0 : 전체 사용자 조회, iUserPK>0 : 특정 사용자만 조회)
    """
    dt = datetime.now()
    login_user = AUTH_JWT.TO_USER_MODEL(auth)
    request_log = f"iLocationPK:{iLocationPK},iUserPK:{iUserPK}"
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "요청", request_log))
    if ((iLocationPK == 0) and (iUserPK == 0)):
        msg = f"iLocationPK와 iUserPK 모두 0일 수는 없습니다."
        logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
        raise HTTPException(status_code=500, detail=msg)
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationReviewTable.TO_SELECT_LIST_QUERY(iLocationPK, iUserPK))
            rows_tuple = cursor.fetchall()
            if (result != len(rows_tuple)):
                msg = f"DB 조회 실패, {request_log} (데이터 개수 불일치, {request_log}, 요청:{result}, 실제:{len(rows_tuple)})"
                logger.error(LOG.TO_MESSAGE(request, login_user.to_log(), "실패!", msg, dt))
                raise HTTPException(status_code=500, detail=msg)
            location_review_list_model = LocationReviewListModel(review_list=LocationReviewTable.TO_MODEL_LIST(rows_tuple))
    logger.info(LOG.TO_MESSAGE(request, login_user.to_log(), "완료", f"{request_log}, {result}건", dt))
    return location_review_list_model
