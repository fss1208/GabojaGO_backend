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
