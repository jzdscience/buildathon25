"""
Main Flask application for the Universal Knowledge-Graph Builder
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from src.document_ingestion import DocumentIngestion
from src.entity_extraction import EntityExtractor
from src.knowledge_graph import KnowledgeGraph
from src.graph_visualizer import GraphVisualizer
from src.query_processor import QueryProcessor
import tempfile
import shutil

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GRAPH_FOLDER'] = 'graphs'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GRAPH_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Global variables for the current graph
current_kg = None
current_visualizer = None
current_query_processor = None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_documents():
    """Handle document upload and processing"""
    global current_kg, current_visualizer, current_query_processor
    
    try:
        files = request.files.getlist('files')
        urls = request.form.get('urls', '').split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        
        # Save uploaded files
        sources = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                sources.append(filepath)
        
        # Add URLs
        sources.extend(urls)
        
        if not sources:
            return jsonify({'error': 'No documents provided'}), 400
        
        # Process documents
        ingestion = DocumentIngestion()
        documents = ingestion.load_documents(sources)
        
        if not documents:
            return jsonify({'error': 'No documents could be loaded'}), 400
        
        # Extract entities and relationships
        extractor = EntityExtractor()
        extraction_results = extractor.extract_entities_and_relations(documents)
        
        # Build knowledge graph
        current_kg = KnowledgeGraph()
        current_kg.build_graph(extraction_results)
        current_kg.generate_embeddings()
        
        # Create visualizer and query processor
        current_visualizer = GraphVisualizer(current_kg.graph)
        current_query_processor = QueryProcessor(current_kg)
        
        # Save graph data
        graph_file = os.path.join(app.config['GRAPH_FOLDER'], 'current_graph.json')
        current_kg.export_to_json(graph_file)
        
        # Get statistics
        stats = current_kg.get_graph_statistics()
        ingestion_stats = ingestion.get_statistics()
        
        return jsonify({
            'success': True,
            'message': 'Knowledge graph built successfully',
            'statistics': {
                'documents': ingestion_stats,
                'graph': stats
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/visualize', methods=['GET'])
def visualize_graph():
    """Generate and return graph visualization"""
    global current_kg, current_visualizer
    
    if not current_kg:
        return jsonify({'error': 'No graph loaded. Please upload documents first.'}), 400
    
    try:
        # Get parameters
        max_nodes = int(request.args.get('max_nodes', 500))
        physics = request.args.get('physics', 'true').lower() == 'true'
        
        # Generate visualization
        output_file = os.path.join('static', 'graph.html')
        current_visualizer.create_interactive_graph(
            output_file=output_file,
            max_nodes=max_nodes,
            physics=physics
        )
        
        return jsonify({
            'success': True,
            'visualization_url': '/static/graph.html'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/visualize_subgraph', methods=['POST'])
def visualize_subgraph():
    """Generate subgraph visualization around specific nodes"""
    global current_kg, current_visualizer
    
    if not current_kg:
        return jsonify({'error': 'No graph loaded. Please upload documents first.'}), 400
    
    try:
        data = request.json
        center_nodes = data.get('nodes', [])
        depth = int(data.get('depth', 2))
        
        if not center_nodes:
            return jsonify({'error': 'No center nodes specified'}), 400
        
        # Generate subgraph visualization
        output_file = os.path.join('static', 'subgraph.html')
        current_visualizer.create_subgraph_visualization(
            center_nodes=center_nodes,
            depth=depth,
            output_file=output_file
        )
        
        return jsonify({
            'success': True,
            'visualization_url': '/static/subgraph.html'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/query', methods=['POST'])
def process_query():
    """Process natural language query"""
    global current_query_processor
    
    if not current_query_processor:
        return jsonify({'error': 'No graph loaded. Please upload documents first.'}), 400
    
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Process query
        result = current_query_processor.process_query(query)
        
        # Generate visualization if suggested
        if 'visualization_hint' in result:
            hint = result['visualization_hint']
            
            if hint == 'relationship' and 'data' in result:
                # Visualize relationship between entities
                entities = []
                if 'entity1' in result['data']:
                    entities.append(result['data']['entity1'])
                if 'entity2' in result['data']:
                    entities.append(result['data']['entity2'])
                if 'path' in result['data'] and result['data']['path']:
                    entities.extend(result['data']['path'])
                
                if entities and current_visualizer:
                    output_file = os.path.join('static', 'query_result.html')
                    current_visualizer.create_subgraph_visualization(
                        center_nodes=list(set(entities)),
                        depth=1,
                        output_file=output_file
                    )
                    result['visualization_url'] = '/static/query_result.html'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export', methods=['GET'])
def export_graph():
    """Export graph data"""
    global current_kg
    
    if not current_kg:
        return jsonify({'error': 'No graph loaded. Please upload documents first.'}), 400
    
    try:
        export_format = request.args.get('format', 'json')
        
        if export_format == 'json':
            export_file = os.path.join(app.config['GRAPH_FOLDER'], 'export.json')
            current_kg.export_to_json(export_file)
            return send_file(export_file, as_attachment=True, download_name='knowledge_graph.json')
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get current graph statistics"""
    global current_kg
    
    if not current_kg:
        return jsonify({'error': 'No graph loaded. Please upload documents first.'}), 400
    
    try:
        stats = current_kg.get_graph_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/entities', methods=['GET'])
def get_entities():
    """Get list of entities"""
    global current_kg
    
    if not current_kg:
        return jsonify({'error': 'No graph loaded. Please upload documents first.'}), 400
    
    try:
        entity_type = request.args.get('type', None)
        limit = int(request.args.get('limit', 100))
        
        if entity_type and entity_type in current_kg.entity_types:
            entities = list(current_kg.entity_types[entity_type])[:limit]
        else:
            entities = list(current_kg.graph.nodes())[:limit]
        
        return jsonify({
            'entities': entities,
            'total': len(entities)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Use PORT environment variable for Cloud Run, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
