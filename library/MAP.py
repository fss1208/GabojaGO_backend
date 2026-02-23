from models.location_model import KakaoMapSearchRequestModel
from models.location_model import LocationModel

import requests
import logging
import json
import os

logger = logging.getLogger(__name__)

class KAKAO_MAP:

    @staticmethod
    def SEARCH_KEYWORD(search_param: KakaoMapSearchRequestModel):
        KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        model_dict = search_param.model_dump()
        logger.debug(f"BEFORE {model_dict}")
        params = {k: v for k, v in model_dict.items() if v is not None}
        while (True):
            logger.debug(f"AFTER {params}")
            response_dict = requests.get(url, headers=headers, params=params).json()
            logger.debug(f"RESPONSE {json.dumps(response_dict, indent=4, ensure_ascii=False)}")
            result_dict = {}
            for i, loc_dict in enumerate(response_dict["documents"]):
                location_model = LocationModel(
                    iPK=int(loc_dict["id"]),
                    strName=loc_dict["place_name"],
                    strGroupCode=loc_dict["category_group_code"],
                    strGroupName=loc_dict["category_group_name"],
                    strGroupDetail=loc_dict["category_name"],
                    strAddress=loc_dict["address_name"],
                    strPhone=loc_dict["phone"],
                    strLink=loc_dict["place_url"],
                    chCategory=KAKAO_MAP.TO_CATEGORY(loc_dict["category_group_code"]),
                    ptLongitude=loc_dict["x"],
                    ptLatitude=loc_dict["y"]
                )
                model_dict = location_model.model_dump()
                result_dict[str(i)] = model_dict
            if (response_dict["meta"]["is_end"]):
                break
            params["page"] = params.get("page", 1) + 1
            if (params["page"] > 45):
                break
        logger.debug(f"RESULT {json.dumps(result_dict, indent=4, ensure_ascii=False)}")
        return result_dict

    @staticmethod
    def TO_CATEGORY(group_code: str) -> str:
        if (group_code):
            if (group_code == "AD5"): # 숙박
                return "L"
            elif (group_code == "FD6") or (group_code == "CE7"): # FD6:음식점, CE7:카페
                return "F"
            elif (group_code == "PK6") or (group_code == "OL7") or (group_code == "SW8"): # PK6:주차장, OL7:주유소, SW8:지하철역
                return "T"
            else:
                return "E"
        return "E"
