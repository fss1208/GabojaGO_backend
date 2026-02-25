from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.location_table import LocationTable
from models.location_model import LocationModel, LocationListModel
from models.location_model import KakaoMapSearchRequestModel, LocationRequestListModel
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

@router.post("/search/keyword", summary="키워드로 장소 찾기", response_model=dict[str, LocationModel])
def search_keyword_kakaomap(search_param: KakaoMapSearchRequestModel, request: Request):
    """
    사용자가 요청하는 키워드에 해당하는 장소를 찾아 반환 (최대 15개)
    - **query**:str 필수 입력
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({search_param})")
    location_dict = KAKAO_MAP.SEARCH_KEYWORD(search_param)
    logger.info(f"{text_log} 완료 ({LOG.TO_ESTIMATED_TIME(dt)})")
    return location_dict

@router.post("/request", summary="장소 정보 요청", response_model=LocationListModel)
def request_location(request_model: LocationRequestListModel, request: Request):
    """
    AI가 생성한 일정에 포함된 장소명으로 장소 정보를 검색하여 반환
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 (len:{len(request_model.request_list)}건)")
    location_list = []
    for request_item_model in request_model.request_list:
        search_param = KakaoMapSearchRequestModel(
            query=request_item_model.place_name,
            category_group_code=request_item_model.category_group_code if request_item_model.category_group_code else None
        )
        location_dict = KAKAO_MAP.SEARCH_KEYWORD(search_param)
        for location_model in location_dict.values():
            # logger.debug(f"{place_name} : {location_model}")
            location_list.append(location_model)
            break
    logger.info(f"{text_log} 완료 (len:{len(location_list)}건, {LOG.TO_ESTIMATED_TIME(dt)})")
    return LocationListModel(location_list=location_list)

#################################################################################################################

@router.post("/register", summary="장소 등록", response_model=LocationModel)
def register_location(location_model: LocationModel, request: Request):
    """
    사용자가 요청하는 장소를 등록 (장소 찾기로 받은 정보 그대로 사용)
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationTable.TO_SELECT_ID_QUERY(location_model))
            if (result != 0):
                msg = f"{text_log} 실패! (이미 등록된 장소, {location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            result = DB.EXECUTE(cursor, LocationTable.TO_INSERT_QUERY(location_model))
            if (result != 1):
                msg = f"{text_log} 실패! (DB 등록 실패, {location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            location_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"{text_log} 완료 ({location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return location_model
 
@router.post("/unregister", summary="장소 등록 취소")
def unregister_location(location_model: LocationModel, request: Request):
    """
    사용자가 등록했던 장소를 취소
    - **LocationModel.iPK**:int **필수 입력**
    """
    dt = datetime.now()
    text_log = LOG.TO_ROUTE_TEXT(request)
    logger.info(f"{text_log} 요청 ({location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationTable.TO_DELETE_QUERY(location_model))
            if (result == 0):
                msg = f"{text_log} 실패! (등록되지 않은 장소, {location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"{text_log} 완료 ({location_model.to_log()}, {result}건 삭제, {LOG.TO_ESTIMATED_TIME(dt)})")
    return location_model
