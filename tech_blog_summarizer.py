import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict

load_dotenv()

class TechBlogSummarizer:
    def __init__(self):
        self.llm = ChatAnthropic(
            model_name="claude-3-haiku-20240307",  # 모델명
            temperature=0.1,
            timeout=60,  # 예시값, 필요에 따라 조정
            stop=None    # 또는 적절한 stop 시퀀스
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,  # RSS 기사는 보통 더 짧으므로 청크 크기 축소
            chunk_overlap=150,
            length_function=len
        )

    def summarize_single_article(self, article: Dict, summary_style: str = "technical") -> Dict:
        """단일 기사 요약"""
        try:
            if "error" in article:
                return article
            
            # 요약할 텍스트 준비
            published = article.get('published') or article.get('updated', '')
            text_to_summarize = f"""
            제목: {article['title']}
            작성자: {article['author']}
            발행일: {published}
            
            본문:
            {article.get('content', article.get('summary', ''))}
            """
            
            # 스타일별 프롬프트
            prompts = {
                "technical": """
                다음 기술 블로그 글을 기술적 관점에서 요약해주세요:
                - 사용된 기술/도구
                - 해결한 문제
                - 핵심 솔루션
                - 중요한 인사이트
                """,
                "business": """
                다음 기술 블로그 글을 비즈니스 관점에서 요약해주세요:
                - 비즈니스 임팩트
                - 성능 개선 사항
                - 비용 절감 효과
                - 사용자 경험 개선
                """,
                "brief": """
                다음 기술 블로그 글을 3-4줄로 간단히 요약해주세요:
                - 핵심 내용만 추출
                - 기술적 용어는 간단히 설명
                """
            }
            
            prompt = prompts.get(summary_style, prompts["technical"])
            message = HumanMessage(content=f"{prompt}\n\n{text_to_summarize}")
            
            response = self.llm([message])
            
            return {
                "title": article["title"],
                "link": article["link"],
                "author": article["author"],
                "published": article["published"],
                "summary": response.content,
                "summary_style": summary_style
            }
            
        except Exception as e:
            return {
                "title": article.get("title", "알 수 없는 제목"),
                "error": f"요약 실패: {str(e)}"
            }

    def summarize_multiple_articles(self, articles: List[Dict], summary_style: str = "technical") -> List[Dict]:
        """여러 기사를 한 번에 요약"""
        summaries = []
        
        for i, article in enumerate(articles, 1):
            print(f"📝 {i}/{len(articles)} 기사 요약 중...")
            summary = self.summarize_single_article(article, summary_style)
            summaries.append(summary)
        
        return summaries
