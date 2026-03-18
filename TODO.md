# 📋 Second Brain 개발 TODO 리스트

## 0단계: 프로젝트 기반 및 환경 구축
- [x] **라이선스 일관성 확보**
    - [x] `README.md` 하단 라이선스 문구를 `[Apache-2.0 license](./LICENSE)`로 수정함
- [x] **개발 환경 세팅**`
    - [x] Python 가상환경 생성 및 `requirements.txt` 패키지 설치
    - [x] **로컬 모델 환경 구축 (Ollama)**: `qwen3.5:9B`, `llama3.1:8b`, `deepseek-r1:7b`, `phi3` pull
- [x] **디렉토리 구조 설계**
    - [x] `/data/personal`: 개인 메모 및 일기 저장소 생성함
    - [x] `/data/interest`: 외부 관심사 데이터셋 저장소 생성함
    - [x] `/src/engine`: RAG 및 LLM 로직 폴더 구성함
- [x] **중앙 설정 관리 시스템 구축**: `src/config.py`를 통한 환경 변수 및 시스템 설정 통합

## 1단계: Personal RAG (개인 지식 베이스) 구현
- [x] **데이터 인제스션(Ingestion) 파이프라인**
    - [x] Markdown 로더 구현 (날짜, #태그 등 메타데이터 추출 포함)
    - [x] 텍스트 청킹(Chunking) 전략 수립 (사고의 맥락이 끊기지 않게 500자 단위, 50자 중복 단위 설정)
- [x] **Vector DB 구축**
    - [x] bge-m3 임베딩 모델 연동 및 CUDA 가속 설정
    - [x] ChromaDB를 활용한 로컬 벡터 저장소 초기화 및 데이터 로드함
- [x] **기본 검색 및 응답**
    - [x] 시멘틱 검색(Semantic Search) 로직 및 LCEL 체인 구현
    - [x] 검색된 기록을 바탕으로 LLM 답변 생성 프롬프트 작성함
    - [x] 태그 기반 연관성 인지 프롬프트 및 답변 시 출처(태그 포함) 표시

## 2단계: Hybrid Retrieval 및 지능화
- [ ] **Interest DB 확장**
    - [ ] **외부 지식 및 기술 문서** 외부 지식 데이터셋(Wikipedia, 기술 문서, 유튜브 CC) 수집 및 벡터화 (학습용이 아닌 검색용)
- [ ] **라우팅(Routing) 엔진**
    - [ ] 사용자 질문의 의도를 분석하여 Personal/Interest DB 중 적절한 곳으로 쿼리를 전달하는 로직 구현함
- [ ] **근거 기반 응답 시스템**
    - [ ] 답변에 사용된 문서의 출처(파일명, 행 번호 등)를 표시하는 인용 기능 구현함
    - [ ] Hallucination 억제를 위한 검증 로직 추가함

## 3단계: 나를 복제하는 Fine-tuning 및 Reflection
- [ ] **사고방식/말투 학습 데이터 준비**
    - [ ] **개인 기록(일기, 메모)만 선별**하여 '사고 과정' 추출 및 정제 (유튜브 데이터 제외)
- [ ] **QLoRA 미세 조정 (Fine-tuning)**
    - [ ] Llama 3.1 8B 기반 QLoRA 학습 세팅
    - [ ] 내 문체와 논리 구조가 반영된 페르소나 레이어 생성
- [ ] **Reflection Engine 고도화**
    - [ ] DeepSeek-R1을 활용한 '통찰 질문 3개' 생성 로직 구현

## 4단계: 시스템 통합 및 최적화
- [ ] **Qwen 3.5 메인 엔진 통합**: RAG 시스템과 학습된 페르소나 연결
- [ ] **VRAM 최적화**: 12GB 메모리 내 모델 스위칭 및 양자화 최적화

- [ ] **최종 평가**
    - [ ] README에 명시된 평가 지표(Recall@k, Personal relevance) 측정 및 최적화함
