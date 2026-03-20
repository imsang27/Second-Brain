import sys
import time
import threading
from src.config import STATUS_MESSAGES, USER_NAME, NOTES_PATH, CHUNK_SIZE

def loading_animation(stop_event, task_type, device_status=""):
    """
    작업 유형(task_type)에 따라 적절한 메시지를 찾아 애니메이션을 실행합니다.
    """
    # 작업별 메시지 매핑 (중앙 집중 관리)
    task_map = {
        "sync": ("checking_sync", {"user_name": USER_NAME}),
        "ingest": ("embedding", {"device_status": device_status}),
        "search": ("searching", {"user_name": USER_NAME}),
        "load": ("loading_start", {"notes_path": NOTES_PATH, "user_name": USER_NAME})
    }
    
    msg_key, kwargs = task_map.get(task_type, ("searching", {}))
    chars = [".  ", ".. ", "..."]
    idx = 0
    
    while not stop_event.is_set():
        # config의 STATUS_MESSAGES를 활용해 문구 완성
        msg = STATUS_MESSAGES[msg_key].format(dots=chars[idx % 3], **kwargs)
        sys.stdout.write(f"\r{msg}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.5)
    
    # 현재 메시지를 고정하고 다음 줄로 이동
    sys.stdout.write("\n")
    sys.stdout.flush()

def start_animation(task_type, device_status=""):
    """
    단순히 'sync'나 'search' 같은 단어만 받아서 스레드를 시작합니다.
    """
    stop_event = threading.Event()
    thread = threading.Thread(target=loading_animation, args=(stop_event, task_type, device_status))
    thread.start()
    return stop_event, thread
