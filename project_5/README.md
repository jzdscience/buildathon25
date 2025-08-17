# 🌐 Universal Knowledge-Graph Builder

A powerful Python system that transforms documents into interactive knowledge graphs with natural language querying capabilities.

## Features

- **📁 Multi-Source Document Ingestion**: Process plain text files and web URLs (up to 100MB total)
- **🔍 Advanced Entity Extraction**: Automatically identify entities, concepts, and relationships using NLP
- **🕸️ Knowledge Graph Construction**: Build structured graphs representing entity connections
- **🎨 Interactive Visualization**: Explore graphs with beautiful, physics-based visualizations
- **💬 Natural Language Querying**: Ask questions in plain English and get graph-based answers
- **🚀 Web Interface**: User-friendly Flask application for easy interaction
- **⌨️ CLI Tool**: Command-line interface for batch processing and scripting

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this project:
```bash
cd project5
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

## Usage

### Web Interface

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload documents or enter URLs

4. Click "Build Knowledge Graph" to process

5. Use the interface to:
   - Visualize the graph
   - Ask natural language questions
   - Export graph data
   - View statistics

### Command Line Interface

Basic usage:
```bash
python cli.py example_documents/*.txt -i -v
```

Options:
- `-i, --interactive`: Enter interactive query mode
- `-v, --visualize`: Open visualization in browser
- `-o, --output`: Specify output directory
- `--max-size`: Set maximum document size in MB

### Example Queries

The system supports various natural language queries:

- "What are the main topics?"
- "How is artificial intelligence related to machine learning?"
- "Find all person entities"
- "What are the most important concepts?"
- "Show the shortest path from Tesla to climate change"
- "Find entities similar to quantum computing"
- "Show graph statistics"

## Project Structure

```
project5/
├── app.py                  # Flask web application
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── src/
│   ├── document_ingestion.py    # Document loading module
│   ├── entity_extraction.py     # NLP entity extraction
│   ├── knowledge_graph.py       # Graph construction
│   ├── graph_visualizer.py      # Interactive visualization
│   └── query_processor.py       # Natural language queries
├── templates/
│   └── index.html         # Web interface template
├── example_documents/     # Sample documents for testing
├── uploads/              # Uploaded files directory
├── graphs/               # Saved graph data
└── static/               # Static files and visualizations
```

## API Endpoints

The Flask application provides these REST endpoints:

- `POST /upload` - Upload and process documents
- `GET /visualize` - Generate graph visualization
- `POST /visualize_subgraph` - Visualize subgraph around nodes
- `POST /query` - Process natural language query
- `GET /statistics` - Get graph statistics
- `GET /entities` - List entities
- `GET /export` - Export graph as JSON

## Key Technologies

- **NLP**: spaCy for entity recognition and relationship extraction
- **Graph Processing**: NetworkX for graph operations
- **Embeddings**: Sentence Transformers for semantic similarity
- **Visualization**: PyVis for interactive graph rendering
- **Web Framework**: Flask with responsive UI
- **Data Processing**: NumPy, Pandas, scikit-learn

## Example Documents

The project includes sample documents about:
- Artificial Intelligence
- Climate Change
- Quantum Computing

These demonstrate the system's ability to extract entities and relationships from technical content.

## Advanced Features

### Entity Types
The system recognizes various entity types:
- PERSON: People and individuals
- ORG: Organizations and companies
- GPE: Geopolitical entities
- DATE: Temporal expressions
- TECH: Technology terms
- CONCEPT: Abstract concepts
- NOUN_PHRASE: Important noun phrases

### Graph Metrics
- PageRank for entity importance
- Degree centrality for connectivity
- Betweenness centrality for influence
- Community detection for clustering

### Visualization Features
- Interactive node exploration
- Search functionality
- Physics simulation
- Customizable layouts
- Export capabilities

## Troubleshooting

### Common Issues

1. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`

2. **Memory issues with large documents**: Reduce document size or increase system memory

3. **Visualization not loading**: Ensure JavaScript is enabled in your browser

4. **Port already in use**: Change the port in app.py or kill the process using port 5000

## Performance Considerations

- Document processing time scales with size and complexity
- Graph visualization performs best with < 1000 nodes
- Entity extraction quality depends on document structure
- Embedding generation may take time for large graphs

## Future Enhancements

Potential improvements:
- Support for PDF and DOCX files
- Multi-language support
- Real-time collaborative editing
- Graph database integration
- Advanced query language
- Machine learning model fine-tuning
- Export to various graph formats

## License

This project is created for educational purposes as a school project.

## Acknowledgments

Built using open-source libraries and frameworks from the Python ecosystem.
