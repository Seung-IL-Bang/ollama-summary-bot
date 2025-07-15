# app_ollama.py
import streamlit as st
from rss_processor import RSSProcessor  # 이전에 만든 RSS 처리기
from ollama_summarizer import OllamaSummarizer
from datetime import datetime
import subprocess

# 페이지 설정
st.set_page_config(
    page_title="🦙 Ollama 기술 블로그 요약 봇",
    page_icon="🦙",
    layout="wide"
)

def check_ollama_status():
    """Ollama 서버 상태 확인"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_installed_models():
    """설치된 모델 목록 가져오기"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            models = [line.split()[0] for line in lines if line.strip()]
            return models
    except:
        pass
    return []

# 메인 타이틀
st.title("🦙 Ollama 기술 블로그 요약 봇")
st.markdown("**완전 무료** 로컬 AI로 기술 블로그를 요약해보세요!")

# Ollama 상태 확인
if not check_ollama_status():
    st.error("❌ Ollama가 실행되지 않았습니다!")
    st.markdown("""
    ### 🔧 해결 방법:
    1. 터미널에서 `ollama serve` 실행
    2. 별도 터미널에서 `ollama pull llama3.2` 로 모델 다운로드
    3. 페이지 새로고침
    """)
    st.stop()

# 설치된 모델 확인
installed_models = get_installed_models()
if not installed_models:
    st.warning("⚠️ 설치된 Ollama 모델이 없습니다!")
    st.markdown("""
    ### 📥 모델 설치:
    ```bash
    ollama pull llama3.2    # 추천: 가볍고 빠름
    ollama pull qwen2.5:7b  # 추천: 한국어 특화
    ollama pull mistral     # 영어 중심
    ```
    """)
    st.stop()

# 성공적으로 로드되면 캐시된 인스턴스 생성
@st.cache_resource
def load_ollama_processor():
    return RSSProcessor(), None  # summarizer는 나중에 모델 선택 후 생성

rss_processor, _ = load_ollama_processor()

# 탭 생성
tab1, tab2 = st.tabs(["🦙 요약 서비스", "🛠️ RSS 어드민"])

