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

print(f"⚙️ 설정 로드 완료: {DEVICE} 장치 사용 중")