import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.loader import load_personal_notes

def run_ingestion():
    # 1. 데이터 로드: 아까 만든 loader 활용
    print("📂 개인 메모 데이터를 불러오는 중...")
    raw_notes = load_personal_notes("./data/personal")
    
    if not raw_notes:
        print("❌ 불러올 메모가 없습니다. data/personal 폴더를 확인해주세요.")
        return

    # 2. 텍스트 분할 (Chunking): 사고의 맥락을 보존하기 위해 적절한 크기로 자릅니다.
    # 500자 단위로 자르되, 앞뒤 50자씩 겹치게(overlap) 하여 문맥 끊김을 방지합니다.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    all_chunks = []
    all_metadatas = []
    
    for note in raw_notes:
        chunks = text_splitter.split_text(note["page_content"])
        all_chunks.extend(chunks)
        # 각 조각(Chunk)마다 원본 파일의 날짜와 제목 정보를 복사합니다.
        all_metadatas.extend([note["metadata"]] * len(chunks))

    # 3. 임베딩 모델 설정: 한국어와 다국어에 강한 BAAI/bge-m3 모델을 사용합니다.
    print("🧠 텍스트를 숫자로 변환(Embedding) 중... (CUDA 가속 사용)")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cuda'} # GPU 활용
    )

    # 4. 벡터 DB 구축 및 저장: 로컬 폴더(chroma_db)에 저장합니다.
    print(f"💾 {len(all_chunks)}개의 데이터 조각을 Vector DB에 저장합니다...")
    vector_db = Chroma.from_texts(
        texts=all_chunks,
        embedding=embeddings,
        metadatas=all_metadatas,
        persist_directory="./chroma_db" # .gitignore에서 제외한 경로
    )
    
    print("✨ 개인 지식 베이스(Vector DB) 구축이 완료되었습니다!")
    print(f"💾 저장된 데이터 개수: {len(vector_db.get())}개")

if __name__ == "__main__":
    run_ingestion()
    print("✅ 데이터 인제스션 완료!")
