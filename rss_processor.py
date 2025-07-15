import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import json

class RSSProcessor:
    """RSS 피드를 처리하고 기사 내용을 추출하는 클래스"""
    def __init__(self, rss_file: str = "rss_blogs.json"):
        self.rss_file = rss_file
        self.tech_blogs = self._load_blogs()

    def _load_blogs(self) -> Dict[str, str]:
        try:
            with open(self.rss_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_blogs(self):
        with open(self.rss_file, "w", encoding="utf-8") as f:
            json.dump(self.tech_blogs, f, ensure_ascii=False, indent=2)

    def get_available_blogs(self) -> Dict[str, str]:
        """사용 가능한 기술 블로그 목록 반환"""
        return self.tech_blogs

    def add_blog(self, name: str, url: str):
        self.tech_blogs[name] = url
        self._save_blogs()

    def delete_blog(self, name: str):
        if name in self.tech_blogs:
            del self.tech_blogs[name]
            self._save_blogs()

    def fetch_rss_feed(self, rss_url: str, max_entries: int = 10) -> List[Dict]:
        """RSS 피드를 가져오고 최대 max_entries개의 항목을 반환"""
        try:
            # RSS 피드 파싱
            feed = feedparser.parse(rss_url)

            if feed.bozo:
                return [{"error": f"Failed to parse RSS feed: {feed.bozo_exception}"}]
            
            articles = []
            for entry in feed.entries[:max_entries]:
                article = {
                    "title": getattr(entry, "title", ""),
                    "link": getattr(entry, "link", ""),
                    "published": getattr(entry, "published", ""),
                    "summary": self._clean_html_tags(getattr(entry, "summary", "")),
                    "content": self._extract_rss_content(entry),  # entry 전체를 넘김
                    "description": self._clean_html_tags(getattr(entry, "description", "")),
                    "author": getattr(entry, "author", ""),
                    "updated": getattr(entry, "updated", ""),
                    "tags": self._extract_tags(entry)
                }
                articles.append(article)

            return articles
        except Exception as e:
            return [{"error": f"Failed to fetch RSS feed: {str(e)}"}]

    def _extract_rss_content(self, entry) -> str:
        """RSS 엔트리에서 사용 가능한 모든 텍스트 추출"""
        content_parts = []
        
        # 1. summary (대부분의 RSS에 포함)
        if hasattr(entry, 'summary'):
            content_parts.append(entry.summary)
        
        # 2. content (일부 RSS에 전체 내용 포함)
        if hasattr(entry, 'content'):
            for content in entry.content:
                if content.type in ['text/html', 'text/plain']:
                    content_parts.append(content.value)
        
        # 3. description (추가 설명)
        if hasattr(entry, 'description'):
            content_parts.append(entry.description)
        
        # HTML 태그 제거
        full_content = " ".join(content_parts)
        return self._clean_html_tags(full_content)
    
    def _clean_html_tags(self, text: str) -> str:
        """간단한 HTML 태그 제거"""
        # 기본적인 HTML 태그 제거
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 여러 공백을 하나로
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()
        
    def _extract_tags(self, entry) -> List[str]:
        """RSS 엔트리에서 태그/카테고리 추출"""
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags]
        return tags
    
    
if __name__ == "__main__":
    processor = RSSProcessor()
    blogs = processor.get_available_blogs()
    for name, url in blogs.items():
        print(f"블로그: {name}")
        articles = processor.fetch_rss_feed(url, max_entries=3)
        for article in articles:
            print(article)  
    
    