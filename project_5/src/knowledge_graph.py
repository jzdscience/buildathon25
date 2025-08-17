"""
Knowledge Graph Construction Module
Builds and manages the knowledge graph structure
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
import json
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class KnowledgeGraph:
    """Manages the knowledge graph structure and operations"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_embeddings = {}
        self.embedding_model = None
        self.entity_types = defaultdict(set)
        self.entity_attributes = defaultdict(dict)
        
    def build_graph(self, extraction_results: Dict[str, Any]) -> None:
        """
        Build knowledge graph from extracted entities and relationships
        
        Args:
            extraction_results: Dictionary containing entities and relationships
        """
        print("Building knowledge graph...")
        
        # Add entities as nodes
        self._add_entities(extraction_results['entities'])
        
        # Add relationships as edges
        self._add_relationships(extraction_results['relationships'])
        
        # Add entity contexts as attributes
        if 'entity_contexts' in extraction_results:
            self._add_entity_contexts(extraction_results['entity_contexts'])
        
        # Calculate graph metrics
        self._calculate_metrics()
        
        print(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def _add_entities(self, entities: Dict[str, List[str]]) -> None:
        """Add entities as nodes to the graph"""
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                self.graph.add_node(entity, type=entity_type)
                self.entity_types[entity_type].add(entity)
                self.entity_attributes[entity]['type'] = entity_type
    
    def _add_relationships(self, relationships: List[Dict[str, str]]) -> None:
        """Add relationships as edges to the graph"""
        for rel in relationships:
            source = rel['source']
            target = rel['target']
            relation = rel['relation']
            
            # Ensure both nodes exist
            if source not in self.graph:
                self.graph.add_node(source, type='ENTITY')
            if target not in self.graph:
                self.graph.add_node(target, type='ENTITY')
            
            # Add edge with relationship type and context
            self.graph.add_edge(
                source, 
                target, 
                relation=relation,
                context=rel.get('context', '')
            )
    
    def _add_entity_contexts(self, entity_contexts: Dict[str, List[Dict]]) -> None:
        """Add context information to entities"""
        for entity, contexts in entity_contexts.items():
            if entity in self.graph:
                self.graph.nodes[entity]['contexts'] = contexts
                self.entity_attributes[entity]['contexts'] = contexts
    
    def _calculate_metrics(self) -> None:
        """Calculate various graph metrics"""
        # Calculate centrality measures
        if self.graph.number_of_nodes() > 0:
            try:
                # Degree centrality
                degree_centrality = nx.degree_centrality(self.graph)
                for node, centrality in degree_centrality.items():
                    self.graph.nodes[node]['degree_centrality'] = centrality
                
                # PageRank
                pagerank = nx.pagerank(self.graph, max_iter=100)
                for node, rank in pagerank.items():
                    self.graph.nodes[node]['pagerank'] = rank
                    
                # Betweenness centrality (for smaller graphs)
                if self.graph.number_of_nodes() < 1000:
                    betweenness = nx.betweenness_centrality(self.graph)
                    for node, centrality in betweenness.items():
                        self.graph.nodes[node]['betweenness_centrality'] = centrality
            except:
                pass  # Skip metrics if graph structure doesn't support them
    
    def generate_embeddings(self, model_name: str = 'all-MiniLM-L6-v2') -> None:
        """Generate embeddings for entities using sentence transformers"""
        print("Generating entity embeddings...")
        
        if not self.embedding_model:
            self.embedding_model = SentenceTransformer(model_name)
        
        # Generate embeddings for all entities
        entities = list(self.graph.nodes())
        if entities:
            embeddings = self.embedding_model.encode(entities)
            
            for entity, embedding in zip(entities, embeddings):
                self.entity_embeddings[entity] = embedding
    
    def find_similar_entities(self, entity: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar entities based on embeddings"""
        if entity not in self.entity_embeddings:
            return []
        
        entity_embedding = self.entity_embeddings[entity].reshape(1, -1)
        similarities = []
        
        for other_entity, other_embedding in self.entity_embeddings.items():
            if other_entity != entity:
                similarity = cosine_similarity(
                    entity_embedding, 
                    other_embedding.reshape(1, -1)
                )[0][0]
                similarities.append((other_entity, float(similarity)))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_subgraph(self, nodes: List[str], depth: int = 1) -> nx.MultiDiGraph:
        """Get subgraph around specified nodes"""
        subgraph_nodes = set(nodes)
        
        for _ in range(depth):
            new_nodes = set()
            for node in subgraph_nodes:
                if node in self.graph:
                    # Add neighbors
                    new_nodes.update(self.graph.predecessors(node))
                    new_nodes.update(self.graph.successors(node))
            subgraph_nodes.update(new_nodes)
        
        return self.graph.subgraph(subgraph_nodes)
    
    def get_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two entities"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None
    
    def get_entity_info(self, entity: str) -> Dict[str, Any]:
        """Get detailed information about an entity"""
        if entity not in self.graph:
            return {}
        
        info = {
            'name': entity,
            'attributes': dict(self.graph.nodes[entity]),
            'incoming_edges': [],
            'outgoing_edges': [],
            'neighbors': list(self.graph.neighbors(entity))
        }
        
        # Get incoming edges
        for source, target, data in self.graph.in_edges(entity, data=True):
            info['incoming_edges'].append({
                'source': source,
                'relation': data.get('relation', 'related_to')
            })
        
        # Get outgoing edges
        for source, target, data in self.graph.out_edges(entity, data=True):
            info['outgoing_edges'].append({
                'target': target,
                'relation': data.get('relation', 'related_to')
            })
        
        return info
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the graph"""
        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph) if self.graph.is_directed() else nx.is_connected(self.graph),
            'num_components': nx.number_weakly_connected_components(self.graph) if self.graph.is_directed() else nx.number_connected_components(self.graph),
            'entity_types': {k: len(v) for k, v in self.entity_types.items()},
        }
        
        # Add top entities by centrality
        if self.graph.number_of_nodes() > 0:
            pagerank_scores = nx.pagerank(self.graph, max_iter=100)
            top_entities = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            stats['top_entities'] = [{'entity': e, 'score': s} for e, s in top_entities]
        
        return stats
    
    def export_to_json(self, filepath: str) -> None:
        """Export graph to JSON format"""
        graph_data = {
            'nodes': [
                {
                    'id': node,
                    'label': node,
                    **self.graph.nodes[node]
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': source,
                    'target': target,
                    'relation': data.get('relation', 'related_to'),
                    'context': data.get('context', '')
                }
                for source, target, data in self.graph.edges(data=True)
            ],
            'statistics': self.get_graph_statistics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(graph_data, f, indent=2, default=str)
    
    def import_from_json(self, filepath: str) -> None:
        """Import graph from JSON format"""
        with open(filepath, 'r') as f:
            graph_data = json.load(f)
        
        self.graph.clear()
        
        # Add nodes
        for node_data in graph_data['nodes']:
            node_id = node_data.pop('id')
            self.graph.add_node(node_id, **node_data)
        
        # Add edges
        for edge_data in graph_data['edges']:
            self.graph.add_edge(
                edge_data['source'],
                edge_data['target'],
                relation=edge_data.get('relation', 'related_to'),
                context=edge_data.get('context', '')
            )
