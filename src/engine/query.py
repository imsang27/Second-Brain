import os
from src.config import (
    DEVICE,
    EMBEDDING_MODEL,
    OLLAMA_MODEL,
    DB_PATH,
    RAG_PROMPT_TEMPLATE,
    RETRIEVAL_K,
    SEARCH_TYPE,
    FETCH_K,
    STATUS_MESSAGES,
    USER_NAME,
)

# ========================================================================
# [중요] IMPORT 순서 가이드 (수정 시 주의)
# 1. 시스템/환경 설정: AI 라이브러리(langchain 등)가 로드되는 시점에 
#    환경 변수를 즉시 읽기 때문에, 반드시 load_dotenv()를 먼저 실행해야 합니다.
# 2. 경고 제어: 라이브러리 임포트 시 발생하는 DeprecationWarning 등을 
#    사전에 차단하기 위해 warnings 설정을 먼저 수행합니다.
# ========================================================================

# 무거운 AI 라이브러리는 모든 설정이 끝난 뒤 로드
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM # 2026년 최신 표준 langchain-ollama 패키지 사용
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from src.utils.ui_utils import start_animation

# 1. 임베딩 모델 설정
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': DEVICE} # GPU 가속 유지
)

def ask_second_brain(web_input=None): # web_input 인자 추가
    
    # 2. Vector DB 로드
    if not os.path.exists(DB_PATH):
        error_msg = STATUS_MESSAGES["db_not_found"].format(path=DB_PATH)
        if web_input is not None: return error_msg, [] # 웹 응답용
        print(error_msg) # 터미널용
        return
    
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    # config에 정의된 RETRIEVAL_K 상수를 사용해 검색 범위 조절
    retriever = vector_db.as_retriever(
        search_type=SEARCH_TYPE, # 유사도만 보지 않고 '다양성'을 고려합니다.
        search_kwargs={
            "k": RETRIEVAL_K,
            "fetch_k": FETCH_K,
        }
    )
    # 3. LLM 설정
    llm = OllamaLLM(model=OLLAMA_MODEL)
    
    # 4. 프롬프트 디자인: AI에게 페르소나 부여, RAG 시스템 조립 (질문 -> DB 검색 -> 답변)
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE).partial(user_name=USER_NAME)
    
    # 5. RAG 체인 생성 (답변과 출처를 동시에 반환하도록 병렬화)
    chain = RunnableParallel({
        "source_documents": retriever,
        "question": RunnablePassthrough()
    }).assign(
        answer=prompt | llm | StrOutputParser()
    )
    
    # 웹(Gradio)에서 호출한 경우
    if web_input is not None:
        try:
            # invoke 실행 시 터미널 로그를 확인하기 위해 출력문을 추가
            print(f"🔍 질문 수신 완료: {web_input}")
            result = chain.invoke(web_input)
            print(f"✅ 답변 생성 완료: {result['answer']}")
            # app.py에서 기대하는 (답변, 출처문서) 튜플 형태로 반환합니다.
            return result['answer'], result['source_documents']
        except Exception as e:
            return STATUS_MESSAGES["error_occurred"].format(e=e), []
    
    print(STATUS_MESSAGES["start_engine"].format(user_name=USER_NAME))

    # 터미널에서 직접 실행한 경우 (기존 루프 유지)
    while True:
        terminal_input = input(STATUS_MESSAGES["user_prompt"])
        if not terminal_input or terminal_input.lower() in ['exit', 'quit', 'q']:
            break
        
        # 애니메이션 시작! (task_type="search")
        stop_event, anim = start_animation("search")
        
        try:
            # AI 추론 실행: 2026년 방식인 invoke를 사용합니다.            
            result = chain.invoke(terminal_input)
            
            # 답변이 완료되면 애니메이션 중지
            stop_event.set()
            anim.join()
            
            # 1. 딕셔너리 전체 구조 확인 (디버깅용)
            print(f"DEBUG: {result}")
            
            # 2. 강제로 답변 데이터만 출력해보기
            print(f"\n[직접 출력] {result['answer']}")

            # 답변 출력
            print(STATUS_MESSAGES["bot_answer"].format(answer=result['answer'])) # result가 {'source_documents': [...], 'answer': '...'} 형태의 딕셔너리로 반환됨
            
            # 📍 참고한 메모(Source Documents) 출력
            print(STATUS_MESSAGES["source_header"])
            for i, doc in enumerate(result['source_documents']):
                print(STATUS_MESSAGES["source_item"].format(
                    idx=i+1,
                    title=doc.metadata.get('title', '제목 없음'),
                    date=doc.metadata.get('date', '날짜 미상'),
                    tags=doc.metadata.get('tags', '태그 없음')
                ))
        
        except Exception as e:
            stop_event.set()
            anim.join()
            print(STATUS_MESSAGES["error_occurred"].format(e=e))

if __name__ == "__main__":
    ask_second_brain()
