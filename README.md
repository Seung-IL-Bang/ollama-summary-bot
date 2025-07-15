# ollama-summary-bot

## Step 1: 필요한 패키지 설치

```bash
# 기존 패키지 + RSS 관련 패키지 추가
pip install langchain
pip install langchain-anthropic
pip install streamlit
pip install python-dotenv
pip install feedparser  # RSS 피드 파싱
pip install requests    # 웹 페이지 내용 가져오기
pip install beautifulsoup4  # HTML 파싱
pip install newspaper3k  # 뉴스/블로그 기사 추출 (선택사항)
```

## 주요 특징과 개선사항

- 실시간 RSS 피드 처리: 최신 기술 블로그 글을 자동으로 수집
- 스마트 본문 추출: RSS 요약이 아닌 전체 기사 내용을 분석
- 다양한 요약 스타일: 기술적/비즈니스/간단 요약 옵션
- 다이제스트 기능: 여러 기사를 종합한 트렌드 분석

## 확장 아이디어

- 슬랙 봇 연동: 매일 아침 요약을 슬랙으로 전송
- 이메일 뉴스레터: 주간 기술 트렌드 이메일 발송
- 키워드 필터링: 특정 기술(AI, Cloud 등)만 골라서 요약
- 번역 기능: 한국어로 번역된 요약 제공
- 트렌드 분석: 시간별 기술 키워드 트렌드 시각화

---

# 🦙 Ollama 설정 가이드

## Step 1: Ollama 설치

**Windows**
```bash
# PowerShell에서 실행
winget install Ollama.Ollama

# 또는 https://ollama.ai/download 에서 다운로드
```

**macOS**
```bash
# Homebrew 사용
brew install ollama
```

**Linux**
```bash
# 설치 스크립트 실행
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: 모델 다운로드

```bash
# 추천 모델들 (용량과 성능 고려)

# 1. Llama 3.2 (3B) - 가볍고 빠름, 한국어 지원 좋음
ollama pull llama3.2

# 2. Mistral (7B) - 좋은 성능, 영어 위주
ollama pull mistral

# 3. Qwen2.5 (7B) - 코딩과 한국어에 특화
ollama pull qwen2.5:7b

# 설치 확인
ollama list
```

**💡 모델 선택 가이드:**

- 가벼운 테스트: llama3.2 (2GB)
- 균형잡힌 성능: qwen2.5:7b (4.7GB)
- 영어 중심: mistral (4.1GB)

## ollama 관련 패키지 추가
```
streamlit
python-dotenv
feedparser
requests
beautifulsoup4
langchain
langchain-community  # Ollama 연동용
```

## Step 3: 실행하기

```bash
# 1. Ollama 서버 시작 (별도 터미널)
ollama serve

# 2. 모델 다운로드 (다른 터미널)
ollama pull llama3.2

# 3. 앱 실행
streamlit run app_ollama.py
```