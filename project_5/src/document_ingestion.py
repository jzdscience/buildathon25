"""
Document Ingestion Module
Handles loading documents from various sources including text files and URLs
"""

import os
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import chardet
from urllib.parse import urlparse
import re
from tqdm import tqdm


class DocumentIngestion:
    """Handles document loading from various sources"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.total_size = 0
        self.documents = []
        
    def load_documents(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        Load documents from a list of sources (files or URLs)
        
        Args:
            sources: List of file paths or URLs
            
        Returns:
            List of document dictionaries with content and metadata
        """
        for source in tqdm(sources, desc="Loading documents"):
            if self._is_url(source):
                self._load_url(source)
            else:
                self._load_file(source)
                
            if self.total_size > self.max_size_bytes:
                print(f"Warning: Maximum size limit ({self.max_size_bytes / 1024 / 1024} MB) exceeded")
                break
                
        return self.documents
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL"""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _load_url(self, url: str) -> None:
        """Load content from a URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Check size
            content_size = len(response.content)
            if self.total_size + content_size > self.max_size_bytes:
                print(f"Skipping {url}: Would exceed size limit")
                return
                
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if text:
                self.documents.append({
                    'source': url,
                    'type': 'url',
                    'content': text,
                    'title': soup.title.string if soup.title else url,
                    'size': content_size
                })
                self.total_size += content_size
                
        except Exception as e:
            print(f"Error loading URL {url}: {str(e)}")
    
    def _load_file(self, filepath: str) -> None:
        """Load content from a file"""
        try:
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return
                
            # Check file size
            file_size = os.path.getsize(filepath)
            if self.total_size + file_size > self.max_size_bytes:
                print(f"Skipping {filepath}: Would exceed size limit")
                return
            
            # Detect encoding
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            # Read file content
            with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
                
            if content:
                self.documents.append({
                    'source': filepath,
                    'type': 'file',
                    'content': content,
                    'title': os.path.basename(filepath),
                    'size': file_size
                })
                self.total_size += file_size
                
        except Exception as e:
            print(f"Error loading file {filepath}: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded documents"""
        return {
            'total_documents': len(self.documents),
            'total_size_mb': self.total_size / 1024 / 1024,
            'types': {
                'files': sum(1 for d in self.documents if d['type'] == 'file'),
                'urls': sum(1 for d in self.documents if d['type'] == 'url')
            }
        }
