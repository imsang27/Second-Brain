import os
import warnings
from dotenv import load_dotenv

# 1. 시스템 환경 설정
load_dotenv()

USER_NAME = os.getenv("USER_NAME", "사용자")

# 보안 및 라이브러리 경고 제어
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")
os.environ["TOKENIZERS_PARALLELISM"] = os.getenv("TOKENIZERS_PARALLELISM", "false")
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = os.getenv("HF_HUB_DISABLE_PROGRESS_BARS", "1")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 2. 하드웨어 및 모델 설정
DEVICE = os.getenv("DEVICE", "cuda")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
HASH_ALGORITHM = "sha512"

# 3. 데이터 및 경로 설정
NOTES_PATH = os.getenv("NOTES_PATH")
DB_PATH = os.getenv("DB_PATH", "./chroma_db")
FILE_EXTENSIONS = (".md", ".txt")
DATE_FORMAT = "%Y-%m-%d"

# 4. RAG 상세 파라미터
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", 3))

# RAG 질의용 시스템 프롬프트 (ChatPromptTemplate: user_name, source_documents, question)
RAG_PROMPT_TEMPLATE = """당신은 {user_name}님의 '두 번째 두뇌'예요.
    제공된 메모 내용과 해당 메모의 #태그 정보를 참고해서 친절하게 답변해주세요.
    태그가 겹치는 메모들은 서로 강한 연관성이 있음을 인지해주세요.
    메모에 없는 내용은 모른다고 솔직히 답해주세요.
    
    # 참고할 메모 내용 (태그 포함):
    {source_documents}
    
    # 질문:
    {question}
    
    답변:"""
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# ChromaDB(SQLite)의 SQL 변수 및 배치 제한을 고려한 안전 수치입니다.
LOAD_BATCH_SIZE = 10000  # 한 번에 가져올 메타데이터 개수
SAVE_BATCH_SIZE = 5000  # 한 번에 저장할 조각(Chunk) 개수

# 5. 통합 상태 메시지 (STATUS_MESSAGES)
STATUS_MESSAGES = {
    # --- [데이터 로드 & 읽기] ---
    "loading_start": "📂 {notes_path}에서 {user_name}님의 소중한 기록들을 하나하나 읽어보고 있어요{dots}",
    "found_updates": "✨ 찾았다! 새로 써주신 기록 {file_count}개를 발견했어요. 얼른 공부할게요!",
    "file_error": "😴 아이쿠, 깜빡 졸아서 ({filename}) 내용을 읽지 못했어요..\n이유: {e}",
    "no_notes": "❓ 어라? {notes_path} 폴더가 텅 비어있네요. {user_name}님의 생각을 여기 채워주시면 제가 열심히 공부할게요!",
    
    # --- [중복 체크 & 필터링] ---
    "checking_sync": "🔎 이미 알고 있는 내용인지 제 기억이랑 꼼꼼하게 맞춰보는 중이에요{dots}",
    "all_synced": "💯 휴, 이미 다 알고 있는 내용들이네요! 지금 상태로도 충분히 똑똑해요.",
    "db_not_found": "⚠️ 음.. 아직 {user_name}님을 잘 모르겠어요. 어떤 일들이 있었는지 알려주세요!",
    
    # --- [임베딩 & 분할 & 저장] ---
    "process_start": "✂️ 기록이 조금 길어서 이해하기 좋게 {chunk_size}자 단위로 나누고 있어요!",
    "embedding": "🧠 글자를 숫자로 바꿔서 장기 기억 속에 새기고 있어요. ({device_status} 두뇌 풀가동!)",
    "saving_data": "✏️ 공부 중! {chunk_count}개의 새로운 기억 조각들을 머릿속에 잘 기억할게요{dots}",
    "build_complete": "💾 공부 끝! {user_name}님의 '두 번째 두뇌'가 이제 훨씬 더 똑똑해졌어요!",
    "recent_update_file": "\n📖 이번에 새로 공부할 파일 목록이에요\n{recent_update_file}",
    "new_chunk": "📝 이번에 {new_chunk}개의 새로운 지식 조각을 배웠어요!",
    "saved_chunk_total": "✅ 총 {total_chunk}개의 기억 조각들을 머릿속 깊은 곳에 잘 간직할게요.",

    # --- [검색 & 대화 관련] ---
    "start_engine": "\n🧠 {user_name}님 전용 두뇌 가동! 무엇이든 물어보세요!\n(나가려면 'q'나 'exit'를 누르면 돼요!)",
    "searching": "🔍 {user_name}님의 메모들을 뒤적거리는 중{dots}",
    "user_prompt": "\n👤 어떤 게 궁금하세요?: ",
    "bot_answer": "\n🤖 제가 생각한 대답이에요:\n{answer}",
    "source_header": "\n📍 아래 기록들을 참고해서 대답했어요!\n",
    "source_item": "   - {idx}. {title} ({date})\n\t#태그: {tags}",
    "error_occurred": "❌ 으악, 적어둔 종이를 잃었어요.. 다시 물어봐 주실래요?\n에러: {e}"
}

# 장치 상태 매핑 (임베딩 메시지용)
EMBEDDING_DEVICE_STATUS = {
    "cuda": "CUDA 가속 사용",
    "mps": "MPS 가속 사용",
    "cpu": "CPU 사용",
}

print(f"⚙️ 설정 로드 완료: {DEVICE} 장치 사용 중")