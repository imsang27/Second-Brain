# 🧠 Personal Cognitive Twin RAG
> 나의 기록 + 관심사 데이터로 나를 되묻고 확장하는 **개인지능 RAG 시스템**

## 📌 프로젝트 개요
**Personal Cognitive Twin RAG**는 개인의 기록과 관심사 기반 대규모 데이터셋을 결합해  
사용자의 사고를 반추하고, 의미 있는 질문을 생성하며,  
스스로를 더 깊이 이해하도록 돕는 **사고 확장 AI**입니다.

> 단순 요약/검색이 아닌  
**“나와 대화하는 또 하나의 나”**를 구축하는 프로젝트입니다.

## ✨ 주요 기능
| 기능 | 설명 |
|---|---|
🧠 Personal RAG | 일기/노트/회고 기반 맥락 추출 및 응답  
🌐 Interest RAG | 관심 분야 데이터셋 기반 지식 검색  
🎯 질의 라우팅 | 질문에 따라 두 DB 중 최적 선택  
🔍 근거 기반 답변 | 제공 문서 내 근거 인용  
💬 반추 질문 생성 | 통찰 질문 & 미니 코칭  
🔐 컨텍스트 보호 | 개인 데이터는 별도 namespace 관리  

## 🧠 왜 필요한가?
현대인은 기록은 많지만 **생각을 되돌려보고 연결하는 능력**이 부족합니다.

- 노트는 쌓이지만 다시 안 본다  
- AI는 일반적 조언만 준다  
- 메타인지 능력 향상 도구가 없다  

> 이 시스템은  
**기억 → 사고 → 관찰 → 질문 → 행동**  
루프를 자동화합니다.

## 🧩 시스템 구조

```
┌──────────────┐    ┌─────────────────┐
│ Personal Data │    │ Interest Corpus │
│(Notes/Logs)   │    │(Large Dataset)  │
└──────┬───────┘    └──────┬─────────┘
       │                   │
   Embed & Chunk       Embed & Chunk
       │                   │
 Personal VectorDB    Interest VectorDB
      └──────┬─────────────┘
             │ Retrieval Routing (LLM + Rules)
             ▼
        LLM Reasoning
             ▼
 Insight + Follow-up Questions
```

## 📂 데이터 구조

### Personal Documents (Example)
```json
{
  "source": "note",
  "text": "최근 집중이 잘 안 된다. 원인은 수면 부족으로 보임",
  "date": "2025-10-31",
  "tag": ["self-reflection"],
  "sentiment": "neutral"
}
```

### Interest Dataset (Example)
```json
{
  "source": "wikipedia_ai",
  "topic": "machine_learning",
  "tokens": 5800000
}
```

## ⚙️ 기술 스택
- Python, FastAPI
- FAISS / Chroma
- bge-m3 / OpenAI Embedding
- GPT-series or Local LLM
- Markdown / PDF ingest
- Secure local storage for personal data

## ✅ 평가 요소
| 항목 | 기준 |
|---|---|
Retrieval 성능 | Retrieval@k, citation accuracy  
개인화 지표 | Personal relevance score  
융합 효과 | A only / B only / A+B 비교  
응답 품질 | Grounded answer ratio  
지연시간 | p95 latency  

## 🚀 MVP 목표 (1~2 Weeks)
- 개인 기록 ingest + 벡터화
- 관심사 대규모 데이터 구축
- 질의 라우팅 + 점수 가중
- 통찰 질문 + 응답 템플릿 구성

## 📎 예시 대화

**User:**  
요즘 공부 루틴이 계속 깨져. 이유가 뭐지?

**AI:**  
> 최근 기록에서 "밤 시간대 피로"와 "목표 과부하"가 반복됩니다.  
> 주 3회 집중 패턴이 있었는데 최근 무너졌어요.

🧠 질문:  
- 목표 범위가 너무 큰 건 아닐까?
- 공부 시간대를 옮기는 실험을 해볼 수 있을까?

🎯 추천 액션:  
오늘 15분 집중 루틴으로 작게 재시작.

## 📌 핵심 메시지
> 이 프로젝트는 **빅데이터가 아니라 깊은 데이터**를 다룹니다.  
> 세상을 아는 AI가 아니라 **나를 잊지 않게 하는 AI**입니다.

## 📁 Repository Info
**Repo Name:** personal-cognitive-twin-rag  
**Description:** Personal RAG + interest-domain corpus to build a reflective “second self” AI that remembers, questions, and expands user's thinking.

