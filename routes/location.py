from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.location_model import KakaoMapSearchRequestModel, KakaoMapSearchResponseModel
from library.LLM import CategoryGPT
from library.MAP import KakaoMAP
from library.JWT import AuthJWT

from datetime import datetime, timedelta
import logging
import json
import os

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

#################################################################################################################

@router.post("/search/keyword", summary="키워드로 장소 찾기", response_model=dict[str, KakaoMapSearchResponseModel])
def search_keyword_kakaomap(request: Request, search_param: KakaoMapSearchRequestModel, auth: HTTPAuthorizationCredentials = Depends(security)):
    dt = datetime.now()
    logger.debug(f"{request.url.path} Request Body ({search_param})")
    user_model = AuthJWT.get_user_model(auth)
    logger.debug(f"UserModel({user_model})")
    result_dict = KakaoMAP.search_keyword(search_param)
    llm = CategoryGPT()
    location_dict = {}
    for i, loc_dict in enumerate(result_dict["documents"]):
        logger.debug(f"{type(loc_dict)} {json.dumps(loc_dict, indent=4, ensure_ascii=False)}")
        chain_dict = {
            "place_name": loc_dict["place_name"],
            "category_name": loc_dict["category_name"],
            "category_group_name": loc_dict["category_group_name"]
        }
        result = llm.chain.invoke(chain_dict)
        logger.debug(f"[{type(result)}] {result}")
        location_model = KakaoMapSearchResponseModel(
            id=int(loc_dict["id"]),
            name=loc_dict["place_name"],
            longitude=loc_dict["x"],
            latitude=loc_dict["y"],
            category=result.category,
            group_name=loc_dict["category_group_name"],
            group_detail=loc_dict["category_name"],
            address=loc_dict["address_name"],
            phone=loc_dict["phone"],
            link=loc_dict["place_url"]
        )
        model_dict = location_model.model_dump()
        location_dict[str(i)] = model_dict
    logger.info(f"{(datetime.now() - dt).total_seconds() * 1000} ms")
    return location_dict
