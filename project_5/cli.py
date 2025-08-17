#!/usr/bin/env python3
"""
Command-line interface for the Universal Knowledge-Graph Builder
"""

import argparse
import sys
import os
from src.document_ingestion import DocumentIngestion
from src.entity_extraction import EntityExtractor
from src.knowledge_graph import KnowledgeGraph
from src.graph_visualizer import GraphVisualizer
from src.query_processor import QueryProcessor
from colorama import init, Fore, Style
import json

# Initialize colorama for colored output
init(autoreset=True)


def print_header():
    """Print application header"""
    print(Fore.CYAN + "="*60)
    print(Fore.CYAN + "     Universal Knowledge-Graph Builder")
    print(Fore.CYAN + "="*60)
    print()


def print_success(message):
    """Print success message"""
    print(Fore.GREEN + "✓ " + message)


def print_error(message):
    """Print error message"""
    print(Fore.RED + "✗ " + message)


def print_info(message):
    """Print info message"""
    print(Fore.YELLOW + "ℹ " + message)


def build_graph(sources, output_dir="output"):
    """Build knowledge graph from sources"""
    print_header()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Document Ingestion
    print_info("Step 1: Loading documents...")
    ingestion = DocumentIngestion()
    documents = ingestion.load_documents(sources)
    
    if not documents:
        print_error("No documents could be loaded!")
        return None
    
    stats = ingestion.get_statistics()
    print_success(f"Loaded {stats['total_documents']} documents ({stats['total_size_mb']:.2f} MB)")
    
    # Step 2: Entity Extraction
    print_info("Step 2: Extracting entities and relationships...")
    extractor = EntityExtractor()
    extraction_results = extractor.extract_entities_and_relations(documents)
    
    print_success(f"Extracted {extraction_results['statistics']['total_entities']} entities")
    print_success(f"Found {extraction_results['statistics']['total_relationships']} relationships")
    
    # Step 3: Build Knowledge Graph
    print_info("Step 3: Building knowledge graph...")
    kg = KnowledgeGraph()
    kg.build_graph(extraction_results)
    
    graph_stats = kg.get_graph_statistics()
    print_success(f"Built graph with {graph_stats['num_nodes']} nodes and {graph_stats['num_edges']} edges")
    
    # Step 4: Generate Embeddings
    print_info("Step 4: Generating entity embeddings...")
    kg.generate_embeddings()
    print_success("Embeddings generated")
    
    # Step 5: Save Graph
    graph_file = os.path.join(output_dir, "knowledge_graph.json")
    kg.export_to_json(graph_file)
    print_success(f"Graph saved to {graph_file}")
    
    # Step 6: Create Visualization
    print_info("Step 5: Creating visualization...")
    visualizer = GraphVisualizer(kg.graph)
    viz_file = os.path.join(output_dir, "graph_visualization.html")
    visualizer.create_interactive_graph(output_file=viz_file)
    print_success(f"Visualization saved to {viz_file}")
    
    print()
    print_success("Knowledge graph built successfully!")
    
    return kg, visualizer


def interactive_query(kg, visualizer):
    """Interactive query mode"""
    print()
    print(Fore.CYAN + "Interactive Query Mode")
    print(Fore.CYAN + "-" * 30)
    print("Type 'help' for available commands or 'quit' to exit")
    print()
    
    query_processor = QueryProcessor(kg)
    
    while True:
        try:
            query = input(Fore.GREEN + "Query> " + Style.RESET_ALL).strip()
            
            if not query:
                continue
                
            if query.lower() == 'quit':
                print("Goodbye!")
                break
                
            if query.lower() == 'help':
                print_help()
                continue
                
            if query.lower() == 'stats':
                show_statistics(kg)
                continue
                
            if query.lower().startswith('visualize'):
                parts = query.split()
                if len(parts) > 1:
                    entity = ' '.join(parts[1:])
                    visualize_entity(kg, visualizer, entity)
                else:
                    print_error("Please specify an entity to visualize")
                continue
            
            # Process natural language query
            result = query_processor.process_query(query)
            print()
            print(result['answer'])
            
            if 'data' in result and result['data']:
                print()
                print(Fore.CYAN + "Additional Data:")
                print(json.dumps(result['data'], indent=2, default=str))
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print_error(f"Error: {str(e)}")


def print_help():
    """Print help information"""
    print()
    print(Fore.CYAN + "Available Commands:")
    print("  help                - Show this help message")
    print("  stats               - Show graph statistics")
    print("  visualize <entity>  - Visualize subgraph around an entity")
    print("  quit                - Exit the program")
    print()
    print(Fore.CYAN + "Example Queries:")
    print("  What are the main topics?")
    print("  How is X related to Y?")
    print("  Find all person entities")
    print("  What are the most important entities?")
    print("  Show shortest path from A to B")
    print()


def show_statistics(kg):
    """Show graph statistics"""
    stats = kg.get_graph_statistics()
    print()
    print(Fore.CYAN + "Graph Statistics:")
    print(f"  Nodes: {stats['num_nodes']}")
    print(f"  Edges: {stats['num_edges']}")
    print(f"  Density: {stats['density']:.4f}")
    print(f"  Connected: {'Yes' if stats['is_connected'] else 'No'}")
    print(f"  Components: {stats['num_components']}")
    
    if stats['entity_types']:
        print()
        print(Fore.CYAN + "Entity Types:")
        for entity_type, count in stats['entity_types'].items():
            print(f"  {entity_type}: {count}")
    
    if 'top_entities' in stats:
        print()
        print(Fore.CYAN + "Top Entities:")
        for i, entity in enumerate(stats['top_entities'][:5], 1):
            print(f"  {i}. {entity['entity']} (score: {entity['score']:.4f})")


def visualize_entity(kg, visualizer, entity):
    """Visualize subgraph around an entity"""
    # Find best matching entity
    if entity not in kg.graph:
        # Try to find similar entity
        for node in kg.graph.nodes():
            if entity.lower() in node.lower():
                entity = node
                break
    
    if entity not in kg.graph:
        print_error(f"Entity '{entity}' not found in graph")
        return
    
    output_file = f"subgraph_{entity.replace(' ', '_')}.html"
    visualizer.create_subgraph_visualization([entity], depth=2, output_file=output_file)
    print_success(f"Subgraph visualization saved to {output_file}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Universal Knowledge-Graph Builder - Transform documents into interactive knowledge graphs"
    )
    
    parser.add_argument(
        'sources',
        nargs='+',
        help='Document sources (files or URLs)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output',
        help='Output directory (default: output)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Enter interactive query mode after building'
    )
    
    parser.add_argument(
        '-v', '--visualize',
        action='store_true',
        help='Open visualization in browser after building'
    )
    
    parser.add_argument(
        '--max-size',
        type=int,
        default=100,
        help='Maximum total size in MB (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Build knowledge graph
    result = build_graph(args.sources, args.output)
    
    if result:
        kg, visualizer = result
        
        # Open visualization if requested
        if args.visualize:
            import webbrowser
            viz_file = os.path.join(args.output, "graph_visualization.html")
            webbrowser.open(f"file://{os.path.abspath(viz_file)}")
        
        # Enter interactive mode if requested
        if args.interactive:
            interactive_query(kg, visualizer)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
