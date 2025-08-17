import re
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EmailClusterer:
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        
    def cluster_emails(self, emails: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        if len(emails) < self.n_clusters:
            self.n_clusters = max(1, len(emails) // 2)
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        
        text_features = []
        for email in emails:
            combined_text = f"{email['subject']} {email['body']}"
            cleaned_text = self._clean_text(combined_text)
            text_features.append(cleaned_text)
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(text_features)
            cluster_labels = self.kmeans.fit_predict(tfidf_matrix)
        except Exception as e:
            print(f"Clustering failed: {e}")
            cluster_labels = [0] * len(emails)
        
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(emails[i])
        
        labeled_clusters = {}
        for cluster_id, cluster_emails in clusters.items():
            cluster_name = self._generate_cluster_name(cluster_emails)
            labeled_clusters[cluster_id] = {
                'name': cluster_name,
                'emails': cluster_emails,
                'count': len(cluster_emails)
            }
        
        return labeled_clusters
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()
    
    def _generate_cluster_name(self, cluster_emails: List[Dict[str, Any]]) -> str:
        subjects = [email['subject'] for email in cluster_emails]
        senders = [email['sender'] for email in cluster_emails]
        
        common_sender = self._find_most_common(senders)
        common_words = self._extract_common_keywords(subjects)
        
        if common_sender and len([s for s in senders if common_sender in s]) >= len(cluster_emails) * 0.6:
            sender_name = self._extract_sender_name(common_sender)
            return f"Emails from {sender_name}"
        
        if common_words:
            return f"Emails about {', '.join(common_words[:3])}"
        
        if any(keyword in ' '.join(subjects).lower() for keyword in ['newsletter', 'promotion', 'deal', 'sale']):
            return "Promotional Emails"
        
        if any(keyword in ' '.join(subjects).lower() for keyword in ['meeting', 'calendar', 'event', 'invite']):
            return "Meeting & Events"
        
        if any(keyword in ' '.join(subjects).lower() for keyword in ['notification', 'alert', 'update', 'reminder']):
            return "Notifications & Updates"
        
        return f"Email Group ({len(cluster_emails)} emails)"
    
    def _find_most_common(self, items: List[str]) -> str:
        if not items:
            return ""
        
        from collections import Counter
        counter = Counter(items)
        return counter.most_common(1)[0][0] if counter else ""
    
    def _extract_common_keywords(self, subjects: List[str]) -> List[str]:
        combined_text = ' '.join(subjects).lower()
        
        common_keywords = []
        business_terms = ['invoice', 'payment', 'order', 'receipt', 'billing', 'account']
        social_terms = ['social', 'linkedin', 'facebook', 'twitter', 'instagram']
        news_terms = ['news', 'weekly', 'daily', 'update', 'digest']
        
        for term_list in [business_terms, social_terms, news_terms]:
            for term in term_list:
                if term in combined_text and combined_text.count(term) >= 2:
                    common_keywords.append(term)
        
        if not common_keywords:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', combined_text)
            word_counts = {}
            for word in words:
                if word not in ['email', 'mail', 'message', 'from', 'your', 'this', 'that', 'with', 'have', 'will']:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            common_keywords = [word for word, count in sorted_words[:3] if count >= 2]
        
        return common_keywords
    
    def _extract_sender_name(self, sender: str) -> str:
        match = re.search(r'"?([^"<]+)"?\s*<', sender)
        if match:
            return match.group(1).strip()
        
        match = re.search(r'([^@]+)@', sender)
        if match:
            name = match.group(1).replace('.', ' ').replace('_', ' ')
            return name.title()
        
        return sender.split('@')[0] if '@' in sender else sender