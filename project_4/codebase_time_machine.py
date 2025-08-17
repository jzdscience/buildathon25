#!/usr/bin/env python3
"""
Codebase Time Machine - A tool to explore the evolution of codebases over time
"""

import os
import re
import ast
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
from dataclasses import dataclass
from pathlib import Path

import git
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass
class CommitInfo:
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    
@dataclass
class FileChange:
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted', 'renamed'
    lines_added: int
    lines_deleted: int
    commit_hash: str
    
@dataclass
class CodeMetrics:
    file_path: str
    lines_of_code: int
    complexity: int
    functions: int
    classes: int
    commit_hash: str


class CodebaseTimeMachine:
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path
        self.repo = None
        self.console = Console()
        self.db_path = "codebase_analysis.db"
        self.init_database()
        
        # Download NLTK data if not present
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('vader_lexicon')
        except LookupError:
            try:
                import ssl
                # Handle SSL certificate issues
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:
                    pass
                else:
                    ssl._create_default_https_context = _create_unverified_https_context
                
                self.console.print("Downloading NLTK data...")
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
            except Exception as e:
                # NLTK download failed, but continue anyway
                self.console.print(f"Warning: NLTK data download failed: {e}")
                self.console.print("Some NLP features may be limited.")
    
    def init_database(self):
        """Initialize SQLite database for storing analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Commits table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS commits (
            hash TEXT PRIMARY KEY,
            author TEXT,
            date TEXT,
            message TEXT,
            files_changed INTEGER,
            insertions INTEGER,
            deletions INTEGER
        )
        ''')
        
        # File changes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            change_type TEXT,
            lines_added INTEGER,
            lines_deleted INTEGER,
            commit_hash TEXT,
            FOREIGN KEY (commit_hash) REFERENCES commits (hash)
        )
        ''')
        
        # Code metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            lines_of_code INTEGER,
            complexity INTEGER,
            functions INTEGER,
            classes INTEGER,
            commit_hash TEXT,
            FOREIGN KEY (commit_hash) REFERENCES commits (hash)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def clone_repository(self, repo_url: str, local_path: str = None) -> str:
        """Clone a Git repository and return the local path"""
        if local_path is None:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            local_path = f"./repos/{repo_name}"
        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        if os.path.exists(local_path):
            self.console.print(f"Repository already exists at {local_path}")
            self.repo = git.Repo(local_path)
        else:
            self.console.print(f"Cloning repository {repo_url} to {local_path}")
            self.repo = git.Repo.clone_from(repo_url, local_path)
        
        self.repo_path = local_path
        return local_path
    
    def analyze_commit_history(self) -> List[CommitInfo]:
        """Analyze the complete commit history of the repository"""
        if not self.repo:
            raise ValueError("No repository loaded. Use clone_repository() or load_repository() first.")
        
        commits = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Analyzing commit history...", total=None)
            
            for commit in self.repo.iter_commits():
                try:
                    # Get commit stats
                    stats = commit.stats
                    total_insertions = stats.total['insertions']
                    total_deletions = stats.total['deletions']
                    files_changed = list(stats.files.keys())
                    
                    commit_info = CommitInfo(
                        hash=commit.hexsha,
                        author=commit.author.name,
                        date=datetime.fromtimestamp(commit.committed_date),
                        message=commit.message.strip(),
                        files_changed=files_changed,
                        insertions=total_insertions,
                        deletions=total_deletions
                    )
                    commits.append(commit_info)
                    
                except Exception as e:
                    self.console.print(f"Error processing commit {commit.hexsha}: {e}")
                    continue
        
        self.console.print(f"Analyzed {len(commits)} commits")
        self.store_commits(commits)
        return commits
    
    def store_commits(self, commits: List[CommitInfo]):
        """Store commit data in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for commit in commits:
            cursor.execute('''
            INSERT OR REPLACE INTO commits 
            (hash, author, date, message, files_changed, insertions, deletions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                commit.hash,
                commit.author,
                commit.date.isoformat(),
                commit.message,
                len(commit.files_changed),
                commit.insertions,
                commit.deletions
            ))
        
        conn.commit()
        conn.close()
    
    def extract_file_changes(self) -> List[FileChange]:
        """Extract detailed file changes from commit history"""
        if not self.repo:
            raise ValueError("No repository loaded.")
        
        file_changes = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Extracting file changes...", total=None)
            
            commits = list(self.repo.iter_commits())
            for i, commit in enumerate(commits):
                try:
                    # Get parent commits
                    parents = commit.parents
                    
                    if parents:
                        # Compare with first parent
                        diffs = commit.diff(parents[0])
                    else:
                        # First commit, compare with empty tree
                        diffs = commit.diff(git.NULL_TREE)
                    
                    for diff in diffs:
                        change_type = self.get_change_type(diff)
                        file_path = diff.a_path or diff.b_path
                        
                        if file_path and self.is_code_file(file_path):
                            lines_added = 0
                            lines_deleted = 0
                            
                            # Use commit stats for more reliable line counts
                            try:
                                if file_path in commit.stats.files:
                                    file_stats = commit.stats.files[file_path]
                                    lines_added = file_stats['insertions']
                                    lines_deleted = file_stats['deletions']
                            except:
                                # Fallback to diff parsing
                                try:
                                    if hasattr(diff, 'diff') and diff.diff:
                                        diff_text = diff.diff.decode('utf-8', errors='ignore')
                                        lines_added = len([line for line in diff_text.split('\n') if line.startswith('+') and not line.startswith('+++')])
                                        lines_deleted = len([line for line in diff_text.split('\n') if line.startswith('-') and not line.startswith('---')])
                                except:
                                    pass
                            
                            file_change = FileChange(
                                file_path=file_path,
                                change_type=change_type,
                                lines_added=lines_added,
                                lines_deleted=lines_deleted,
                                commit_hash=commit.hexsha
                            )
                            file_changes.append(file_change)
                
                except Exception as e:
                    self.console.print(f"Error processing commit {commit.hexsha}: {e}")
                    continue
        
        self.console.print(f"Extracted {len(file_changes)} file changes")
        self.store_file_changes(file_changes)
        return file_changes
    
    def get_change_type(self, diff) -> str:
        """Determine the type of change from a git diff"""
        if diff.new_file:
            return 'added'
        elif diff.deleted_file:
            return 'deleted'
        elif diff.renamed_file:
            return 'renamed'
        else:
            return 'modified'
    
    def is_code_file(self, file_path: str) -> bool:
        """Check if a file is a code file based on its extension"""
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.jsx', '.tsx', '.vue', '.html', '.css', '.scss', '.sass'
        }
        return any(file_path.endswith(ext) for ext in code_extensions)
    
    def store_file_changes(self, file_changes: List[FileChange]):
        """Store file changes in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for change in file_changes:
            cursor.execute('''
            INSERT INTO file_changes 
            (file_path, change_type, lines_added, lines_deleted, commit_hash)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                change.file_path,
                change.change_type,
                change.lines_added,
                change.lines_deleted,
                change.commit_hash
            ))
        
        conn.commit()
        conn.close()
    
    def calculate_code_metrics(self) -> List[CodeMetrics]:
        """Calculate code complexity and other metrics for Python files"""
        if not self.repo:
            raise ValueError("No repository loaded.")
        
        metrics = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Calculating code metrics...", total=None)
            
            for commit in self.repo.iter_commits():
                try:
                    self.repo.git.checkout(commit.hexsha)
                    
                    for root, dirs, files in os.walk(self.repo_path):
                        for file in files:
                            if file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                rel_path = os.path.relpath(file_path, self.repo_path)
                                
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    tree = ast.parse(content)
                                    
                                    # Calculate metrics
                                    lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
                                    complexity = self.calculate_complexity(tree)
                                    functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                                    classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
                                    
                                    metric = CodeMetrics(
                                        file_path=rel_path,
                                        lines_of_code=lines_of_code,
                                        complexity=complexity,
                                        functions=functions,
                                        classes=classes,
                                        commit_hash=commit.hexsha
                                    )
                                    metrics.append(metric)
                                    
                                except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
                                    continue
                
                except Exception as e:
                    self.console.print(f"Error processing commit {commit.hexsha}: {e}")
                    continue
        
        # Return to latest commit
        self.repo.git.checkout('HEAD')
        
        self.console.print(f"Calculated metrics for {len(metrics)} files")
        self.store_code_metrics(metrics)
        return metrics
    
    def calculate_complexity(self, tree) -> int:
        """Calculate cyclomatic complexity of an AST"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.Lambda, ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def store_code_metrics(self, metrics: List[CodeMetrics]):
        """Store code metrics in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in metrics:
            cursor.execute('''
            INSERT INTO code_metrics 
            (file_path, lines_of_code, complexity, functions, classes, commit_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric.file_path,
                metric.lines_of_code,
                metric.complexity,
                metric.functions,
                metric.classes,
                metric.commit_hash
            ))
        
        conn.commit()
        conn.close()
    
    def analyze_commit_messages(self) -> Dict[str, Any]:
        """Analyze commit messages for patterns and business context"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM commits", conn)
        conn.close()
        
        if df.empty:
            return {}
        
        # Preprocess commit messages
        messages = df['message'].fillna('').tolist()
        processed_messages = []
        
        for msg in messages:
            # Remove URLs, ticket numbers, and other noise
            cleaned = re.sub(r'http[s]?://\S+', '', msg)
            cleaned = re.sub(r'#\d+', '', cleaned)
            cleaned = re.sub(r'\b[A-Z]+-\d+\b', '', cleaned)  # JIRA tickets
            processed_messages.append(cleaned.lower().strip())
        
        # Extract keywords and patterns
        try:
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_messages)
            feature_names = vectorizer.get_feature_names_out()
            
            # Cluster commit messages
            n_clusters = min(10, len(set(processed_messages)))
            clusters = None
            if n_clusters > 1 and len(processed_messages) > 1:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(tfidf_matrix)
                df['cluster'] = clusters
        except Exception as e:
            # If ML analysis fails, continue with basic analysis
            feature_names = []
            clusters = None
        
        # Identify common patterns
        patterns = {
            'bug_fix': r'\b(fix|bug|error|issue|problem)\b',
            'feature': r'\b(add|new|feature|implement)\b',
            'refactor': r'\b(refactor|clean|improve|optimize)\b',
            'docs': r'\b(doc|readme|comment|documentation)\b',
            'test': r'\b(test|spec|unittest)\b',
            'security': r'\b(security|auth|permission|vulnerability)\b',
            'performance': r'\b(performance|speed|optimize|fast)\b'
        }
        
        pattern_counts = {}
        for pattern_name, pattern in patterns.items():
            count = sum(1 for msg in processed_messages if re.search(pattern, msg))
            pattern_counts[pattern_name] = count
        
        return {
            'total_commits': len(df),
            'top_keywords': list(feature_names[:20]) if feature_names is not None else [],
            'pattern_counts': pattern_counts,
            'clusters': clusters.tolist() if clusters is not None else None,
            'messages_df': None  # Don't include DataFrame in results to avoid serialization issues
        }
    
    def query_natural_language(self, query: str) -> str:
        """Process natural language queries about the codebase"""
        query_lower = query.lower()
        
        # Load data
        conn = sqlite3.connect(self.db_path)
        commits_df = pd.read_sql_query("SELECT * FROM commits", conn)
        file_changes_df = pd.read_sql_query("SELECT * FROM file_changes", conn)
        conn.close()
        
        if commits_df.empty:
            return "No analysis data available. Please run an analysis first."
        
        response = ""
        
        if 'authentication' in query_lower or 'auth' in query_lower:
            auth_commits = commits_df[commits_df['message'].str.contains('auth|login|password|token', case=False, na=False)]
            if not auth_commits.empty:
                response += f"Found {len(auth_commits)} authentication-related commits:\n\n"
                for _, commit in auth_commits.head(5).iterrows():
                    response += f"• {commit['date'][:10]} - {commit['message'][:100]}...\n"
            else:
                response += "No authentication-related commits found.\n"
        
        elif 'pattern' in query_lower:
            analysis = self.analyze_commit_messages()
            if analysis and 'pattern_counts' in analysis:
                response += "Code change patterns found:\n\n"
                for pattern, count in analysis['pattern_counts'].items():
                    response += f"• {pattern.replace('_', ' ').title()}: {count} commits\n"
        
        elif 'complexity' in query_lower or 'growth' in query_lower:
            response += "Complexity analysis features have been simplified. You can see basic code ownership and contributor patterns in the visualizations.\n"
        
        elif 'who' in query_lower or 'author' in query_lower:
            authors = commits_df['author'].value_counts()
            response += "Top contributors:\n\n"
            for author, count in authors.head(10).items():
                response += f"• {author}: {count} commits\n"
        
        else:
            # Generic search in commit messages
            search_terms = [word for word in query_lower.split() if len(word) > 3]
            if search_terms:
                pattern = '|'.join(search_terms)
                matching_commits = commits_df[commits_df['message'].str.contains(pattern, case=False, na=False)]
                if not matching_commits.empty:
                    response += f"Found {len(matching_commits)} commits matching your query:\n\n"
                    for _, commit in matching_commits.head(5).iterrows():
                        response += f"• {commit['date'][:10]} - {commit['message'][:100]}...\n"
                else:
                    response += "No commits found matching your query.\n"
        
        return response or "I couldn't find information related to your query. Try asking about 'authentication', 'patterns', 'complexity', or 'contributors'."
    
    def visualize_code_ownership(self, output_file: str = "code_ownership.html"):
        """Create visualizations for code ownership by contributors"""
        conn = sqlite3.connect(self.db_path)
        commits_df = pd.read_sql_query("SELECT * FROM commits", conn)
        file_changes_df = pd.read_sql_query("SELECT * FROM file_changes", conn)
        conn.close()
        
        if commits_df.empty:
            self.console.print("No commit data available for visualization")
            return
        
        # Check if we have file changes data
        if file_changes_df.empty:
            self.console.print("No file changes data available for detailed ownership analysis")
            # Create basic visualization with only commit data
            self._create_basic_ownership_viz(commits_df, output_file)
            return
        
        # Merge data
        merged_df = file_changes_df.merge(commits_df[['hash', 'author', 'date']], 
                                        left_on='commit_hash', right_on='hash')
        
        if merged_df.empty:
            self.console.print("No matching data between commits and file changes")
            self._create_basic_ownership_viz(commits_df, output_file)
            return
        
        # Calculate ownership by lines of code contributed
        ownership = merged_df.groupby(['author', 'file_path']).agg({
            'lines_added': 'sum',
            'lines_deleted': 'sum'
        }).reset_index()
        
        ownership['net_contribution'] = ownership['lines_added'] - ownership['lines_deleted']
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Commits by Author', 'Lines Added by Author', 
                          'File Ownership Heatmap', 'Activity Over Time'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "heatmap"}, {"type": "scatter"}]]
        )
        
        # Commits by author
        author_commits = commits_df['author'].value_counts().head(10)
        fig.add_trace(
            go.Bar(x=author_commits.index, y=author_commits.values, name="Commits"),
            row=1, col=1
        )
        
        # Lines added by author
        lines_by_author = ownership.groupby('author')['lines_added'].sum().sort_values(ascending=False).head(10)
        fig.add_trace(
            go.Bar(x=lines_by_author.index, y=lines_by_author.values, name="Lines Added"),
            row=1, col=2
        )
        
        # File ownership heatmap (top files and authors)
        top_files = ownership.groupby('file_path')['net_contribution'].sum().nlargest(20).index
        top_authors = ownership.groupby('author')['net_contribution'].sum().nlargest(10).index
        
        heatmap_data = ownership[
            (ownership['file_path'].isin(top_files)) & 
            (ownership['author'].isin(top_authors))
        ].pivot_table(
            index='file_path', 
            columns='author', 
            values='net_contribution', 
            fill_value=0
        )
        
        fig.add_trace(
            go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='RdYlBu_r',
                name="Ownership"
            ),
            row=2, col=1
        )
        
        # Activity over time
        commits_df['date'] = pd.to_datetime(commits_df['date'])
        daily_commits = commits_df.groupby(commits_df['date'].dt.date).size()
        
        fig.add_trace(
            go.Scatter(
                x=daily_commits.index,
                y=daily_commits.values,
                mode='lines+markers',
                name="Daily Commits"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Codebase Ownership Analysis",
            showlegend=False
        )
        
        fig.write_html(output_file)
        self.console.print(f"Code ownership visualization saved to {output_file}")
    
    def _create_basic_ownership_viz(self, commits_df: pd.DataFrame, output_file: str):
        """Create basic ownership visualization when detailed file changes are not available"""
        # Create simpler visualization with just commit data
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Commits by Author', 'Activity Over Time')
        )
        
        # Commits by author
        author_commits = commits_df['author'].value_counts().head(10)
        fig.add_trace(
            go.Bar(x=author_commits.index, y=author_commits.values, name="Commits"),
            row=1, col=1
        )
        
        # Activity over time
        commits_df['date'] = pd.to_datetime(commits_df['date'])
        daily_commits = commits_df.groupby(commits_df['date'].dt.date).size()
        
        fig.add_trace(
            go.Scatter(
                x=daily_commits.index,
                y=daily_commits.values,
                mode='lines+markers',
                name="Daily Commits"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            title_text="Basic Repository Analysis",
            showlegend=False
        )
        
        fig.write_html(output_file)
        self.console.print(f"Basic ownership visualization saved to {output_file}")
    
    def visualize_complexity_trends(self, output_file: str = "complexity_trends.html"):
        """Create visualizations for complexity and growth trends"""
        conn = sqlite3.connect(self.db_path)
        commits_df = pd.read_sql_query("SELECT * FROM commits", conn)
        metrics_df = pd.read_sql_query("SELECT * FROM code_metrics", conn)
        conn.close()
        
        if metrics_df.empty:
            self.console.print("No code metrics available for visualization")
            return
        
        # Merge with commit data to get dates
        merged_df = metrics_df.merge(commits_df[['hash', 'date']], 
                                   left_on='commit_hash', right_on='hash')
        merged_df['date'] = pd.to_datetime(merged_df['date'])
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Complexity Over Time', 'Lines of Code Growth', 
                          'Function Count Trends', 'Class Count Trends')
        )
        
        # Aggregate metrics by date
        daily_metrics = merged_df.groupby(merged_df['date'].dt.date).agg({
            'complexity': 'mean',
            'lines_of_code': 'sum',
            'functions': 'sum',
            'classes': 'sum'
        }).reset_index()
        
        # Complexity over time
        fig.add_trace(
            go.Scatter(
                x=daily_metrics['date'],
                y=daily_metrics['complexity'],
                mode='lines+markers',
                name="Avg Complexity",
                line=dict(color='red')
            ),
            row=1, col=1
        )
        
        # Lines of code growth
        fig.add_trace(
            go.Scatter(
                x=daily_metrics['date'],
                y=daily_metrics['lines_of_code'],
                mode='lines+markers',
                name="Total LOC",
                line=dict(color='blue')
            ),
            row=1, col=2
        )
        
        # Function count trends
        fig.add_trace(
            go.Scatter(
                x=daily_metrics['date'],
                y=daily_metrics['functions'],
                mode='lines+markers',
                name="Total Functions",
                line=dict(color='green')
            ),
            row=2, col=1
        )
        
        # Class count trends
        fig.add_trace(
            go.Scatter(
                x=daily_metrics['date'],
                y=daily_metrics['classes'],
                mode='lines+markers',
                name="Total Classes",
                line=dict(color='purple')
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Code Complexity and Growth Trends",
            showlegend=False
        )
        
        fig.write_html(output_file)
        self.console.print(f"Complexity trends visualization saved to {output_file}")
    
    def generate_report(self, output_file: str = "codebase_report.html"):
        """Generate a comprehensive HTML report"""
        # Analyze commit messages
        commit_analysis = self.analyze_commit_messages()
        
        # Generate visualizations
        self.visualize_code_ownership("temp_ownership.html")
        self.visualize_complexity_trends("temp_complexity.html")
        
        # Create comprehensive report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Codebase Time Machine Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ margin: 30px 0; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Codebase Time Machine Analysis Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="section">
                <h2>Repository Overview</h2>
                <div class="metric">Total Commits: {commit_analysis.get('total_commits', 'N/A')}</div>
                <div class="metric">Repository Path: {self.repo_path}</div>
            </div>
            
            <div class="section">
                <h2>Commit Patterns</h2>
                <table>
                    <tr><th>Pattern</th><th>Count</th></tr>
                    {''.join([f'<tr><td>{pattern.replace("_", " ").title()}</td><td>{count}</td></tr>' 
                             for pattern, count in commit_analysis.get('pattern_counts', {}).items()])}
                </table>
            </div>
            
            <div class="section">
                <h2>Top Keywords in Commits</h2>
                <p>{', '.join(commit_analysis.get('top_keywords', [])[:15])}</p>
            </div>
            
            <div class="section">
                <h2>Natural Language Query Examples</h2>
                <p><strong>Try these queries:</strong></p>
                <ul>
                    <li>"Show me how authentication evolved"</li>
                    <li>"What patterns were introduced?"</li>
                    <li>"Who are the main contributors?"</li>
                    <li>"Show complexity trends"</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        # Clean up temp files
        for temp_file in ["temp_ownership.html", "temp_complexity.html"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        self.console.print(f"Comprehensive report generated: {output_file}")


@click.command()
@click.option('--repo-url', help='Git repository URL to clone and analyze')
@click.option('--repo-path', help='Local path to existing repository')
@click.option('--query', help='Natural language query about the codebase')
@click.option('--full-analysis', is_flag=True, help='Run complete analysis including metrics calculation')
def main(repo_url, repo_path, query, full_analysis):
    """Codebase Time Machine - Explore code evolution over time"""
    
    tm = CodebaseTimeMachine()
    
    # Load or clone repository
    if repo_url:
        tm.clone_repository(repo_url)
    elif repo_path:
        tm.repo_path = repo_path
        tm.repo = git.Repo(repo_path)
    else:
        tm.console.print("Please provide either --repo-url or --repo-path")
        return
    
    # Run analysis
    tm.console.print("Starting codebase analysis...")
    
    # Basic analysis
    commits = tm.analyze_commit_history()
    file_changes = tm.extract_file_changes()
    
    if full_analysis:
        # More intensive analysis
        tm.console.print("Running full analysis (this may take a while)...")
        code_metrics = tm.calculate_code_metrics()
    
    # Handle query
    if query:
        response = tm.query_natural_language(query)
        tm.console.print(f"\nQuery: {query}")
        tm.console.print("=" * 50)
        tm.console.print(response)
    
    # Generate visualizations and report
    tm.visualize_code_ownership()
    if full_analysis:
        tm.visualize_complexity_trends()
    tm.generate_report()
    
    tm.console.print("\n✅ Analysis complete! Check the generated HTML files for detailed insights.")


if __name__ == "__main__":
    main()