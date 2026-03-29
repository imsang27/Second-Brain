# src/app.py
import gradio as gr
import os
from src.config import USER_NAME, STATUS_MESSAGES, DB_PATH
from src.engine.ingestion import run_ingestion
# query.py의 로직을 함수화하여 호출한다고 가정합니다.
from src.engine.query import ask_second_brain 

# 1. 지식 업데이트 실행 함수 (Ingestion)
def start_learning():
    try:
        # ingestion.py 내부에서 이미 애니메이션과 STATUS_MESSAGES를 출력합니다.
        run_ingestion()
        # 완료 시 상혁님을 위한 최종 성공 메시지 반환
        return STATUS_MESSAGES["build_complete"].format(user_name=USER_NAME)
    except Exception as e:
        return STATUS_MESSAGES["error_occurred"].format(e=e)

# 2. 질문 답변 실행 함수 (Query)
def chat_with_brain(message, history):
    # 메시지가 비어있는 경우 방어
    if not message.strip():
        return "", history
    
    # DB 존재 여부 체크
    if not os.path.exists(DB_PATH):
        response = STATUS_MESSAGES["db_not_found"].format(user_name=USER_NAME)
        # Gradio 6.x 형식으로 추가
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return "", history

    try:
        # query.py의 로직을 통해 AI 답변과 참고 문헌 리스트를 가져옵니다.
        # (ask_second_brain이 answer와 source_docs를 반환하도록 구성됨)
        answer, source_docs = ask_second_brain(message) 
        
        # 참고 기록(Source Header) 및 목록 구성
        source_text = STATUS_MESSAGES["source_header"]
        seen_sources = set() # 이미 표시한 파일명을 저장
        idx = 1

        for doc in source_docs:
            title = doc.metadata.get('title', '제목 없음')
            # 동일 파일 중복 표시 방지
            if title in seen_sources:
                continue
            
            date = doc.metadata.get('date', '날짜 미상')
            tags = doc.metadata.get('tags', '없음')
            
            source_text += STATUS_MESSAGES["source_item"].format(
                idx=idx,
                title=title,
                date=date,
                tags=tags
            )
            seen_sources.add(title)
            idx += 1

        # for i, doc in enumerate(source_docs):
        #     source_text += STATUS_MESSAGES["source_item"].format(
        #         idx=i+1,
        #         title=doc.metadata.get('title', '제목 없음'),
        #         date=doc.metadata.get('date', '날짜 미상'),
        #         tags=doc.metadata.get('tags', '태그 없음')
        #     )
        
        # 출처가 하나도 없을 경우 메시지 처리
        if not seen_sources:
            source_text = STATUS_MESSAGES["no_source_found"]

        full_response = f"{answer}\n\n{source_text}"
        # 튜플 대신 딕셔너리 리스트 형식으로 저장합니다.
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": full_response})
        return "", history
        
    except Exception as e:
        error_msg = STATUS_MESSAGES["error_occurred"].format(e=e)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return "", history

# 3. Gradio 인터페이스 구성
custom_css = """
#chatbot { background-color: #1e1e1e; border-radius: 15px; }
.gradio-container { font-family: 'Pretendard', sans-serif; }
button.primary { background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); border: none; }
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"# 🧠 {USER_NAME}님의 'Second Brain'")
    
    with gr.Tabs():
        # 대화 탭 (Query)
        with gr.TabItem("💬 대화하기"):
            chatbot = gr.Chatbot(label="나의 지식 베이스", height=600)
            with gr.Row():
                txt = gr.Textbox(
                    show_label=False,
                    placeholder=STATUS_MESSAGES["user_prompt"].strip(),
                    container=False
                )
            with gr.Row():
                clear_btn = gr.Button("🗑️ 대화 초기화")
            
            txt.submit(chat_with_brain, [txt, chatbot], [txt, chatbot])
            clear_btn.click(lambda: None, None, chatbot, queue=False)

        # 관리 탭 (Ingestion)
        with gr.TabItem("⚙️ 지식 관리"):
            gr.Markdown(f"### 📚 {USER_NAME}님의 장기 기억 업데이트")
            gr.Markdown("옵시디언 폴더의 새로운 기록들을 분석하여 엔진에 반영합니다.")
            learn_btn = gr.Button("✨ 새 지식 공부 시작 (Ingestion)", variant="primary")
            status_box = gr.Textbox(label="처리 결과", interactive=False)
            
            learn_btn.click(start_learning, outputs=status_box)

if __name__ == "__main__":
    # 로컬 네트워크에서 접속 가능하도록 설정
    demo.launch(server_name="127.0.0.1", server_port=7860)
