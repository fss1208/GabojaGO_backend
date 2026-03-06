import boto3
from botocore.client import Config

import logging
logger = logging.getLogger(__name__)

class CloudFlare:
    #
    def __init__(self, account_id: str, access_key: str, secret_key: str, bucket_name: str):
        self.account_id = account_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.endpoint_url = f'https://{account_id}.r2.cloudflarestorage.com' # Cloudflare R2 엔드포인트 URL
        # S3 클라이언트 생성 (R2는 S3 호환 API를 사용)
        self.s3 = boto3.client(
            service_name='s3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='auto', # R2는 region을 'auto'로 설정
            config=Config(signature_version='s3v4')
        )
    #
    def upload_file(self, local_file: str, remote_file: str):
        """파일 업로드"""
        try:
            self.s3.upload_file(local_file, self.bucket_name, remote_file)
            logger.info(f"UPLOAD: {local_file} > {self.bucket_name}/{remote_file}")
        except Exception as e:
            logger.error(f"UPLOAD FAILED!: {e}")
    #
    def download_file(self, remote_file: str, local_file: str):
        """파일 다운로드"""
        try:
            self.s3.download_file(self.bucket_name, remote_file, local_file)
            logger.info(f"DOWNLOAD: {self.bucket_name}/{remote_file} > {local_file}")
        except Exception as e:
            logger.error(f"DOWNLOAD FAILED!: {e}")
    #
    def get_file_list(self, path: str="") -> list[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=path)
        file_list = []
        if 'Contents' in response:
            logger.info(f"--- {self.bucket_name} 버킷의 파일 목록 ---")
            for obj in response['Contents']:
                file_list.append(obj['Key'])
                logger.debug(f"파일명: {obj['Key']}, 크기: {obj['Size']} bytes")
        else:
            logger.debug("버킷이 비어있습니다.")
        return file_list
    #
    def get_folder_list(self, path: str="") -> list[str]:
        """
        prefix: 검색을 시작할 경로 (예: "photos/" 또는 루트의 경우 "")
        """
        # Delimiter를 '/'로 설정하면 공통된 경로를 'CommonPrefixes'로 그룹화해줍니다.
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=path, Delimiter='/')
        folder_list = []
        # CommonPrefixes 안에 폴더 형태의 경로들이 담깁니다.
        if 'CommonPrefixes' in response:
            for item in response['CommonPrefixes']:
                # 'images/' 처럼 끝에 '/'가 붙은 폴더명 추출
                folder_list.append(item['Prefix'])
        return folder_list
    #
    def delete_file(self, remote_target: str):
        """파일 삭제"""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=remote_target)
            logger.info(f"DELETE: {self.bucket_name}/{remote_target}")
        except Exception as e:
            logger.error(f"DELETE FAILED!: {e}")
    #
    def delete_folder(self, folder_path: str):
        # 폴더 경로는 반드시 '/'로 끝나야 정확합니다.
        if not folder_path.endswith('/'):
            folder_path += '/'
        # 삭제할 파일 목록 찾기
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=folder_path)
        delete_file_list = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    delete_file_list.append({'Key': obj['Key']})
        # 파일이 있다면 일괄 삭제 (최대 1,000개씩 가능)
        if delete_file_list:
            # 1,000개 단위로 끊어서 삭제 처리
            for i in range(0, len(delete_file_list), 1000):
                self.s3.delete_objects(Bucket=self.bucket_name, Delete={'Objects': delete_file_list[i:i+1000]})
            logger.info(f"DELETE: {self.bucket_name}/{folder_path} 내 {len(delete_file_list)}개의 파일 삭제")
        else:
            logger.info("삭제할 파일이 없습니다.")
    #
    def is_exist(self, remote_target: str) -> bool:
        """파일 존재 여부 확인"""
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=remote_target)
            return True
        except Exception as e:
            logger.error(f"FILE NOT FOUND!: {e}")
            return False

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    account_id = os.getenv("CF_ACCOUNT_ID")
    access_key = os.getenv("CF_ACCESS_KEY")
    secret_key = os.getenv("CF_SECRET_KEY")
    bucket_name = os.getenv("CF_BUCKET_NAME")
    cf = CloudFlare(account_id, access_key, secret_key, bucket_name)
    #
    path = "C:/SeSAC_AI_3rd/project/samples"
    file = "20260110_145834_10.webp"
    # 파일을 R2에 업로드
    # cf.upload_file(f"{path}/{file}", f"images/{file}") 
    # R2의 파일을 내 컴퓨터에 다운로드
    # cf.download_file(file, f"{path}/download_{file}")
    # 파일 삭제
    # cf.delete_file(file)
    # 폴더 삭제
    # cf.delete_folder("images/")
    # print(cf.get_only_folders())
    print(cf.get_file_list())
    print(cf.get_folder_list())
