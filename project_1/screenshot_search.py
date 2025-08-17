#!/usr/bin/env python3
"""
Screenshot Search Tool
Search your screenshot history using natural language queries for both text content and visual elements.
"""

import os
import json
import cv2
import numpy as np
from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import argparse


class ScreenshotSearcher:
    def __init__(self, cache_file: str = "screenshot_cache.json"):
        self.cache_file = cache_file
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize BLIP model for image captioning
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        self.screenshots_data = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached screenshot data or return empty dict."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save screenshot data to cache file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.screenshots_data, f, indent=2)
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def generate_image_description(self, image_path: str) -> str:
        """Generate visual description of image using BLIP."""
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.blip_processor(image, return_tensors="pt")
            out = self.blip_model.generate(**inputs, max_length=50)
            description = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return description
        except Exception as e:
            print(f"Error generating description for {image_path}: {e}")
            return ""
    
    def detect_ui_elements(self, image_path: str) -> List[str]:
        """Detect UI elements like buttons, text fields, etc."""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            ui_elements = []
            
            # Detect rectangles (potential buttons/UI elements)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            button_count = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 10000:  # Filter by size
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 5:  # Button-like aspect ratio
                        button_count += 1
            
            if button_count > 0:
                ui_elements.append(f"{button_count} button-like elements")
            
            # Color analysis for prominent colors
            pixels = image.reshape(-1, 3)
            unique_colors = np.unique(pixels, axis=0)
            
            # Simple color detection
            blue_pixels = np.sum((pixels[:, 0] > pixels[:, 1]) & (pixels[:, 0] > pixels[:, 2]))
            red_pixels = np.sum((pixels[:, 2] > pixels[:, 1]) & (pixels[:, 2] > pixels[:, 0]))
            green_pixels = np.sum((pixels[:, 1] > pixels[:, 0]) & (pixels[:, 1] > pixels[:, 2]))
            
            total_pixels = len(pixels)
            if blue_pixels > total_pixels * 0.1:
                ui_elements.append("prominent blue elements")
            if red_pixels > total_pixels * 0.1:
                ui_elements.append("prominent red elements")
            if green_pixels > total_pixels * 0.1:
                ui_elements.append("prominent green elements")
            
            return ui_elements
        except Exception as e:
            print(f"Error detecting UI elements in {image_path}: {e}")
            return []
    
    def process_screenshot_folder(self, folder_path: str):
        """Process all screenshots in a folder and extract data."""
        if not os.path.exists(folder_path):
            print(f"Folder {folder_path} does not exist!")
            return
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        
        for filename in os.listdir(folder_path):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_path = os.path.join(folder_path, filename)
                
                # Skip if already processed and file hasn't changed
                if filename in self.screenshots_data:
                    cached_mtime = self.screenshots_data[filename].get('mtime', 0)
                    current_mtime = os.path.getmtime(image_path)
                    if cached_mtime == current_mtime:
                        continue
                
                print(f"Processing {filename}...")
                
                # Extract text content
                ocr_text = self.extract_text_from_image(image_path)
                
                # Generate visual description
                visual_description = self.generate_image_description(image_path)
                
                # Detect UI elements
                ui_elements = self.detect_ui_elements(image_path)
                
                # Combine all text for embedding
                combined_text = f"{ocr_text} {visual_description} {' '.join(ui_elements)}"
                
                # Generate embedding
                embedding = self.sentence_model.encode(combined_text).tolist()
                
                self.screenshots_data[filename] = {
                    'path': image_path,
                    'ocr_text': ocr_text,
                    'visual_description': visual_description,
                    'ui_elements': ui_elements,
                    'combined_text': combined_text,
                    'embedding': embedding,
                    'mtime': os.path.getmtime(image_path)
                }
        
        self._save_cache()
        print(f"Processed {len(self.screenshots_data)} screenshots")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Search screenshots using natural language query."""
        if not self.screenshots_data:
            print("No screenshots processed yet. Please process a folder first.")
            return []
        
        # Generate query embedding
        query_embedding = self.sentence_model.encode(query)
        
        results = []
        
        for filename, data in self.screenshots_data.items():
            # Calculate similarity
            screenshot_embedding = np.array(data['embedding'])
            similarity = cosine_similarity([query_embedding], [screenshot_embedding])[0][0]
            
            results.append((filename, similarity, data))
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def display_results(self, results: List[Tuple[str, float, Dict]], query: str):
        """Display search results in a formatted way."""
        print(f"\nSearch results for: '{query}'")
        print("=" * 50)
        
        if not results:
            print("No results found.")
            return
        
        for i, (filename, confidence, data) in enumerate(results, 1):
            print(f"\n{i}. {filename}")
            print(f"   Confidence: {confidence:.3f}")
            print(f"   Path: {data['path']}")
            
            if data['ocr_text']:
                print(f"   OCR Text: {data['ocr_text'][:100]}{'...' if len(data['ocr_text']) > 100 else ''}")
            
            if data['visual_description']:
                print(f"   Visual: {data['visual_description']}")
            
            if data['ui_elements']:
                print(f"   UI Elements: {', '.join(data['ui_elements'])}")


def main():
    parser = argparse.ArgumentParser(description='Search screenshots using natural language')
    parser.add_argument('--folder', '-f', help='Folder containing screenshots to process')
    parser.add_argument('--query', '-q', help='Search query')
    parser.add_argument('--top', '-t', type=int, default=5, help='Number of top results to return')
    parser.add_argument('--cache', '-c', default='screenshot_cache.json', help='Cache file path')
    
    args = parser.parse_args()
    
    searcher = ScreenshotSearcher(cache_file=args.cache)
    
    if args.folder:
        searcher.process_screenshot_folder(args.folder)
    
    if args.query:
        results = searcher.search(args.query, top_k=args.top)
        searcher.display_results(results, args.query)
    
    # Interactive mode if no query provided
    if not args.query:
        print("\nInteractive search mode. Type 'quit' to exit.")
        while True:
            query = input("\nEnter search query: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            if query:
                results = searcher.search(query, top_k=args.top)
                searcher.display_results(results, query)


if __name__ == "__main__":
    main()