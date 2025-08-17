#!/usr/bin/env python3
"""
Example usage of the Codebase Time Machine tool
"""

from codebase_time_machine import CodebaseTimeMachine
import os

def example_analysis():
    """
    Demonstrate the main features of the Codebase Time Machine
    """
    
    # Initialize the tool
    tm = CodebaseTimeMachine()
    
    # Example 1: Analyze a well-known open source repository
    print("=" * 60)
    print("CODEBASE TIME MACHINE - EXAMPLE ANALYSIS")
    print("=" * 60)
    
    # For this example, we'll use a small public repository
    # You can replace this with any Git repository URL
    repo_url = "https://github.com/octocat/Hello-World.git"
    
    try:
        # Clone and analyze repository
        print(f"\n1. Cloning repository: {repo_url}")
        tm.clone_repository(repo_url)
        
        # Analyze commit history
        print("\n2. Analyzing commit history...")
        commits = tm.analyze_commit_history()
        print(f"   Found {len(commits)} commits")
        
        # Extract file changes
        print("\n3. Extracting file changes...")
        file_changes = tm.extract_file_changes()
        print(f"   Found {len(file_changes)} file changes")
        
        # Analyze commit messages for patterns
        print("\n4. Analyzing commit patterns...")
        analysis = tm.analyze_commit_messages()
        if analysis:
            print(f"   Total commits analyzed: {analysis.get('total_commits', 0)}")
            print(f"   Top keywords: {', '.join(analysis.get('top_keywords', [])[:5])}")
            
            patterns = analysis.get('pattern_counts', {})
            print("\n   Commit patterns found:")
            for pattern, count in patterns.items():
                if count > 0:
                    print(f"   - {pattern.replace('_', ' ').title()}: {count}")
        
        # Example natural language queries
        print("\n5. Testing natural language queries...")
        
        queries = [
            "Who are the main contributors?",
            "What patterns were introduced?",
            "Show me commits about features"
        ]
        
        for query in queries:
            print(f"\n   Query: {query}")
            response = tm.query_natural_language(query)
            print(f"   Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        # Generate visualizations
        print("\n6. Generating visualizations...")
        tm.visualize_code_ownership("example_ownership.html")
        print("   - Code ownership visualization: example_ownership.html")
        
        # Generate comprehensive report
        print("\n7. Generating comprehensive report...")
        tm.generate_report("example_report.html")
        print("   - Comprehensive report: example_report.html")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE!")
        print("=" * 60)
        print("\nGenerated files:")
        print("- example_ownership.html (Code ownership visualization)")
        print("- example_report.html (Comprehensive analysis report)")
        print("- codebase_analysis.db (SQLite database with analysis data)")
        
        print("\nTo explore the results:")
        print("1. Open the HTML files in your web browser")
        print("2. Query the database for custom analysis")
        print("3. Run more natural language queries")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("This might happen if:")
        print("- The repository URL is invalid")
        print("- Network connectivity issues")
        print("- Missing dependencies")


def interactive_mode():
    """
    Interactive mode for exploring a codebase
    """
    tm = CodebaseTimeMachine()
    
    print("=" * 60)
    print("INTERACTIVE CODEBASE EXPLORATION")
    print("=" * 60)
    
    # Get repository from user
    repo_input = input("\nEnter repository URL or local path: ").strip()
    
    if repo_input.startswith('http'):
        tm.clone_repository(repo_input)
    else:
        tm.repo_path = repo_input
        try:
            import git
            tm.repo = git.Repo(repo_input)
        except:
            print("Invalid repository path!")
            return
    
    # Run basic analysis
    print("\nRunning analysis...")
    tm.analyze_commit_history()
    tm.extract_file_changes()
    
    # Interactive query loop
    print("\n" + "=" * 40)
    print("ASK QUESTIONS ABOUT YOUR CODEBASE")
    print("=" * 40)
    print("Examples:")
    print("- 'Who are the main contributors?'")
    print("- 'Show me how authentication evolved'")
    print("- 'What patterns were introduced?'")
    print("- 'Show complexity trends'")
    print("\nType 'quit' to exit")
    
    while True:
        query = input("\nYour question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if query:
            response = tm.query_natural_language(query)
            print(f"\nAnswer: {response}")
    
    # Generate final report
    print("\nGenerating final report...")
    tm.visualize_code_ownership()
    tm.generate_report()
    print("Reports generated! Check the HTML files.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        example_analysis()