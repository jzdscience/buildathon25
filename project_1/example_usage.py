#!/usr/bin/env python3
"""
Example usage of the Screenshot Search Tool
"""

from screenshot_search import ScreenshotSearcher
import os

def demo_screenshot_search():
    """Demonstrate the screenshot search functionality."""
    
    # Initialize the searcher
    searcher = ScreenshotSearcher(cache_file="demo_cache.json")
    
    # Example 1: Process a folder of screenshots
    print("=== Demo: Processing Screenshots ===")
    screenshots_folder = "./sample_screenshots"  # Change this to your folder
    
    if os.path.exists(screenshots_folder):
        print(f"Processing screenshots in {screenshots_folder}...")
        searcher.process_screenshot_folder(screenshots_folder)
    else:
        print(f"Creating sample folder structure at {screenshots_folder}")
        print("Please add your screenshots to this folder and run again.")
        os.makedirs(screenshots_folder, exist_ok=True)
        return
    
    # Example 2: Text-based searches
    print("\n=== Demo: Text-based Searches ===")
    text_queries = [
        "error message",
        "login",
        "password",
        "save button",
        "email"
    ]
    
    for query in text_queries:
        print(f"\nSearching for: '{query}'")
        results = searcher.search(query, top_k=3)
        if results:
            print(f"Found {len(results)} results:")
            for i, (filename, confidence, data) in enumerate(results, 1):
                print(f"  {i}. {filename} (confidence: {confidence:.3f})")
                if data['ocr_text']:
                    preview = data['ocr_text'][:50].replace('\n', ' ')
                    print(f"     Text preview: {preview}...")
        else:
            print("  No results found")
    
    # Example 3: Visual-based searches
    print("\n=== Demo: Visual-based Searches ===")
    visual_queries = [
        "blue button",
        "red error",
        "green interface",
        "dark theme",
        "settings screen"
    ]
    
    for query in visual_queries:
        print(f"\nSearching for: '{query}'")
        results = searcher.search(query, top_k=3)
        if results:
            print(f"Found {len(results)} results:")
            for i, (filename, confidence, data) in enumerate(results, 1):
                print(f"  {i}. {filename} (confidence: {confidence:.3f})")
                if data['visual_description']:
                    print(f"     Visual: {data['visual_description']}")
                if data['ui_elements']:
                    print(f"     UI elements: {', '.join(data['ui_elements'])}")
        else:
            print("  No results found")
    
    # Example 4: Combined searches
    print("\n=== Demo: Combined Searches ===")
    combined_queries = [
        "error message with red text",
        "blue submit button",
        "login screen with password field",
        "settings with dark background"
    ]
    
    for query in combined_queries:
        print(f"\nSearching for: '{query}'")
        results = searcher.search(query, top_k=2)
        if results:
            for i, (filename, confidence, data) in enumerate(results, 1):
                print(f"  {i}. {filename} (confidence: {confidence:.3f})")
                print(f"     Path: {data['path']}")


def interactive_demo():
    """Run an interactive demo session."""
    print("=== Interactive Screenshot Search Demo ===")
    print("This demo will let you search through your screenshots interactively.")
    print("Type 'quit' to exit.\n")
    
    searcher = ScreenshotSearcher()
    
    # Check if we have processed screenshots
    if not searcher.screenshots_data:
        folder = input("Enter path to screenshots folder: ").strip()
        if folder and os.path.exists(folder):
            searcher.process_screenshot_folder(folder)
        else:
            print("Invalid folder path. Exiting.")
            return
    
    print(f"\nLoaded {len(searcher.screenshots_data)} screenshots")
    print("You can search for:")
    print("- Text content: 'error message', 'login', 'password'")
    print("- Visual elements: 'blue button', 'red text', 'dark theme'")
    print("- Combined: 'error message in red popup'\n")
    
    while True:
        query = input("Search query: ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if query:
            results = searcher.search(query, top_k=5)
            searcher.display_results(results, query)
        

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        demo_screenshot_search()