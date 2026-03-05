from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.location_table import LocationTable
from models.location_model import LocationModel, LocationListModel
from models.location_model import KakaoMapSearchRequestModel, LocationRequestListModel
from database.location.location_review_view import LocationReviewView

from library.MAP import KAKAO_MAP
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

@router.post("/search/keyword", summary="키워드로 장소 찾기", response_model=LocationListModel)
def search_keyword_kakaomap(search_param: KakaoMapSearchRequestModel, request: Request):
    """
    사용자가 요청하는 키워드에 해당하는 장소를 찾아 반환 (최대 15개)
    - **query**:str 필수 입력
    - **category_group_code**:str 선택 입력
    """
    dt = datetime.now()
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", search_param.query))
    location_model_list = KAKAO_MAP.SEARCH_KEYWORD(search_param)
    logger.info(LOG.TO_MESSAGE(request, request_user, "완료", search_param.query, dt))
    return LocationListModel(location_list=location_model_list)

@router.post("/request", summary="장소 정보 요청", response_model=LocationListModel)
def request_location(request_model: LocationRequestListModel, request: Request):
    """
    AI가 생성한 일정에 포함된 장소명으로 장소 정보를 검색하여 반환
    **request_list**:list[LocationRequestModel] 필수 입력
    - **LocationRequestModel.place_name**:str 필수 입력
    - **LocationRequestModel.category_group_code**:str 선택 입력
    """
    dt = datetime.now()
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", f"{len(request_model.request_list)}건"))
    response_model_list = []
    for request_item_model in request_model.request_list:
        search_param = KakaoMapSearchRequestModel(
            query=request_item_model.place_name,
            category_group_code=request_item_model.category_group_code if request_item_model.category_group_code else None
        )
        location_model_list = KAKAO_MAP.SEARCH_KEYWORD(search_param)
        for location_model in location_model_list:
            response_model_list.append(location_model)
            break
    new_location_count = 0
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            for location_model in response_model_list:
                result = DB.EXECUTE(cursor, LocationTable.TO_SELECT_MODEL_QUERY(location_model.iPK))
                if (result == 0):
                    result = DB.EXECUTE(cursor, LocationTable.TO_INSERT_QUERY(location_model))
                    new_location_count += 1
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, request_user, "완료", f"전체 {len(response_model_list)}건 중에서 {new_location_count}건 신규 등록"))
    return LocationListModel(location_list=response_model_list)

#################################################################################################################

@router.post("/register", summary="장소 등록", response_model=LocationModel)
def register_location(location_model: LocationModel, request: Request):
    """
    사용자가 요청하는 장소를 등록 (장소 찾기로 받은 정보 그대로 사용)
    """
    dt = datetime.now()
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", location_model.to_log()))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationTable.TO_SELECT_MODEL_QUERY(location_model.iPK))
            if (result == 0):
                result = DB.EXECUTE(cursor, LocationTable.TO_INSERT_QUERY(location_model))
                if (result != 1):
                    connection.rollback()
                    msg = f"DB 등록 실패, result:{result}, {location_model.to_log()}"
                    logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
                    raise HTTPException(status_code=500, detail=msg)
            else:
                msg = f"이미 등록된 장소, {location_model.to_log()}"
                logger.debug(LOG.TO_MESSAGE(request, request_user, "무시", msg))
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, request_user, "완료", f"{location_model.to_log()}", dt))
    return location_model
 
@router.post("/unregister", summary="장소 등록 취소", response_model=dict)
def unregister_location(iLocationPK: int, request: Request):
    """
    사용자가 등록했던 장소를 취소
    - **LocationModel.iPK**:int **필수 입력**
    """
    dt = datetime.now()
    request_log = f"iLocationPK:{iLocationPK}"
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", request_log))
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationTable.TO_DELETE_QUERY(iLocationPK))
            if (result == 0):
                connection.rollback()
                msg = f"{text_log} 실패! (등록되지 않은 장소, {request_log})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(LOG.TO_MESSAGE(request, request_user, "완료", request_log, dt))
    return {"iLocationPK": iLocationPK}

#################################################################################################################

@router.get("/top", summary="인기 장소 목록 조회", response_model=LocationListModel)
def list_top_location(request: Request, count: int, category_group_code: str = None):
    """
    리뷰의 평점이 높은 순서대로 인기 장소를 요청한 개수만큼 반환
    - **count**:int **필수 입력** (count > 0)
    - **category_group_code**:str 선택 입력 (값을 설정하지 않으면 전체)
    """
    dt = datetime.now()
    request_user = LOG.TO_REQUEST_USER(request)
    logger.info(LOG.TO_MESSAGE(request, request_user, "요청", f"TOP {count}:{category_group_code}" if category_group_code else f"TOP {count}"))
    if (count <= 0):
        msg = f"count 값은 0보다 커야 합니다. (count:{count})"
        logger.error(LOG.TO_MESSAGE(request, request_user, "실패!", msg, dt))
        raise HTTPException(status_code=400, detail=msg)
    location_model_list = []
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationReviewView.TO_SELECT_TOP_LIST_QUERY(count, category_group_code))
            rows_tuple = cursor.fetchall()
            for row_tuple in rows_tuple:
                result = DB.EXECUTE(cursor, LocationTable.TO_SELECT_MODEL_QUERY(row_tuple[0]))
                row_tuple = cursor.fetchone()
                location_model_list.append(LocationTable.TO_MODEL(row_tuple))
    logger.info(LOG.TO_MESSAGE(request, request_user, "완료", f"TOP {len(location_model_list)}", dt))
    return LocationListModel(location_list=location_model_list)
