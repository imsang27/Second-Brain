import os
import re
from datetime import datetime
from langchain_core.documents import Document

def load_personal_notes(directory_path):
    """
    마크다운 파일을 읽어 제목, 내용, 날짜를 추출합니다.
    """
    notes = []
    # 마크다운 태그를 찾는 정규표현식 (예: #python, #보안)
    tag_pattern = re.compile(r'#(\w+)')

    # 폴더가 없으면 에러를 내는 대신 자동으로 생성합니다.
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return notes

    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 1. 태그 추출
                tags = list(set(tag_pattern.findall(content)))
                # 파일 수정 시간을 날짜 메타데이터로 활용합니다.
                mtime = os.path.getmtime(file_path)
                date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                
                # 2. LangChain 문서 객체 생성
                document = Document(
                    page_content=content,
                    metadata={
                        "source": file_path,
                        "title": filename,
                        "date": date_str,
                        "tags": ", ".join(tags) # 리스트를 문자열로 변환하여 저장
                    }
                )
                notes.append(document)
    return notes

if __name__ == "__main__":
    # 테스트 실행부
    path = os.getenv("NOTES_PATH")
    data = load_personal_notes(path)
    print(f"✅ 발견된 메모 개수: {len(data)}개")
    if data:
        print(f"가장 최근 읽은 파일: {data[0].metadata['title']}")
