from models.location_model import LocationModel, KakaoMapSearchRequestModel

import requests
import logging
import json
import os

logger = logging.getLogger(__name__)

class KakaoMAP:

    @staticmethod
    def search_keyword(search_param: KakaoMapSearchRequestModel):
        KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        model_dict = search_param.model_dump()
        logger.debug(f"BEFORE {model_dict}")
        params = {k: v for k, v in model_dict.items() if v is not None}
        logger.debug(f"AFTER {params}")
        response_dict = requests.get(url, headers=headers, params=params).json()
        result_dict = {}
        for i, loc_dict in enumerate(response_dict["documents"]):
            logger.debug(f"{type(loc_dict)} {json.dumps(loc_dict, indent=4, ensure_ascii=False)}")
            location_model = LocationModel(
                pk=0,
                id=int(loc_dict["id"]),
                longitude=loc_dict["x"],
                latitude=loc_dict["y"],
                name=loc_dict["place_name"],
                category="",
                group_name=loc_dict["category_group_name"],
                group_detail=loc_dict["category_name"],
                address=loc_dict["address_name"],
                phone=loc_dict["phone"],
                link=loc_dict["place_url"]
            )
            model_dict = location_model.model_dump()
            result_dict[str(i)] = model_dict
        return result_dict
