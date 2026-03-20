import os
import re
import hashlib
from datetime import datetime
from src.config import (
    HASH_ALGORITHM,
    FILE_EXTENSIONS,
    DATE_FORMAT,
    STATUS_MESSAGES,
    USER_NAME
)
from langchain_core.documents import Document

def load_personal_notes(directory_path):
    """
    하위 폴더를 포함하여 모든 마크다운 파일을 찾아 제목, 내용, 날짜를 추출합니다.
    """
    notes = []
    # 마크다운 태그를 찾는 정규표현식 (예: #python, #보안)
    tag_pattern = re.compile(r'#(\w+)')
    
    # 폴더가 없으면 에러를 내는 대신 자동으로 생성합니다.
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return notes
    
    # os.listdir 대신 os.walk를 사용하여 모든 하위 폴더를 탐색합니다.
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(FILE_EXTENSIONS):
                file_path = os.path.join(root, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 1. Config에 설정된 해시 알고리즘으로 해시 생성
                        hasher = hashlib.new(HASH_ALGORITHM)
                        hasher.update(content.encode('utf-8'))
                        file_hash = hasher.hexdigest()
                        
                        # 2. 태그 추출
                        tags = list(set(tag_pattern.findall(content)))
                        # 파일 수정 시간을 날짜 메타데이터로 활용합니다.
                        mtime = os.path.getmtime(file_path)
                        date_str = datetime.fromtimestamp(mtime).strftime(DATE_FORMAT)
                        
                        document = Document(
                            page_content=content,
                            metadata={
                                "source": file_path,
                                "title": filename,
                                "date": date_str,
                                "tags": ", ".join(tags), # 리스트를 문자열로 변환하여 저장
                                "file_id": file_hash # 중복 체크를 위한 ID 추가
                            }
                        )
                        notes.append(document)
                
                except Exception as e:
                    print(STATUS_MESSAGES["file_error"].format(filename=filename, e=e))
    return notes

if __name__ == "__main__":
    # 테스트 실행부
    path = os.getenv("NOTES_PATH")
    data = load_personal_notes(path)
    print(STATUS_MESSAGES["found_updates"].format(file_count=len(data)))
    if data:
        print(STATUS_MESSAGES["build_complete"].format(user_name=USER_NAME))
