from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.location_table import LocationTable
from models.location_model import LocationModel
from models.location_model import KakaoMapSearchRequestModel
from library.LLM import CategoryGPT
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
def search_keyword_kakaomap(request: Request, search_param: KakaoMapSearchRequestModel):
    """
    사용자가 요청하는 키워드에 해당하는 장소를 찾아 반환 (최대 15개)
    - **query**: 필수 입력
    """
    dt = datetime.now()
    logger.info(f"{request.url.path} 요청 수신 ({search_param})")
    location_dict = KAKAO_MAP.SEARCH_KEYWORD(search_param)
    logger.info(f"{request.url.path} 처리 완료 ({LOG.TO_ESTIMATED_TIME(dt)})")
    return location_dict

@router.post("/register", summary="장소 등록")
def register_location(location_model: LocationModel):
    """
    사용자가 요청하는 장소를 등록 (장소 찾기로 전달한 정보 그대로 사용)
    """
    dt = datetime.now()
    logger.info(f"장소 등록 요청 ({location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationTable.TO_SELECT_ID_QUERY(location_model))
            if (result != 0):
                msg = f"장소 등록 실패! (이미 등록된 장소, {location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=400, detail=msg)
            result = DB.EXECUTE(cursor, LocationTable.TO_INSERT_QUERY(location_model))
            if (result != 1):
                msg = f"장소 등록 실패! (DB 등록 실패, {location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            location_model.iPK = cursor.lastrowid
            connection.commit()
    logger.info(f"장소 등록 완료 ({location_model.to_log()}, {LOG.TO_ESTIMATED_TIME(dt)})")
    return {"message": f"등록 완료 ({location_model.to_log()})"}
 
@router.post("/unregister", summary="장소 등록 취소")
def unregister_location(location_model: LocationModel):
    """
    사용자가 요청하는 장소를 등록 취소 (장소 찾기로 전달한 정보 그대로 사용)
    """
    dt = datetime.now()
    logger.info(f"장소 등록 취소 요청 ({location_model.to_log()})")
    with DB.CONNECT() as connection:
        with connection.cursor() as cursor:
            result = DB.EXECUTE(cursor, LocationTable.TO_DELETE_QUERY(location_model))
            if (result == 0):
                msg = f"장소 등록 취소 실패! (등록되지 않은 장소, {location_model.to_log()})"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            connection.commit()
    logger.info(f"장소 등록 취소 완료 ({location_model.to_log()}, {result}건 삭제, {LOG.TO_ESTIMATED_TIME(dt)})")
    return {"message": f"등록 취소 완료 ({location_model.to_log()}, {result}건 삭제)"}
