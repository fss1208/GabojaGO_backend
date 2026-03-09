import os, io, base64
import folium, webbrowser

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from PIL.TiffImagePlugin import IFDRational

import logging
logger = logging.getLogger(__name__)

##################################################################################################################################################

def debug_gps(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    
    print("=== 전체 EXIF 태그 ===")
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        print(f"{tag_name}({tag}): {repr(value)}")
    
    print("\n=== GPSInfo raw ===")
    for tag, value in exif_data.items():
        if TAGS.get(tag) == "GPSInfo":
            for t, v in value.items():
                print(f"  {GPSTAGS.get(t, t)}({t}): {repr(v)}")

def _get_decimal_from_dms_(dms, ref):
    def to_float(val):
        # IFDRational 명시적 처리 (float() 변환 시 NaN 가능성 차단)
        if isinstance(val, IFDRational):
            if val.denominator == 0:
                return 0.0
            return float(val.numerator) / float(val.denominator)
        # (분자, 분모) 튜플 처리
        elif isinstance(val, tuple):
            return float(val[0]) / float(val[1]) if val[1] != 0 else 0.0
        return float(val)
    degrees = to_float(dms[0])
    minutes = to_float(dms[1]) / 60.0
    seconds = to_float(dms[2]) / 3600.0
    if ref in ['S', 'W']:
        return -(degrees + minutes + seconds)
    return degrees + minutes + seconds

# def get_exif_location(image_path):
#     """
#     이미지의 파일에서 GPS 좌표 및 촬영시간을 추출하는 함수
#     """
#     try:
#         image = Image.open(image_path)
#         exif_data = image.getexif()
#         if not exif_data:
#             return None, "EXIF 데이터가 없습니다."

#         exif_info = {}
#         gps_info = {}
#         for tag, value in exif_data.items():
#             tag_name = TAGS.get(tag, tag)
#             exif_info[tag_name] = value
#             if tag_name == "GPSInfo":
#                 for t in value:
#                     sub_tag = GPSTAGS.get(t, t)
#                     gps_info[sub_tag] = value[t]

#         # 시간 정보 추출
#         shot_dt_str = exif_info.get("DateTimeOriginal") or exif_info.get("DateTime")
#         shot_date_str = shot_dt_str[:10].replace(":", "-")
#         shot_time_str = shot_dt_str[11:]
#         shot_dt_str = f"{shot_date_str} {shot_time_str}"

#         if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
#             x = _get_decimal_from_dms_(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
#             y = _get_decimal_from_dms_(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
#             if x is None or y is None:
#                 return {"x": None, "y": None, "dt": shot_dt_str, "error": "GPS 변환 실패"}, ""
#             return {"x": x, "y": y, "dt": shot_dt_str}, ""
#         else:
#             return {"x": None, "y": None, "dt": shot_dt_str, "error": "GPS 정보가 없습니다."}, ""
#     except Exception as e:
#         return None, str(e)

import exifread

def get_exif_location(image_path):
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        if not tags:
            return None, "EXIF 데이터가 없습니다."

        # 시간 정보
        shot_dt_str = str(tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime", ""))
        if shot_dt_str:
            shot_date_str = shot_dt_str[:10].replace(":", "-")
            shot_time_str = shot_dt_str[11:]
            shot_dt_str = f"{shot_date_str} {shot_time_str}"

        lat_tag = tags.get("GPS GPSLatitude")
        lon_tag = tags.get("GPS GPSLongitude")
        lat_ref = str(tags.get("GPS GPSLatitudeRef", "N"))
        lon_ref = str(tags.get("GPS GPSLongitudeRef", "E"))
        if not lat_tag or not lon_tag:
            return {"x": None, "y": None, "dt": shot_dt_str, "error": "GPS 정보가 없습니다."}, ""

        def ifd_to_decimal(tag, ref):
            vals = tag.values
            def safe_div(num, den):
                return float(num) / float(den) if den != 0 else 0.0
            degrees = safe_div(vals[0].num, vals[0].den)
            minutes = safe_div(vals[1].num, vals[1].den) / 60.0
            seconds = safe_div(vals[2].num, vals[2].den) / 3600.0
            result = degrees + minutes + seconds
            return -result if ref in ['S', 'W'] else result

        x = ifd_to_decimal(lon_tag, lon_ref)
        y = ifd_to_decimal(lat_tag, lat_ref)
        if (x == 0.0) and (y == 0.0):
            return {"x": None, "y": None, "dt": shot_dt_str, "error": "GPS 값이 비어있습니다."}, ""

        return {"x": x, "y": y, "dt": shot_dt_str}, ""

    except Exception as e:
        return None, str(e)

##################################################################################################################################################

def create_map_with_photo(lat, lng, shot_time, image_path):
    # 1. 지도 생성
    m = folium.Map(location=[lat, lng], zoom_start=15)
    # 2. 이미지 리사이징 및 Base64 인코딩 (속도 및 렌더링 최적화)
    try:
        with Image.open(image_path) as img:
            # 원본 비율 유지하며 최대 너비 600px로 리사이즈
            img.thumbnail((600, 600))
            # 이미지를 바이너리 스트림으로 저장
            buffered = io.BytesIO()
            img_format = img.format if img.format else 'JPEG'
            img.save(buffered, format=img_format)
            encoded_string = base64.b64encode(buffered.getvalue()).decode()
            mime_type = f"image/{img_format.lower()}"
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return None
    # 3. 팝업에 들어갈 HTML
    # 이미지가 깨지지 않도록 스타일 조정
    time_html = f"<p style='margin: 5px 0; font-size: 13px;'><b>촬영 시간:</b> {shot_time}</p>" if shot_time else ""
    html = f"""
        <div style="width: 100%; text-align: center;">
            <h4 style="margin-bottom: 5px;">사진 위치</h4>
            <p style="font-size: 11px; color: gray; margin-bottom: 5px;">{os.path.basename(image_path)}</p>
            {time_html}
            <img src="data:{mime_type};base64,{encoded_string}" 
                 style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); margin-top: 5px;">
        </div>
    """
    # 4. 마커 추가 (IFrame 대신 직접 HTML 삽입 시도)
    popup = folium.Popup(html, max_width=400)
    folium.Marker([lat, lng], popup=popup, tooltip="사진 보기를 위해 클릭하세요").add_to(m)
    # 5. 지도 저장 및 열기
    output_file = "photo_location_map.html"
    m.save(output_file)
    return os.path.abspath(output_file)

##################################################################################################################################################

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    path = "C:/SeSAC_AI_3rd/project/samples"
    file = "20260207_140127.jpg"
    file_path = f"{path}/{file}"
    logger.info(file_path)
    if (os.path.exists(file_path)):
        info = get_exif_location(file_path)
        if isinstance(info, dict) and info.get("x") is not None:
            shot_time = info.get("dt")
            x, y = info["x"], info["y"]
            print(f"경도({type(x)}): {x}")
            print(f"위도({type(y)}): {y}")
            print(f"촬영 시간({type(shot_time)}): {shot_time}")
            map_path = create_map_with_photo(y, x, shot_time, file_path)
            print(f"지도 생성: {map_path}")
            webbrowser.open(f"file:///{map_path.replace(os.sep, '/')}")
        else:
            print(f"오류: {info}")
    else:
        print(f"파일을 찾을 수 없습니다! ({file_path})")
