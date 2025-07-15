import os
from langchain_community.llms import Ollama
from langchain.schema import BaseMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import time

class OllamaSummarizer:
    """Ollama를 사용한 완전 무료 기술 블로그 요약 클래스"""
    def __init__(self, model_name: str = "llama3.2"):
        print(f"🦙 Ollama 모델 '{model_name}' 초기화 중...")
        
        try:
            self.llm = Ollama(
                model=model_name,
                temperature=0.1
                # Ollama는 로컬 실행이므로 타임아웃을 길게 설정
                # request_timeout=60.0
            )
            
            # 모델 테스트
            test_response = self.llm("안녕하세요!")
            print(f"✅ Ollama 모델 '{model_name}' 준비 완료!")
            
        except Exception as e:
            print(f"❌ Ollama 초기화 실패: {str(e)}")
            print("💡 해결 방법:")
            print("1. 'ollama serve' 명령어로 Ollama 서버가 실행 중인지 확인")
            print(f"2. 'ollama pull {model_name}' 명령어로 모델이 설치되었는지 확인")
            raise e
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # Ollama는 긴 텍스트 처리가 느릴 수 있음
            chunk_overlap=100,
            length_function=len
        )
    
    def summarize_single_article(self, article: Dict, summary_style: str = "technical") -> Dict:
        """단일 기사 요약 (Ollama 버전)"""
        try:
            if "error" in article:
                return article
            
            # 요약할 텍스트 준비 (짧게 유지)
            content = article.get('content', article.get('summary', ''))
            if len(content) > 2000:
                content = content[:2000] + "..."
            
            text_to_summarize = f"""
            제목: {article['title']}
            작성자: {article['author']}
            
            내용:
            {content}
            """
            
            # Ollama에 맞는 프롬프트 (한국어/영어 혼용)
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
            full_prompt = f"{prompt}\n\n{text_to_summarize}"
            
            print(f"🤖 '{article['title'][:30]}...' 요약 중...")
            
            # Ollama 실행 (시간이 좀 걸릴 수 있음)
            start_time = time.time()
            summary = self.llm(full_prompt)
            elapsed_time = time.time() - start_time
            
            print(f"✅ 요약 완료 ({elapsed_time:.1f}초)")
            
            return {
                "title": article["title"],
                "link": article["link"],
                "author": article["author"],
                "published": article["published"] or article["updated"] or '',
                "summary": summary,
                "summary_style": summary_style,
                "processing_time": f"{elapsed_time:.1f}초"
            }
            
        except Exception as e:
            print(f"❌ 요약 실패: {str(e)}")
            return {
                "title": article.get("title", "알 수 없는 제목"),
                "error": f"Ollama 요약 실패: {str(e)}"
            }

    def summarize_multiple_articles(self, articles: List[Dict], summary_style: str = "technical") -> List[Dict]:
        """여러 기사를 순차적으로 요약"""
        summaries = []
        
        print(f"📚 총 {len(articles)}개 기사 요약 시작...")
        
        for i, article in enumerate(articles, 1):
            print(f"\n🔄 진행상황: {i}/{len(articles)}")
            summary = self.summarize_single_article(article, summary_style)
            summaries.append(summary)
            
            # 로컬 모델이므로 과부하 방지를 위한 짧은 대기
            if i < len(articles):
                time.sleep(1)
        
        print(f"\n🎉 모든 요약 완료!")
        return summaries

    def create_digest(self, summaries: List[Dict], blog_name: str) -> str:
        """여러 요약을 하나의 다이제스트로 통합"""
        try:
            valid_summaries = [s for s in summaries if "error" not in s]
            
            if not valid_summaries:
                return "요약할 수 있는 기사가 없습니다."
            
            # 요약들을 간단히 결합
            articles_text = ""
            for i, summary in enumerate(valid_summaries[:3], 1):  # 최대 3개만 사용
                articles_text += f"\n{i}. {summary['title']}\n요약: {summary['summary']}\n"
            
            digest_prompt = f"""아래는 {blog_name}의 최신 기술 블로그 요약들입니다.
                이들을 종합하여 다음과 같은 다이제스트를 작성해주세요:
                1. 전체적인 기술 트렌드 (2-3문장)
                2. 주요 혁신 사항들 (2-3문장)  
                3. 개발자들이 주목할 점들 (2-3문장)

                간결하고 실용적으로 작성해주세요.

                기사 요약들:
                {articles_text}
                """
            
            print("📰 전체 다이제스트 생성 중...")
            digest = self.llm(digest_prompt)
            print("✅ 다이제스트 생성 완료!")
            
            return digest
            
        except Exception as e:
            return f"다이제스트 생성 실패: {str(e)}"

    def get_available_models(self) -> List[str]:
        """사용 가능한 Ollama 모델 목록 반환"""
        try:
            import subprocess
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 헤더 제외
                models = [line.split()[0] for line in lines if line.strip()]
                return models
            return []
        except:
            return ["empty"]  # 기본값