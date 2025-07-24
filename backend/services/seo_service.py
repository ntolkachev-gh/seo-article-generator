import re
from typing import List
from bs4 import BeautifulSoup

class SEOService:
    def __init__(self):
        self.min_word_count = 1500
        self.optimal_word_count = 2500
        self.max_word_count = 4000
    
    def calculate_seo_score(self, article: str, keywords: List[str]) -> float:
        """Рассчитывает SEO-оценку статьи от 0 до 10"""
        
        score = 0.0
        max_score = 10.0
        
        # 1. Количество слов (2 балла)
        word_count = len(article.split())
        if word_count >= self.min_word_count:
            if word_count <= self.optimal_word_count:
                score += 2.0
            elif word_count <= self.max_word_count:
                score += 1.5
            else:
                score += 1.0
        else:
            score += (word_count / self.min_word_count) * 2.0
        
        # 2. Структура заголовков (2 балла)
        h1_count = len(re.findall(r'^# .+', article, re.MULTILINE))
        h2_count = len(re.findall(r'^## .+', article, re.MULTILINE))
        h3_count = len(re.findall(r'^### .+', article, re.MULTILINE))
        
        # Идеально: 1 H1, несколько H2, несколько H3
        if h1_count == 1:
            score += 0.5
        if h2_count >= 3:
            score += 1.0
        elif h2_count >= 1:
            score += 0.5
        if h3_count >= 2:
            score += 0.5
        
        # 3. Использование ключевых слов (2 балла)
        article_lower = article.lower()
        keywords_used = 0
        total_keyword_density = 0
        
        for keyword in keywords[:10]:  # Проверяем топ-10 ключевых слов
            keyword_lower = keyword.lower()
            keyword_count = article_lower.count(keyword_lower)
            
            if keyword_count > 0:
                keywords_used += 1
                # Плотность ключевого слова (идеально 1-3%)
                density = (keyword_count / word_count) * 100
                if 1 <= density <= 3:
                    total_keyword_density += 1
                elif 0.5 <= density < 1 or 3 < density <= 5:
                    total_keyword_density += 0.5
        
        # Бонус за использование ключевых слов
        if keywords_used >= len(keywords) * 0.7:  # 70% ключевых слов использовано
            score += 1.5
        elif keywords_used >= len(keywords) * 0.5:  # 50% ключевых слов
            score += 1.0
        else:
            score += (keywords_used / len(keywords)) * 1.0
        
        # Бонус за правильную плотность
        score += min(total_keyword_density * 0.1, 0.5)
        
        # 4. Длина заголовков (1 балл)
        headers = re.findall(r'^#{1,3} (.+)', article, re.MULTILINE)
        optimal_header_lengths = 0
        
        for header in headers:
            if 30 <= len(header) <= 60:  # Оптимальная длина заголовка
                optimal_header_lengths += 1
        
        if headers:
            score += (optimal_header_lengths / len(headers)) * 1.0
        
        # 5. Наличие введения и заключения (1 балл)
        has_intro = bool(re.search(r'введение|вступление', article_lower))
        has_conclusion = bool(re.search(r'заключение|выводы|итог', article_lower))
        
        if has_intro:
            score += 0.5
        if has_conclusion:
            score += 0.5
        
        # 6. Читабельность (1 балл)
        sentences = re.split(r'[.!?]+', article)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Оптимальная длина предложения 15-20 слов
            if 10 <= avg_sentence_length <= 25:
                score += 1.0
            elif 8 <= avg_sentence_length < 10 or 25 < avg_sentence_length <= 30:
                score += 0.7
            else:
                score += 0.3
        
        # 7. Разнообразие контента (1 балл)
        # Проверяем наличие списков, выделений и т.д.
        has_lists = bool(re.search(r'^[\*\-\+] .+', article, re.MULTILINE))
        has_emphasis = bool(re.search(r'\*\*.+\*\*|\*.+\*', article))
        has_links = bool(re.search(r'\[.+\]\(.+\)', article))
        
        content_variety_score = 0
        if has_lists:
            content_variety_score += 0.4
        if has_emphasis:
            content_variety_score += 0.3
        if has_links:
            content_variety_score += 0.3
        
        score += content_variety_score
        
        # Ограничиваем максимальный балл
        return min(score, max_score)
    
    def get_seo_recommendations(self, article: str, keywords: List[str], score: float) -> List[str]:
        """Возвращает рекомендации по улучшению SEO"""
        recommendations = []
        
        word_count = len(article.split())
        if word_count < self.min_word_count:
            recommendations.append(f"Увеличьте объем статьи до {self.min_word_count}+ слов (сейчас {word_count})")
        
        h1_count = len(re.findall(r'^# .+', article, re.MULTILINE))
        if h1_count == 0:
            recommendations.append("Добавьте заголовок H1")
        elif h1_count > 1:
            recommendations.append("Используйте только один заголовок H1")
        
        h2_count = len(re.findall(r'^## .+', article, re.MULTILINE))
        if h2_count < 3:
            recommendations.append("Добавьте больше подзаголовков H2 для лучшей структуры")
        
        # Проверяем использование ключевых слов
        article_lower = article.lower()
        unused_keywords = []
        
        for keyword in keywords[:5]:  # Проверяем топ-5 ключевых слов
            if keyword.lower() not in article_lower:
                unused_keywords.append(keyword)
        
        if unused_keywords:
            recommendations.append(f"Добавьте ключевые слова: {', '.join(unused_keywords)}")
        
        # Проверяем структуру
        has_intro = bool(re.search(r'введение|вступление', article_lower))
        has_conclusion = bool(re.search(r'заключение|выводы|итог', article_lower))
        
        if not has_intro:
            recommendations.append("Добавьте введение к статье")
        if not has_conclusion:
            recommendations.append("Добавьте заключение к статье")
        
        # Проверяем списки и форматирование
        has_lists = bool(re.search(r'^[\*\-\+] .+', article, re.MULTILINE))
        if not has_lists:
            recommendations.append("Добавьте маркированные или нумерованные списки для лучшей читабельности")
        
        return recommendations 