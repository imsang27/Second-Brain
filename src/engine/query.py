import os
import sys
import time
import threading
from src.config import (
    DEVICE,
    EMBEDDING_MODEL,
    OLLAMA_MODEL,
    DB_PATH,
    RETRIEVAL_K,
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

def ask_second_brain():
    # 1. 임베딩 모델 설정
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': DEVICE} # GPU 가속 유지
    )
    
    # 2. Vector DB 로드
    if not os.path.exists(DB_PATH):
        print(STATUS_MESSAGES["db_not_found"].format(path=DB_PATH))
        return
    
    vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    # config에 정의된 RETRIEVAL_K 상수를 사용해 검색 범위 조절
    retriever = vector_db.as_retriever(search_kwargs={"k": RETRIEVAL_K})
    
    # 3. LLM 설정
    llm = OllamaLLM(model=OLLAMA_MODEL)
    
    # 4. 프롬프트 디자인: AI에게 페르소나 부여, RAG 시스템 조립 (질문 -> DB 검색 -> 답변)
    template = """당신은 {user_name}님의 '두 번째 두뇌'예요.
    제공된 메모 내용과 해당 메모의 #태그 정보를 참고해서 친절하게 답변해주세요.
    태그가 겹치는 메모들은 서로 강한 연관성이 있음을 인지해주세요.
    메모에 없는 내용은 모른다고 솔직히 답해주세요.
    
    # 참고할 메모 내용 (태그 포함):
    {source_documents}
    
    # 질문:
    {question}
    
    답변:"""
    prompt = ChatPromptTemplate.from_template(template).partial(user_name=USER_NAME)
    
    # 5. RAG 체인 생성 (답변과 출처를 동시에 반환하도록 병렬화)
    chain = RunnableParallel({
        "source_documents": retriever,
        "question": RunnablePassthrough()
    }).assign(
        answer=prompt | llm | StrOutputParser()
    )
    
    print(STATUS_MESSAGES["start_engine"].format(user_name=USER_NAME))
    
    while True:
        user_input = input(STATUS_MESSAGES["user_prompt"])
        if not user_input or user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        # 애니메이션 시작! (task_type="search")
        stop_event, anim = start_animation("search")
        
        try:
            # 2026년 방식인 invoke를 사용합니다.            
            result = chain.invoke(user_input)
            
            # 답변이 완료되면 애니메이션 중지
            stop_event.set()
            anim.join()
            
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
