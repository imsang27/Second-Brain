import os
import warnings
from dotenv import load_dotenv

# 1. 시스템 전체에 환경 변수 로드
load_dotenv()

# 2. 보안 및 시스템 설정 적용
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")
os.environ["TOKENIZERS_PARALLELISM"] = os.getenv("TOKENIZERS_PARALLELISM", "false")
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = os.getenv("HF_HUB_DISABLE_PROGRESS_BARS", "1")

# 3. 경고 메시지 일괄 차단
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 4. 다른 파일에서 불러다 쓸 설정값들 (전역 변수)
NOTES_PATH = os.getenv("NOTES_PATH")
DB_PATH = os.getenv("DB_PATH", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
DEVICE = os.getenv("DEVICE", "cuda")
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", 3))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# 5. 상태/출력 메시지 설정
EMBEDDING_DEVICE_STATUS = {
    "cuda": "CUDA 가속 사용",
    "mps": "Apple Silicon(MPS) 가속 사용",
    "cpu": "CPU 사용",
}

INGESTION_STATUS_MESSAGES = {
    "load_notes": "📂 {notes_path}에서 개인 메모 읽는 중...",
    "no_notes": "❌ 불러올 메모가 없습니다.\n{notes_path} 폴더를 확인해주세요.",
    "embedding": "🧠 텍스트를 숫자로 변환(Embedding) 중... ({device_status})",
    "load_existing_db": "🔄 기존 Vector DB를 로드하여 새로운 데이터 {chunk_count}개를 추가합니다...",
    "create_new_db": "💾 새로운 Vector DB를 생성하여 {chunk_count}개의 조각을 저장합니다...",
    "build_complete": "✨ 개인 지식 베이스(Vector DB) 구축이 완료되었습니다!",
    "saved_chunk_total": "💾 저장된 데이터 조각(Chunks) 총합: {chunk_count}개",
    "ingestion_complete": "✅ 데이터 인제스션 완료!",
}

print(f"⚙️ 설정 로드 완료: {DEVICE} 장치 사용 중")