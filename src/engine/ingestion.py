import os
from src.config import (
    NOTES_PATH,
    DB_PATH,
    EMBEDDING_MODEL,
    DEVICE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_DEVICE_STATUS,
    INGESTION_STATUS_MESSAGES,
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.loader import load_personal_notes

def _get_embedding_status(device: str) -> str:
    normalized = (device or "").lower()
    
    if "cuda" in normalized:
        return EMBEDDING_DEVICE_STATUS["cuda"]
    if "mps" in normalized:
        return EMBEDDING_DEVICE_STATUS["mps"]
    if "cpu" in normalized:
        return EMBEDDING_DEVICE_STATUS["cpu"]
    return f"{device} 사용"

def run_ingestion():
    # 1. 데이터 로드: loader.py를 통해 해당 경로의 모든 마크다운을 읽어옴
    print(INGESTION_STATUS_MESSAGES["load_notes"].format(notes_path=NOTES_PATH))
    loaded_notes = load_personal_notes(NOTES_PATH)
    
    if not loaded_notes:
        print(INGESTION_STATUS_MESSAGES["no_notes"].format(notes_path=NOTES_PATH))
        return
    
    # 2. 텍스트 분할 (Chunking): 사고의 맥락을 보존하기 위해 적절한 크기로 자름
    # 500자 단위로 자르되, 앞뒤 50자씩 겹치게(overlap) 하여 문맥 끊김을 방지
    # 분할 시 Document 객체를 직접 사용하여 메타데이터 자동 복사
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        )
    # split_documents를 사용하면 metadata를 만들 필요가 없음
    all_splitter = text_splitter.split_documents(loaded_notes)

    # 3. 임베딩 모델 설정: 환경 변수 사용
    embedding_status = _get_embedding_status(DEVICE)
    print(INGESTION_STATUS_MESSAGES["embedding"].format(device_status=embedding_status))
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': DEVICE} # GPU 활용
    )

    # 4. 벡터 DB 구축 및 저장
    # 기존 DB가 있으면 로드
    if os.path.exists(DB_PATH):
        print(
            INGESTION_STATUS_MESSAGES["load_existing_db"].format(
                chunk_count=len(all_splitter)
            )
        )
        vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        vector_db.add_documents(documents=all_splitter)
    # 기존 DB가 없으면 새로 생성
    else:
        print(
            INGESTION_STATUS_MESSAGES["create_new_db"].format(
                chunk_count=len(all_splitter)
            )
        )
        vector_db = Chroma.from_documents(
            documents=all_splitter,
            embedding=embeddings,
            persist_directory=DB_PATH # .gitignore에서 제외한 경로
        )
    
    print(INGESTION_STATUS_MESSAGES["build_complete"])

    # ._collection.count()를 사용하면 데이터를 불러오지 않고 숫자만 빠르게 가져옴
    chunk_count = vector_db._collection.count()
    print(INGESTION_STATUS_MESSAGES["saved_chunk_total"].format(chunk_count=chunk_count))

if __name__ == "__main__":
    run_ingestion()
    print(INGESTION_STATUS_MESSAGES["ingestion_complete"])