# =========================
# 1. Ollama 요약 서비스 탭
# =========================
with tab1:
    st.title("🦙 Ollama 기술 블로그 요약 봇")
    st.markdown("**완전 무료** 로컬 AI로 기술 블로그를 요약해보세요!")
    
    # 사이드바 설정
    st.sidebar.header("🦙 Ollama 설정")

    # 모델 선택
    selected_model = st.sidebar.selectbox(
        "사용할 모델 선택",
        installed_models,
        help="더 큰 모델일수록 성능이 좋지만 느려집니다"
    )

    # 블로그 선택
    available_blogs = rss_processor.get_available_blogs()
    selected_blog = st.sidebar.selectbox(
        "기술 블로그 선택",
        list(available_blogs.keys())
    )

    # 기사 개수 (Ollama는 느리므로 적게 권장)
    num_articles = st.sidebar.slider(
        "요약할 기사 수",
        min_value=1,
        max_value=5,  # Ollama는 느리므로 최대 5개로 제한
        value=3,
        help="로컬 AI는 클라우드보다 느리므로 적은 수를 권장합니다"
    )

    # 요약 스타일
    summary_style = st.sidebar.selectbox(
        "요약 스타일",
        ["technical", "business", "brief"],
        format_func=lambda x: {
            "technical": "🔧 기술적 관점",
            "business": "💼 비즈니스 관점", 
            "brief": "📋 간단 요약"
        }[x]
    )

    # 다이제스트 옵션
    create_digest = st.sidebar.checkbox(
        "📰 전체 다이제스트 생성",
        value=False,  # 기본값을 False로 (시간 절약)
        help="모든 기사를 종합한 다이제스트 (시간이 더 걸립니다)"
    )

    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(f"📡 {selected_blog}")
        st.info(f"🦙 사용 모델: **{selected_model}** (로컬 실행)")
        
        if st.button("🚀 무료 AI로 요약하기", type="primary"):
            # Ollama summarizer 생성
            try:
                with st.spinner(f"🦙 {selected_model} 모델 로딩 중..."):
                    summarizer = OllamaSummarizer(selected_model)
                
                # 진행상황 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # RSS 피드 가져오기
                status_text.text("📡 RSS 피드 수집 중...")
                progress_bar.progress(20)
                
                # RSS만 사용하는 안전한 버전
                articles = rss_processor.fetch_rss_feed(
                    available_blogs[selected_blog], 
                    num_articles
                )
                
                if not articles or "error" in articles[0]:
                    st.error(f"RSS 피드 처리 실패: {articles[0].get('error', '알 수 없는 오류')}")
                    st.stop()
                
                # AI 요약 시작
                status_text.text(f"🤖 {selected_model}이 요약 생성 중... (시간이 좀 걸려요)")
                progress_bar.progress(40)
                
                summaries = summarizer.summarize_multiple_articles(articles, summary_style)
                progress_bar.progress(80)
                
                # 다이제스트 생성
                digest = None
                if create_digest:
                    status_text.text("📰 전체 다이제스트 생성 중...")
                    digest = summarizer.create_digest(summaries, selected_blog)
                
                progress_bar.progress(100)
                status_text.text("✅ 모든 작업 완료!")
                
                # 결과 표시
                progress_bar.empty()
                status_text.empty()
                
                # 다이제스트 표시
                if digest:
                    st.header("📰 기술 트렌드 다이제스트")
                    st.markdown(digest)
                    st.markdown("---")
                
                # 개별 요약 표시
                st.header("📝 개별 기사 요약")
                
                for i, summary in enumerate(summaries, 1):
                    if "error" in summary:
                        st.error(f"기사 {i} 요약 실패: {summary['error']}")
                        continue
                    
                    with st.expander(f"📄 {summary['title']}", expanded=True):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.markdown(f"**작성자:** {summary['author']}")
                            st.markdown(f"**발행일:** {summary['published']}")
                            st.markdown("**AI 요약:**")
                            st.markdown(summary['summary'])
                        
                        with col_b:
                            st.markdown(f"[🔗 원문]({summary['link']})")
                            st.markdown(f"**처리시간:** {summary.get('processing_time', 'N/A')}")
                            st.markdown(f"**모델:** {selected_model}")
                
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
                st.markdown("""
                ### 🔧 문제 해결:
                1. `ollama serve` 가 실행 중인지 확인
                2. 선택한 모델이 설치되어 있는지 확인
                3. 컴퓨터 메모리가 충분한지 확인
                """)

    with col2:
        st.header("🦙 Ollama 가이드")
        st.markdown(f"""
        ### ✅ 현재 상태
        - **Ollama 서버**: 실행 중 ✅
        - **설치된 모델**: {len(installed_models)}개
        - **선택된 모델**: {selected_model}
        
        ### 🚀 장점
        - 완전 무료 사용
        - 인터넷 연결 불필요
        - API 키 없이 사용 가능
        - 개인정보 보호
        
        ### ⚡ 성능 팁
        - 첫 실행 시 모델 로딩 시간 소요
        - GPU가 있으면 더 빠름
        - 메모리 8GB 이상 권장
        
        ### 🔧 추가 모델 설치
        ```bash
        ollama pull llama3.2      # 3B (빠름)
        ollama pull qwen2.5:7b    # 7B (한국어)
        ollama pull mistral       # 7B (영어)
        ```
        """)
        
        # 현재 시간
        st.markdown("---")
        st.markdown(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =========================
# 2. 어드민 탭 (블로그 CRUD)
# =========================
with tab2:
    st.title("🛠️ RSS 어드민 페이지")

    # RSS 추가
    with st.form("add_rss"):
        name = st.text_input("블로그 이름")
        url = st.text_input("RSS URL")
        if st.form_submit_button("추가"):
            rss_processor.add_blog(name, url)
            st.success("추가 완료!")

    # RSS 삭제
    blogs = rss_processor.get_available_blogs()
    if blogs:
        delete_name = st.selectbox("삭제할 블로그 선택", list(blogs.keys()))
        if st.button("삭제"):
            rss_processor.delete_blog(delete_name)
            st.success("삭제 완료!")
    else:
        st.info("등록된 블로그가 없습니다.")

    # RSS 목록
    st.header("현재 RSS 목록")
    st.write(blogs)

    # RSS 수집 테스트
    test_url = st.text_input("테스트할 RSS URL")
    if st.button("수집 테스트"):
        articles = rss_processor.fetch_rss_feed(test_url)
        st.write(articles)

# 푸터
st.markdown("---")
st.markdown("🦙 **Powered by Ollama** | 🆓 **Completely Free** | 🔒 **Privacy First**")