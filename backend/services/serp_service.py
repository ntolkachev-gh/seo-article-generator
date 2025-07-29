import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from urllib.parse import quote_plus
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class SERPService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.serp_api_key = settings.SERP_API_KEY
        print(f"SERP_API_KEY: {'Set' if self.serp_api_key else 'Not set'}")
    
    def analyze_topic(self, topic: str) -> Dict[str, List[str]]:
        """Анализирует тему и возвращает ключевые слова, заголовки и вопросы"""
        try:
            # Сначала пробуем официальный SERP API
            if self.serp_api_key:
                search_results = self._serp_api_search(topic)
            else:
                # Fallback на Google поиск
                search_results = self._google_search(topic)
            
            # Извлекаем данные
            keywords = self._extract_keywords(topic, search_results)
            titles = self._extract_titles(search_results)
            questions = self._extract_questions(topic)
            related_searches = self._extract_related_searches(topic)
            
            return {
                "keywords": keywords,
                "titles": titles,
                "questions": questions,
                "related_searches": related_searches
            }
        except Exception as e:
            print(f"Error analyzing SERP: {e}")
            # Возвращаем базовые ключевые слова на основе темы
            return {
                "keywords": self._generate_basic_keywords(topic),
                "titles": [],
                "questions": [],
                "related_searches": []
            }
    
    def _serp_api_search(self, query: str) -> List[Dict]:
        """Выполняет поиск через официальный SERP API"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "engine": "google",
                "num": 10,
                "hl": "ru",
                "gl": "ru"
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Извлекаем результаты из SERP API ответа
            if "organic_results" in data:
                for result in data["organic_results"]:
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', '')
                    })
            
            print(f"SERP API found {len(results)} results")
            return results[:10]
            
        except Exception as e:
            print(f"Error in SERP API search: {e}")
            # Fallback на Google поиск
            return self._google_search(query)
    
    def _google_search(self, query: str) -> List[Dict]:
        """Выполняет поиск в Google и возвращает результаты (fallback метод)"""
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num=10"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Извлекаем результаты поиска
            for result in soup.find_all('div', class_='g'):
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('span', {'data-ved': True})
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(),
                        'link': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text() if snippet_elem else ''
                    })
            
            print(f"Google search found {len(results)} results")
            return results[:10]
        except Exception as e:
            print(f"Error in Google search: {e}")
            return []
    
    def _extract_keywords(self, topic: str, results: List[Dict]) -> List[str]:
        """Извлекает ключевые слова из результатов поиска"""
        keywords = set()
        
        # Добавляем основную тему
        topic_words = topic.lower().split()
        keywords.update(topic_words)
        
        # Извлекаем из заголовков и сниппетов
        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
            
            # Простое извлечение слов (можно улучшить с помощью NLP)
            words = re.findall(r'\b[а-яё]{3,}\b', text)
            keywords.update(words[:5])  # Берем первые 5 слов из каждого результата
        
        # Фильтруем и возвращаем топ-20 ключевых слов
        filtered_keywords = [kw for kw in keywords if len(kw) >= 3 and kw not in ['что', 'как', 'для', 'это', 'или']]
        return list(filtered_keywords)[:20]
    
    def _extract_titles(self, results: List[Dict]) -> List[str]:
        """Извлекает заголовки из результатов поиска"""
        return [result.get('title', '') for result in results if result.get('title')]
    
    def _extract_questions(self, topic: str) -> List[str]:
        """Извлекает популярные вопросы по теме"""
        # Генерируем базовые вопросы
        base_questions = [
            f"Что такое {topic}?",
            f"Как работает {topic}?",
            f"Зачем нужен {topic}?",
            f"Где используется {topic}?",
            f"Какие преимущества {topic}?",
            f"Как выбрать {topic}?",
            f"Сколько стоит {topic}?",
            f"Как настроить {topic}?"
        ]
        
        return base_questions[:5]
    
    def _extract_related_searches(self, topic: str) -> List[str]:
        """Извлекает связанные поисковые запросы"""
        # Генерируем связанные запросы
        related = [
            f"{topic} что это",
            f"{topic} как использовать",
            f"{topic} преимущества",
            f"{topic} недостатки",
            f"{topic} альтернативы",
            f"лучший {topic}",
            f"{topic} цена",
            f"{topic} отзывы"
        ]
        
        return related[:6]
    
    def _generate_basic_keywords(self, topic: str) -> List[str]:
        """Генерирует базовые ключевые слова из темы"""
        words = topic.lower().split()
        keywords = []
        
        for word in words:
            if len(word) >= 3:
                keywords.append(word)
        
        # Добавляем общие SEO слова
        keywords.extend(['преимущества', 'недостатки', 'использование', 'применение', 'выбор'])
        
        return keywords[:15] 