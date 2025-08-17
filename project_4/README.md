# Codebase Time Machine

A powerful tool that allows developers to explore the evolution of any codebase over time, providing insights into how features, design patterns, and architectural decisions have changed, while connecting these changes to business context.

## Features

- **Git Repository Analysis**: Clone and analyze the complete commit history of any Git repository
- **Semantic Code Interpretation**: Extract and interpret code changes over time (refactorings, feature introductions, removals)
- **Natural Language Queries**: Ask questions like "Why was this pattern introduced?" or "Show me how authentication evolved"
- **Rich Visualizations**: Generate interactive charts for code ownership, complexity trends, and growth patterns
- **Business Context Linking**: Connect commits and code changes to high-level business features based on commit messages and patterns

## Installation

### Option 1: Automatic Installation (Recommended)

1. Clone or download this project
2. Run the installation script:

**On macOS/Linux:**
```bash
chmod +x install.sh
./install.sh
```

**On Windows or manual installation:**
```bash
python3 install.py
```

### Option 2: Manual Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Download NLTK data (if needed):
```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

## Usage

### 🌐 Web Interface (Recommended for Demos)

The easiest way to use and demo the Codebase Time Machine is through the web interface:

1. **Start the web server:**
```bash
python3 start_web.py
```

2. **Open your browser to:** `http://localhost:5000`

3. **Try the demo with example repositories** or analyze your own!

**Web Interface Features:**
- 🖱️ **User-friendly interface** - No command line needed
- 📊 **Interactive visualizations** - Plotly charts embedded in the browser
- 🔄 **Real-time progress** - Live updates during analysis
- 💬 **Natural language queries** - Ask questions directly in the web UI
- 📱 **Mobile responsive** - Works on all devices
- 🚀 **One-click demos** - Pre-configured example repositories

### 💻 Command Line Interface

For advanced users or automation:

**Basic Analysis:**
```bash
python3 codebase_time_machine.py --repo-url https://github.com/user/repository.git
```

**Local Repository:**
```bash
python3 codebase_time_machine.py --repo-path /path/to/local/repo
```

**Full Analysis (includes code metrics):**
```bash
python3 codebase_time_machine.py --repo-url https://github.com/user/repository.git --full-analysis
```

**Natural Language Queries:**
```bash
python3 codebase_time_machine.py --repo-path ./my-repo --query "Show me how authentication evolved"
```

## Example Queries

The tool supports various types of natural language queries:

- **Authentication Evolution**: "Show me how authentication evolved" or "How did auth change?"
- **Pattern Analysis**: "What patterns were introduced?" or "Show me design patterns"
- **Contributor Analysis**: "Who are the main contributors?" or "Show me code ownership"
- **Complexity Trends**: "Show complexity trends" or "How did complexity grow?"
- **Feature History**: "When was feature X added?" or "Show me API changes"

## Output

### 🌐 Web Interface Output

When using the web interface, results are displayed directly in your browser:

- **Interactive Dashboard**: Real-time analysis progress and results
- **Embedded Visualizations**: Charts displayed directly in the web page
- **Query Interface**: Ask questions and get instant responses
- **Downloadable Reports**: Export results as HTML files
- **Shareable Links**: Share analysis results with others

### 💻 Command Line Output

The CLI tool generates several types of output:

1. **Console Output**: Real-time progress and query responses
2. **Interactive Visualizations**: 
   - `code_ownership.html`: Code ownership by contributors
   - `complexity_trends.html`: Complexity and growth trends over time
3. **Comprehensive Report**: `codebase_report.html` with overview and insights
4. **Database**: `codebase_analysis.db` with structured analysis data

## Architecture

The tool consists of several key components:

### Core Classes

- **CodebaseTimeMachine**: Main orchestrator class
- **CommitInfo**: Data structure for commit information
- **FileChange**: Data structure for file-level changes
- **CodeMetrics**: Data structure for code complexity metrics

### Key Features

1. **Repository Cloning**: Automatic cloning and local repository handling
2. **Commit Analysis**: Complete commit history extraction with statistics
3. **File Change Tracking**: Detailed tracking of file additions, modifications, deletions
4. **Code Metrics**: Complexity calculation for Python files (extensible to other languages)
5. **Natural Language Processing**: Query understanding and response generation
6. **Data Visualization**: Interactive charts using Plotly
7. **Database Storage**: SQLite database for persistent analysis results

### Supported Languages

Currently optimized for Python analysis, but supports change tracking for:
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- PHP (.php)
- Ruby (.rb)
- Go (.go)
- Rust (.rs)
- Swift (.swift)
- Kotlin (.kt)
- Scala (.scala)
- Vue (.vue)
- HTML/CSS (.html, .css, .scss, .sass)

## Database Schema

The tool uses SQLite to store analysis results:

```sql
-- Commits table
CREATE TABLE commits (
    hash TEXT PRIMARY KEY,
    author TEXT,
    date TEXT,
    message TEXT,
    files_changed INTEGER,
    insertions INTEGER,
    deletions INTEGER
);

-- File changes table
CREATE TABLE file_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT,
    change_type TEXT,
    lines_added INTEGER,
    lines_deleted INTEGER,
    commit_hash TEXT,
    FOREIGN KEY (commit_hash) REFERENCES commits (hash)
);

-- Code metrics table
CREATE TABLE code_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT,
    lines_of_code INTEGER,
    complexity INTEGER,
    functions INTEGER,
    classes INTEGER,
    commit_hash TEXT,
    FOREIGN KEY (commit_hash) REFERENCES commits (hash)
);
```

## Example Analysis Results

### Code Ownership Visualization
- Bar charts showing commits and lines of code by author
- Heatmap of file ownership
- Activity timeline

### Complexity Trends
- Complexity evolution over time
- Lines of code growth
- Function and class count trends

### Commit Pattern Analysis
- Bug fixes, features, refactoring patterns
- Business context identification
- Keyword extraction and clustering

## Contributing

To extend the tool:

1. **Add Language Support**: Extend `is_code_file()` and `calculate_complexity()` methods
2. **Improve NLP**: Enhance the `query_natural_language()` method with more sophisticated understanding
3. **Add Visualizations**: Create new visualization methods in the main class
4. **Extend Metrics**: Add more code quality metrics beyond complexity

## Dependencies

- **gitpython**: Git repository interaction
- **pandas/numpy**: Data manipulation and analysis
- **matplotlib/seaborn/plotly**: Data visualization
- **nltk/textblob/scikit-learn**: Natural language processing
- **click**: Command-line interface
- **rich**: Enhanced terminal output
- **tree-sitter**: Code parsing (for future language support)

## Performance Considerations

- **Large Repositories**: Analysis time scales with repository size and history length
- **Memory Usage**: Consider using `--full-analysis` only for smaller repositories initially
- **Database**: Analysis results are cached in SQLite for faster subsequent queries
- **Visualization**: HTML files are generated locally and can be large for big repositories

## Future Enhancements

- Support for more programming languages
- Integration with issue tracking systems (JIRA, GitHub Issues)
- Machine learning-based commit classification
- Real-time repository monitoring
- API integration for CI/CD pipelines
- Advanced refactoring detection
- Code quality trend predictions