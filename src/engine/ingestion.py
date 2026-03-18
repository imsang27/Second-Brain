import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.loader import load_personal_notes

load_dotenv() # 환경 변수 로드

# 환경 변수에서 실제 메모 경로 가져오기
NOTES_PATH = os.getenv("NOTES_PATH")
DB_PATH = os.getenv("DB_PATH", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
DEVICE = os.getenv("DEVICE", "cuda")

def run_ingestion():
    # 1. 데이터 로드: loader.py를 통해 해당 경로의 모든 마크다운을 읽어옴
    print(f"📂 {NOTES_PATH}에서 개인 메모 읽는 중...")
    loaded_notes = load_personal_notes(NOTES_PATH)
    
    if not loaded_notes:
        print(f"❌ 불러올 메모가 없습니다.\n{NOTES_PATH} 폴더를 확인해주세요.")
        return

    # 2. 텍스트 분할 (Chunking): 사고의 맥락을 보존하기 위해 적절한 크기로 자름
    # 500자 단위로 자르되, 앞뒤 50자씩 겹치게(overlap) 하여 문맥 끊김을 방지
    # 분할 시 Document 객체를 직접 사용하여 메타데이터 자동 복사
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        )
    # split_documents를 사용하면 metadata를 만들 필요가 없음
    all_splitter = text_splitter.split_documents(loaded_notes)


    # 3. 임베딩 모델 설정: 환경 변수 사용
    print("🧠 텍스트를 숫자로 변환(Embedding) 중... (CUDA 가속 사용)")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': DEVICE} # GPU 활용
    )

    # 4. 벡터 DB 구축 및 저장
    print(f"💾 {len(all_splitter)}개의 데이터 조각을 Vector DB에 저장합니다...")
    vector_db = Chroma.from_documents(
        documents=all_splitter,
        embedding=embeddings,
        persist_directory=DB_PATH # .gitignore에서 제외한 경로
    )
    
    print("✨ 개인 지식 베이스(Vector DB) 구축이 완료되었습니다!")
    print(f"💾 저장된 데이터 개수: {len(vector_db.get())}개")

if __name__ == "__main__":
    run_ingestion()
    print("✅ 데이터 인제스션 완료!")
