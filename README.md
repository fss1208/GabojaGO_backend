# GabojaGO Project (FastAPI Backend)

## 설치
```bash
pip install python-dotenv
pip install fastapi uvicorn
pip install pymysql
pip install pandas
pip install numpy
pip install PyJWT
pip install openai
pip install langchain
pip install langchain-openai
pip install pydantic
pip install Pillow # WebP 변환 라이브러리
pip install folium # 지도 생성 라이브러리
pip install boto3 # CloudFlare
pip install python-multipart # 파일 업로드
```

## 실행
- main : 파일 이름 (main.py)
- app : 코드 내에서 app = FastAPI()로 선언한 변수 이름
```bash
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Python Vitual Environment (venv)
```bash
source ~/SeSAC/GabojaGO_backend/venv/bin/activate
```

### Python Vitual Environment (anaconda)
```bash
C:/ProgramData/anaconda3/Scripts/activate
conda activate base
```
