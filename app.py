# app.py
import streamlit as st
from rss_processor import RSSProcessor
from tech_blog_summarizer import TechBlogSummarizer
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="기술 블로그 요약 봇",
    page_icon="🤖",
    layout="wide"
)

# 제목과 설명
st.title("🤖 기술 블로그 RSS 요약 봇")
st.markdown("유명 IT 회사들의 최신 기술 블로그를 자동으로 요약해드립니다!")

# 인스턴스 생성 (캐싱)
@st.cache_resource
def load_processors():
    return RSSProcessor(), TechBlogSummarizer()

rss_processor, summarizer = load_processors()

# 사이드바 설정
st.sidebar.header("⚙️ 설정")

# 블로그 선택
available_blogs = rss_processor.get_available_blogs()
selected_blog = st.sidebar.selectbox(
    "기술 블로그 선택",
    list(available_blogs.keys()),
    help="요약하고 싶은 회사의 기술 블로그를 선택하세요"
)

# 기사 개수 선택
num_articles = st.sidebar.slider(
    "요약할 기사 수",
    min_value=1,
    max_value=10,
    value=5,
    help="더 많은 기사를 선택할수록 비용이 증가합니다"
)

# 요약 스타일 선택
summary_style = st.sidebar.selectbox(
    "요약 스타일",
    ["technical", "business", "brief"],
    format_func=lambda x: {
        "technical": "🔧 기술적 관점",
        "business": "💼 비즈니스 관점",
        "brief": "📋 간단 요약"
    }[x]
)

# 다이제스트 생성 옵션
create_digest = st.sidebar.checkbox(
    "📰 전체 다이제스트 생성",
    value=True,
    help="모든 기사를 종합한 다이제스트를 생성합니다"
)

# 메인 컨텐츠
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"📡 {selected_blog}")
    st.markdown(f"**RSS URL:** `{available_blogs[selected_blog]}`")
    
    # 요약 시작 버튼
    if st.button("🚀 최신 기사 요약하기", type="primary"):
        # 진행상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1단계: RSS 피드 가져오기
            status_text.text("📡 RSS 피드를 가져오는 중...")
            progress_bar.progress(20)
            
            articles = rss_processor.fetch_rss_feed(
                available_blogs[selected_blog], 
                num_articles
            )
            
            if not articles or "error" in articles[0]:
                st.error(f"RSS 피드 처리 실패: {articles[0].get('error', '알 수 없는 오류')}")
                st.stop()
            
            # 2단계: 기사 요약
            status_text.text("🤖 AI가 기사를 요약하는 중...")
            progress_bar.progress(60)
            
            summaries = summarizer.summarize_multiple_articles(articles, summary_style)
            
            # 3단계: 다이제스트 생성 (선택사항)
            # digest = None
            # if create_digest:
            #     status_text.text("📰 전체 다이제스트 생성 중...")
            #     progress_bar.progress(80)
            #     digest = summarizer.create_digest(summaries, selected_blog)
            
            progress_bar.progress(100)
            status_text.text("✅ 완료!")
            time.sleep(1)
            
            # 결과 표시
            progress_bar.empty()
            status_text.empty()
            
            # 다이제스트 먼저 표시
            # if digest:
            #     st.header("📰 오늘의 기술 다이제스트")
            #     st.markdown(digest)
            #     st.markdown("---")
            
            # 개별 기사 요약들
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
                        st.markdown("**요약:**")
                        st.markdown(summary['summary'])
                    
                    with col_b:
                        st.markdown(f"[🔗 원문 보기]({summary['link']})")
                        st.markdown(f"**스타일:** {summary['summary_style']}")
            
        except Exception as e:
            st.error(f"처리 중 오류가 발생했습니다: {str(e)}")

with col2:
    st.header("📖 사용 가이드")
    st.markdown("""
    ### 🎯 사용법
    1. **블로그 선택**: 관심있는 회사 선택
    2. **기사 수 설정**: 1-10개 범위에서 선택
    3. **요약 스타일 선택**: 
        - 기술적: 기술 세부사항 중심
        - 비즈니스: 비즈니스 임팩트 중심  
        - 간단: 핵심 내용만 간략히
    4. **요약 시작**: 버튼 클릭 후 대기
    
    ### 💡 팁
    - 처음에는 3-5개 기사로 시작하세요
    - 다이제스트는 전체 트렌드 파악에 유용해요
    - 원문 링크로 자세한 내용 확인 가능
    
    ### ⚡ 지원 블로그
    """)
    
    # 지원하는 블로그 목록 표시
    for blog_name in available_blogs.keys():
        st.markdown(f"- {blog_name}")

# 푸터
st.markdown("---")
st.markdown("🤖 Powered by Claude AI & LangChain | 📡 RSS Technology")

# 현재 시간 표시
st.sidebar.markdown("---")
st.sidebar.markdown(f"⏰ 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")