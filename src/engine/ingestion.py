import os
from src.config import (
    USER_NAME,
    NOTES_PATH,
    DB_PATH,
    EMBEDDING_MODEL,
    DEVICE,
    LOAD_BATCH_SIZE,
    SAVE_BATCH_SIZE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_DEVICE_STATUS,
    STATUS_MESSAGES,
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.loader import load_personal_notes
from src.utils.ui_utils import start_animation

def _get_embedding_status(device: str) -> str:
    normalized = (device or "").lower()
    if "cuda" in normalized: return EMBEDDING_DEVICE_STATUS["cuda"]
    if "mps" in normalized: return EMBEDDING_DEVICE_STATUS["mps"]
    if "cpu" in normalized: return EMBEDDING_DEVICE_STATUS["cpu"]
    return f"{device} 사용"

def run_ingestion():
    # 1. 데이터 로드 애니메이션 시작
    stop_event, anim = start_animation("load")
    loaded_notes = load_personal_notes(NOTES_PATH)
    stop_event.set()
    anim.join()
    
    if not loaded_notes:
        print(STATUS_MESSAGES["no_notes"].format(notes_path=NOTES_PATH, user_name=USER_NAME))
        return
    
    # 2. 임베딩 모델 설정 및 기존 DB ID 로드
    embedding_status = _get_embedding_status(DEVICE)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': DEVICE} # GPU 활용
    )
    
    # 3. 기존 DB 로드 및 현재 저장된 파일 ID 목록 가져오기
    existing_ids = set()
    if os.path.exists(DB_PATH):
        # 애니메이션 시작! (task_type="sync")
        stop_event, anim = start_animation("sync")
        
        vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        # DB에서 기존에 저장된 모든 file_id 메타데이터를 가져옵니다.
        
        # 단, 한 번에 다 가져오지 않고 1만 개씩 끊어서 가져옵니다.
        total_chunk = vector_db._collection.count()
        
        for i in range(0, total_chunk, LOAD_BATCH_SIZE):
            # get() 함수에 limit와 offset을 사용하여 SQL 변수 제한을 피합니다.
            data = vector_db.get(
                include=['metadatas'], 
                limit=LOAD_BATCH_SIZE, 
                offset=i
            )
            batch_ids = {m.get("file_id") for m in data['metadatas'] if m.get("file_id")}
            existing_ids.update(batch_ids)
        stop_event.set()
        anim.join()
    else:
        vector_db = None
    
    # 4. 중복 제외 필터링: 이미 DB에 있는 file_id는 제외
    new_notes = [n for n in loaded_notes if n.metadata["file_id"] not in existing_ids]
    
    if not new_notes:
        print(STATUS_MESSAGES["all_synced"])
        return
    
    # 업데이트된 파일 목록 보여주기
    # metadata에서 'title'을 가져와서 줄바꿈으로 연결합니다.
    updated_files = [f"- {n.metadata['title']}" for n in new_notes]
    recent_update_file = "\n".join(updated_files)
    print(STATUS_MESSAGES["recent_update_file"].format(recent_update_file=recent_update_file))
    
    # 5. 새로운 메모만 분할 및 저장
    # 사고의 맥락을 보존하기 위해 적절한 크기로 자름
    # 500자 단위로 자르되, 앞뒤 50자씩 겹치게(overlap) 하여 문맥 끊김을 방지
    # 분할 시 Document 객체를 직접 사용하여 메타데이터 자동 복사
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    # split_documents를 사용하면 metadata를 만들 필요가 없음
    all_splitter = text_splitter.split_documents(new_notes)
    
    # 분할된 조각이 0개라면 종료
    if not all_splitter:
        print(STATUS_MESSAGES["all_synced"])
        return
    
    # 6. 임베딩(GPU 연산) 단계 애니메이션 시작
    stop_event, anim = start_animation("ingest", device_status=embedding_status)
    
    try:
        if vector_db:
            # all_splitter 리스트를 SAVE_BATCH_SIZE만큼 쪼개서 넣습니다.
            for i in range(0, len(all_splitter), SAVE_BATCH_SIZE):
                batch = all_splitter[i : i + SAVE_BATCH_SIZE]
                vector_db.add_documents(documents=batch)
        # 기존 DB가 없으면 새로 생성
        else:
            # 첫 번째 배치로 DB 객체를 생성합니다.
            initial_batch = all_splitter[:SAVE_BATCH_SIZE]
            vector_db = Chroma.from_documents(
                documents=initial_batch,
                embedding=embeddings,
                persist_directory=DB_PATH # .gitignore에서 제외한 경로
            )
            
            # 남은 배치가 있다면 추가로 넣어줍니다.
            if len(all_splitter) > SAVE_BATCH_SIZE:
                for i in range(SAVE_BATCH_SIZE, len(all_splitter), SAVE_BATCH_SIZE):
                    batch = all_splitter[i : i + SAVE_BATCH_SIZE]
                    vector_db.add_documents(documents=batch)
    
    finally:
        stop_event.set()
        anim.join()
        
    # 7. 최종 결과 출력
    print(STATUS_MESSAGES["build_complete"].format(user_name=USER_NAME))

    # 신규 습득과 전체 기억을 구분
    new_chunk = len(all_splitter)

    # ._collection.count()를 사용하면 데이터를 불러오지 않고 숫자만 빠르게 가져옴
    total_chunk = vector_db._collection.count()
    print(STATUS_MESSAGES["new_chunk"].format(new_chunk=new_chunk))
    print(STATUS_MESSAGES["saved_chunk_total"].format(total_chunk=total_chunk))

if __name__ == "__main__":
    run_ingestion()
