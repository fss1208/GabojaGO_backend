from PIL import Image, ImageOps
import os

def convert_to_webp(input_path, output_path, quality=80):
    try:
        with Image.open(input_path) as img:
            # EXIF 회전 정보를 실제 픽셀에 적용 (회전 방지 핵심)
            img = ImageOps.exif_transpose(img)
            # RGBA(투명도 포함) 모델 유지하며 변환 가능
            img.save(output_path, "WEBP", quality=quality)
            print(f"변환 완료: {output_path}")
            # 용량 비교 출력
            original_size = os.path.getsize(input_path)
            webp_size = os.path.getsize(output_path)
            print(f"용량 변화: {original_size} -> {webp_size} bytes ({(webp_size/original_size)*100:.1f}%)")
    except Exception as e:
        print(f"에러 발생: {e}")

if (__name__ == "__main__"):
    quality = 10
    path = "C:/SeSAC_AI_3rd/project/samples"
    convert_to_webp(path + "/20260110_145834.jpg", f"{path}/20260110_145834_{quality}.webp", quality=quality)
