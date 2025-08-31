import os
import shutil
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dependencies import parse_dashboard_form
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import Base, DashboardItem
from schemas import DashboardItemCreate, DashboardItemResponse, SearchResults
from search_service import SearchService
from settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 설정 및 데이터베이스 초기화
settings = Settings()
DATABASE_URL = settings.async_database_url

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# fastapi의 생명주기
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션의 생명주기를 관리한다.

    Args:
        app (FastAPI): FastAPI 애플리케이션 인스턴스

    Yields:
        None: 컨텍스트가 유지되는 동안 애플리케이션 실행
    """
    app.state.search = SearchService(settings.es_host, settings.es_port)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # 종료 시 정리 작업이 필요하면 여기에 추가
    app.state.search.close()


async def save_upload_file(upload_file: UploadFile, destination: str):
    """비동기적으로 업로드된 파일을 지정된 경로에 저장"""

    def write_file():
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

    await run_in_threadpool(write_file)
    upload_file.file.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 정적 파일 마운트
os.makedirs("uploads", exist_ok=True)
# '/uploads' 경로로 요청이 오면 'uploads' 디렉터리의 파일을 제공
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# API 엔드포인트
@app.post("/items", response_model=DashboardItemResponse, status_code=201)
async def create_item(
    request: Request,
    payload_and_image: tuple[DashboardItemCreate, UploadFile | None] = Depends(
        parse_dashboard_form
    ),
):
    """새로운 대시보드 아이템을 생성한다."""
    payload, image = payload_and_image
    now_utc = datetime.now(timezone.utc)
    saved_path = None

    # 이미지가 첨부된 경우, 고유한 파일 이름으로 서버에 저장
    if image is not None and getattr(image, "filename", None):
        ext = os.path.splitext(image.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        saved_path = f"uploads/{unique_name}"
        await save_upload_file(image, saved_path)

    # 데이터베이스 세션을 사용하여 아이템을 저장
    async with AsyncSessionLocal() as session:
        db_item = DashboardItem(
            title=payload.title,
            description=payload.description,
            image_path=saved_path,
            created_at=now_utc,
        )
        session.add(db_item)
        await session.commit()

        # DB에서 자동 생성된 ID 등을 로드
        await session.refresh(db_item)

        es_doc = {
            "title": payload.title,
            "description": payload.description,
            "created_at": now_utc.isoformat(),
        }
        if saved_path:
            es_doc["image_path"] = saved_path

        # Elasticsearch 색인
        request.app.state.search.index_item(db_item.id, es_doc)

        return DashboardItemResponse(
            id=db_item.id,
            title=db_item.title,
            description=db_item.description,
            image_path=db_item.image_path,
            created_at=db_item.created_at,
        )


@app.get("/search", response_model=SearchResults)
async def search_items(query: str, request: Request):
    """Elasticsearch에서 아이템 검색"""

    # Cache miss -> query Elasticsearch
    try:
        result = await run_in_threadpool(request.app.state.search.search_items, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    hits = []
    for hit in result:
        src = hit.get("_source", {})
        hits.append(DashboardItemResponse(**src, id=int(hit.get("_id", 0))))

    return SearchResults(results=hits)
