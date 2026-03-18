import os
import warnings
import sys
import time
import threading
from dotenv import load_dotenv

# ========================================================================
# [중요] IMPORT 순서 가이드 (수정 시 주의)
# 1. 시스템/환경 설정: AI 라이브러리(langchain 등)가 로드되는 시점에 
#    환경 변수를 즉시 읽기 때문에, 반드시 load_dotenv()를 먼저 실행해야 합니다.
# 2. 경고 제어: 라이브러리 임포트 시 발생하는 DeprecationWarning 등을 
#    사전에 차단하기 위해 warnings 설정을 먼저 수행합니다.
# ========================================================================

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 값 가져오기 (없을 경우를 대비한 기본값 설정)
HF_TOKEN = os.getenv("HF_TOKEN")
DEVICE = os.getenv("DEVICE", "cuda")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
DB_PATH = os.getenv("DB_PATH", "./chroma_db")
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", 3))

# 시스템 환경 변수 설정 (토크나이저 데드락 방지 등)
os.environ["TOKENIZERS_PARALLELISM"] = os.getenv("TOKENIZERS_PARALLELISM", "false")
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = os.getenv("HF_HUB_DISABLE_PROGRESS_BARS", "1")

# 경고 메시지 무시 설정 (Chroma 관련 경고 등)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 무거운 AI 라이브러리는 모든 설정이 끝난 뒤 로드
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM # 2026년 최신 표준 langchain-ollama 패키지 사용
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# 점 애니메이션을 처리하는 함수입니다.
def loading_animation(stop_event):
    chars = [".  ", ".. ", "..."]
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r🔍 메모 뒤적이는 중{chars[idx % 3]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.5)
    # 작업 완료 후 줄을 깨끗하게 비웁니다.
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

def ask_second_brain():
    # 1. 임베딩 모델 설정 (ingestion.py와 동일해야 함, 환경 변수 사용)
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': DEVICE} # GPU 가속 유지
    )
    
    # 2. 구축된 Vector DB 로드
    if not os.path.exists(DB_PATH):
        print(f"❌ {DB_PATH}를 찾을 수 없습니다.")
        return

    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": RETRIEVAL_K})

    # 3. LLM 설정
    llm = OllamaLLM(model=OLLAMA_MODEL)
    
    # 4. 프롬프트 디자인: AI에게 페르소나 부여, RAG 시스템 조립 (질문 -> DB 검색 -> 답변)
    template = """당신은 ㅇㅅㅇ님의 '두 번째 두뇌'입니다.
    제공된 메모 내용과 해당 메모의 #태그 정보를 참고하여 친절하게 답변하세요.
    태그가 겹치는 메모들은 서로 강한 연관성이 있음을 인지하세요.
    메모에 없는 내용은 모른다고 솔직히 답하세요.
    
    # 참고할 메모 내용 (태그 포함):
    {source_documents}
    
    # 질문:
    {question}

    답변:"""
    prompt = ChatPromptTemplate.from_template(template)

    # 5. LCEL 체인 생성 (답변과 출처를 동시에 반환하도록 병렬화)
    chain = RunnableParallel({
        "source_documents": retriever,
        "question": RunnablePassthrough()
    }).assign(
        answer=prompt | llm | StrOutputParser()
    )

    print("\n🧠 Second Brain 가동 중...")
    print("종료하려면 'exit' 또는 'q'를 입력하세요.")

    while True:
        user_input = input("\n👤 질문: ")
        if not user_input or user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        # 애니메이션 일꾼(Thread) 시작
        stop_event = threading.Event()
        loader_thread = threading.Thread(target=loading_animation, args=(stop_event,))
        loader_thread.start()

        try:
            # 2026년 방식인 invoke를 사용합니다.            
            result = chain.invoke(user_input)

            # 답변이 완료되면 애니메이션 중지
            stop_event.set()
            loader_thread.join()

            print(f"\n🤖 답변: {result['answer']}") # result가 {'source_documents': [...], 'answer': '...'} 형태의 딕셔너리로 반환됨

            # 📍 참고한 메모(Source Documents) 출력
            print("\n📍 참고한 메모:")
            for i, doc in enumerate(result['source_documents']):
                title = doc.metadata.get('title', '제목 없음')
                date = doc.metadata.get('date', '날짜 미상')
                tags = doc.metadata.get('tags', '태그 없음')
                print(f"   {i+1}. {title} ({date}) [태그: {tags}]")

        except Exception as e:
            stop_event.set()
            loader_thread.join()
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    ask_second_brain()
