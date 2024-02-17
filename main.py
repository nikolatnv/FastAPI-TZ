from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import uuid
from aiofile import async_open

# Подключение к базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://root:example@postgres/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание сессии SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Директория для хранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Определение модели для таблицы файлов
class Files(Base):
    __tablename__ = "files"

    uuid = Column(String, primary_key=True, index=True)
    filename = Column(String)
    upload_date = Column(DateTime, default=datetime.now)


Base.metadata.create_all(bind=engine)

app = FastAPI()


def upload_file(db, file: UploadFile):
    file_uuid = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, file_uuid)
    with open(file_path, 'wb') as f:
        f.write(file.file.read())
    db.add(Files(uuid=file_uuid, filename=file.filename))
    db.commit()
    return {'uuid': file_uuid, 'filename': file.filename}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/v2/upload/")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return upload_file(db, file)


@app.get("/v1/find/")
async def find_files(filename: str = None, date: str = None, db: Session = Depends(get_db)):
    files = []
    files_query = db.query(Files)
    if filename:
        files_query = files_query.filter(Files.filename.startswith(filename))
    if date:
        files_query = files_query.filter(Files.upload_date == date)
    files_result = files_query.all()
    for file in files_result:
        file_info = {
            'uuid': file.uuid,
            'filename': file.filename,
            'date': file.upload_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        files.append(file_info)
    return files


@app.get("/v1/download/{uuid}")
async def download(uuid: str):
    # file_record = db.query(Files).filter(Files.uuid == uuid).first()
    file_path = os.path.join(UPLOAD_FOLDER, uuid)
    if os.path.exists(file_path):
        async with async_open(file_path, mode="rb") as file:
            content = await file.read()
        return FileResponse(content, filename=uuid)
    else:
        raise HTTPException(status_code=404, detail="File not found")
