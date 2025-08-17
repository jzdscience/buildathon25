"""
Natural Language Query Processing Module
Handles NL questions and returns graph-based answers
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class QueryProcessor:
    """Processes natural language queries over the knowledge graph"""
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.graph = knowledge_graph.graph
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Define query patterns and handlers
        self.query_patterns = [
            {
                'pattern': r'what are the (main|key|important|top) (topics|concepts|entities)',
                'handler': self._get_main_topics
            },
            {
                'pattern': r'how (is|are) (.*) (related|connected) to (.*)',
                'handler': self._find_relationship
            },
            {
                'pattern': r'what (is|are) (.*)',
                'handler': self._get_entity_info
            },
            {
                'pattern': r'(find|show|list) all (.*) (entities|concepts|topics)',
                'handler': self._find_entities_by_type
            },
            {
                'pattern': r'(shortest|best) (path|route|connection) (from|between) (.*) (to|and) (.*)',
                'handler': self._find_path
            },
            {
                'pattern': r'(similar|related) to (.*)',
                'handler': self._find_similar
            },
            {
                'pattern': r'(neighbors|connections) of (.*)',
                'handler': self._get_neighbors
            },
            {
                'pattern': r'(statistics|stats|summary|overview)',
                'handler': self._get_statistics
            },
            {
                'pattern': r'most (important|central|connected) (entities|nodes|concepts)',
                'handler': self._get_most_important
            },
            {
                'pattern': r'(cluster|group|community)',
                'handler': self._find_communities
            }
        ]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return results
        
        Args:
            query: Natural language question
            
        Returns:
            Dictionary containing the answer and relevant data
        """
        query_lower = query.lower().strip()
        
        # Try to match query patterns
        for pattern_dict in self.query_patterns:
            pattern = pattern_dict['pattern']
            handler = pattern_dict['handler']
            
            match = re.search(pattern, query_lower)
            if match:
                return handler(query_lower, match)
        
        # If no pattern matches, use semantic search
        return self._semantic_search(query)
    
    def _get_main_topics(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Get main topics/concepts from the graph"""
        # Get top nodes by PageRank
        if self.graph.number_of_nodes() == 0:
            return {
                'answer': 'The knowledge graph is empty.',
                'data': []
            }
        
        pagerank = nx.pagerank(self.graph, max_iter=100)
        top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Group by type
        topics_by_type = {}
        for node, score in top_nodes:
            node_type = self.graph.nodes[node].get('type', 'ENTITY')
            if node_type not in topics_by_type:
                topics_by_type[node_type] = []
            topics_by_type[node_type].append({
                'name': node,
                'importance': score,
                'connections': self.graph.degree(node)
            })
        
        answer_parts = ["The main topics and concepts in the knowledge graph are:"]
        for node_type, topics in topics_by_type.items():
            answer_parts.append(f"\n{node_type}:")
            for topic in topics[:5]:
                answer_parts.append(f"  • {topic['name']} (importance: {topic['importance']:.4f}, connections: {topic['connections']})")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {
                'topics': topics_by_type,
                'total_topics': len(top_nodes)
            },
            'visualization_hint': 'main_topics'
        }
    
    def _find_relationship(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Find how two entities are related"""
        # Extract entity names from the query
        parts = re.split(r'(related|connected) to', query)
        if len(parts) < 2:
            return {'answer': 'Could not parse entities from the query.', 'data': {}}
        
        entity1_part = parts[0].replace('how is', '').replace('how are', '').strip()
        entity2_part = parts[1].strip()
        
        # Find best matching entities in the graph
        entity1 = self._find_best_match(entity1_part)
        entity2 = self._find_best_match(entity2_part)
        
        if not entity1 or not entity2:
            return {
                'answer': f"Could not find one or both entities in the graph.",
                'data': {'searched_for': [entity1_part, entity2_part]}
            }
        
        # Check direct relationships
        direct_relations = []
        if self.graph.has_edge(entity1, entity2):
            for _, _, data in self.graph.edges(entity1, keys=True, data=True):
                if _ == entity1 and data.get('target') == entity2:
                    direct_relations.append(data.get('relation', 'related_to'))
        
        if self.graph.has_edge(entity2, entity1):
            for _, _, data in self.graph.edges(entity2, keys=True, data=True):
                if _ == entity2 and data.get('target') == entity1:
                    direct_relations.append(f"{data.get('relation', 'related_to')} (reverse)")
        
        # Find shortest path
        path = self.kg.get_shortest_path(entity1, entity2)
        
        answer_parts = [f"Relationship between '{entity1}' and '{entity2}':"]
        
        if direct_relations:
            answer_parts.append(f"\nDirect relationships: {', '.join(direct_relations)}")
        
        if path and len(path) > 2:
            answer_parts.append(f"\nIndirect connection path ({len(path)-1} steps):")
            for i in range(len(path)-1):
                if self.graph.has_edge(path[i], path[i+1]):
                    edge_data = list(self.graph.get_edge_data(path[i], path[i+1]).values())[0]
                    relation = edge_data.get('relation', 'connected to')
                    answer_parts.append(f"  {path[i]} --[{relation}]--> {path[i+1]}")
        elif path and len(path) == 2:
            answer_parts.append("\nThey are directly connected.")
        elif not path:
            answer_parts.append("\nNo connection path found between these entities.")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {
                'entity1': entity1,
                'entity2': entity2,
                'direct_relations': direct_relations,
                'path': path
            },
            'visualization_hint': 'relationship'
        }
    
    def _get_entity_info(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Get information about a specific entity"""
        # Extract entity name
        entity_part = query.replace('what is', '').replace('what are', '').strip()
        entity = self._find_best_match(entity_part)
        
        if not entity:
            return {
                'answer': f"Could not find '{entity_part}' in the knowledge graph.",
                'data': {}
            }
        
        info = self.kg.get_entity_info(entity)
        
        answer_parts = [f"Information about '{entity}':"]
        
        # Type and attributes
        if 'type' in info['attributes']:
            answer_parts.append(f"\nType: {info['attributes']['type']}")
        
        # Importance metrics
        if 'pagerank' in info['attributes']:
            answer_parts.append(f"Importance score: {info['attributes']['pagerank']:.4f}")
        
        # Connections
        answer_parts.append(f"\nConnections:")
        answer_parts.append(f"  • Incoming: {len(info['incoming_edges'])} relationships")
        answer_parts.append(f"  • Outgoing: {len(info['outgoing_edges'])} relationships")
        
        # Sample relationships
        if info['incoming_edges']:
            answer_parts.append("\nSample incoming relationships:")
            for edge in info['incoming_edges'][:3]:
                answer_parts.append(f"  • {edge['source']} --[{edge['relation']}]--> {entity}")
        
        if info['outgoing_edges']:
            answer_parts.append("\nSample outgoing relationships:")
            for edge in info['outgoing_edges'][:3]:
                answer_parts.append(f"  • {entity} --[{edge['relation']}]--> {edge['target']}")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': info,
            'visualization_hint': 'entity_info'
        }
    
    def _find_entities_by_type(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Find all entities of a specific type"""
        # Extract type from query
        type_match = re.search(r'all (\w+)', query)
        if not type_match:
            return {'answer': 'Could not determine entity type from query.', 'data': {}}
        
        requested_type = type_match.group(1).upper()
        
        # Find matching type
        matching_types = []
        for entity_type in self.kg.entity_types.keys():
            if requested_type in entity_type.upper() or entity_type.upper() in requested_type:
                matching_types.append(entity_type)
        
        if not matching_types:
            return {
                'answer': f"No entities of type '{requested_type}' found.",
                'data': {'available_types': list(self.kg.entity_types.keys())}
            }
        
        results = {}
        for entity_type in matching_types:
            entities = list(self.kg.entity_types[entity_type])[:20]
            results[entity_type] = entities
        
        answer_parts = [f"Found entities of type(s) {', '.join(matching_types)}:"]
        for entity_type, entities in results.items():
            answer_parts.append(f"\n{entity_type} ({len(self.kg.entity_types[entity_type])} total):")
            for entity in entities[:10]:
                answer_parts.append(f"  • {entity}")
            if len(self.kg.entity_types[entity_type]) > 10:
                answer_parts.append(f"  ... and {len(self.kg.entity_types[entity_type]) - 10} more")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': results,
            'visualization_hint': 'entity_type'
        }
    
    def _find_path(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Find shortest path between entities"""
        # Extract entities
        parts = re.split(r'(from|between)', query)
        if len(parts) < 2:
            return {'answer': 'Could not parse entities from query.', 'data': {}}
        
        parts2 = re.split(r'(to|and)', parts[-1])
        if len(parts2) < 2:
            return {'answer': 'Could not parse second entity from query.', 'data': {}}
        
        entity1_part = parts[-1].split()[0] if 'between' in query else parts[-1].replace('to', '').replace('and', '').strip()
        entity2_part = parts2[-1].strip()
        
        entity1 = self._find_best_match(entity1_part)
        entity2 = self._find_best_match(entity2_part)
        
        if not entity1 or not entity2:
            return {
                'answer': f"Could not find one or both entities in the graph.",
                'data': {}
            }
        
        path = self.kg.get_shortest_path(entity1, entity2)
        
        if path:
            answer_parts = [f"Shortest path from '{entity1}' to '{entity2}' ({len(path)-1} steps):"]
            for i in range(len(path)-1):
                answer_parts.append(f"  Step {i+1}: {path[i]} → {path[i+1]}")
        else:
            answer_parts = [f"No path found between '{entity1}' and '{entity2}'."]
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {'path': path, 'length': len(path)-1 if path else None},
            'visualization_hint': 'path'
        }
    
    def _find_similar(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Find similar entities"""
        # Extract entity
        entity_part = query.replace('similar to', '').replace('related to', '').strip()
        entity = self._find_best_match(entity_part)
        
        if not entity:
            return {
                'answer': f"Could not find '{entity_part}' in the knowledge graph.",
                'data': {}
            }
        
        # Generate embeddings if not already done
        if not self.kg.entity_embeddings:
            self.kg.generate_embeddings()
        
        similar = self.kg.find_similar_entities(entity, top_k=10)
        
        answer_parts = [f"Entities similar to '{entity}':"]
        for similar_entity, similarity in similar:
            answer_parts.append(f"  • {similar_entity} (similarity: {similarity:.3f})")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {'entity': entity, 'similar': similar},
            'visualization_hint': 'similar'
        }
    
    def _get_neighbors(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Get neighbors of an entity"""
        # Extract entity
        entity_part = query.replace('neighbors of', '').replace('connections of', '').strip()
        entity = self._find_best_match(entity_part)
        
        if not entity:
            return {
                'answer': f"Could not find '{entity_part}' in the knowledge graph.",
                'data': {}
            }
        
        predecessors = list(self.graph.predecessors(entity))
        successors = list(self.graph.successors(entity))
        
        answer_parts = [f"Connections of '{entity}':"]
        
        if predecessors:
            answer_parts.append(f"\nIncoming connections ({len(predecessors)}):")
            for pred in predecessors[:10]:
                answer_parts.append(f"  • {pred}")
            if len(predecessors) > 10:
                answer_parts.append(f"  ... and {len(predecessors) - 10} more")
        
        if successors:
            answer_parts.append(f"\nOutgoing connections ({len(successors)}):")
            for succ in successors[:10]:
                answer_parts.append(f"  • {succ}")
            if len(successors) > 10:
                answer_parts.append(f"  ... and {len(successors) - 10} more")
        
        if not predecessors and not successors:
            answer_parts.append("\nThis entity has no connections.")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {
                'entity': entity,
                'predecessors': predecessors,
                'successors': successors
            },
            'visualization_hint': 'neighbors'
        }
    
    def _get_statistics(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Get graph statistics"""
        stats = self.kg.get_graph_statistics()
        
        answer_parts = ["Knowledge Graph Statistics:"]
        answer_parts.append(f"\n• Total nodes: {stats['num_nodes']}")
        answer_parts.append(f"• Total edges: {stats['num_edges']}")
        answer_parts.append(f"• Graph density: {stats['density']:.4f}")
        answer_parts.append(f"• Connected: {'Yes' if stats['is_connected'] else 'No'}")
        answer_parts.append(f"• Number of components: {stats['num_components']}")
        
        if stats['entity_types']:
            answer_parts.append("\nEntity types:")
            for entity_type, count in stats['entity_types'].items():
                answer_parts.append(f"  • {entity_type}: {count}")
        
        if 'top_entities' in stats:
            answer_parts.append("\nMost important entities:")
            for i, entity_data in enumerate(stats['top_entities'][:5], 1):
                answer_parts.append(f"  {i}. {entity_data['entity']} (score: {entity_data['score']:.4f})")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': stats,
            'visualization_hint': 'statistics'
        }
    
    def _get_most_important(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Get most important/central entities"""
        # Calculate different centrality measures
        pagerank = nx.pagerank(self.graph, max_iter=100)
        degree_centrality = nx.degree_centrality(self.graph)
        
        # Get top entities by PageRank
        top_by_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get top by degree
        top_by_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        answer_parts = ["Most important entities in the knowledge graph:"]
        
        answer_parts.append("\nBy PageRank (overall importance):")
        for entity, score in top_by_pagerank[:5]:
            entity_type = self.graph.nodes[entity].get('type', 'ENTITY')
            answer_parts.append(f"  • {entity} ({entity_type}) - score: {score:.4f}")
        
        answer_parts.append("\nBy degree centrality (most connected):")
        for entity, score in top_by_degree[:5]:
            connections = self.graph.degree(entity)
            answer_parts.append(f"  • {entity} - {connections} connections")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {
                'pagerank': top_by_pagerank,
                'degree': top_by_degree
            },
            'visualization_hint': 'important_entities'
        }
    
    def _find_communities(self, query: str, match: re.Match) -> Dict[str, Any]:
        """Find communities/clusters in the graph"""
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        # Find communities using Louvain method
        import networkx.algorithms.community as nx_comm
        communities = list(nx_comm.greedy_modularity_communities(undirected))
        
        answer_parts = [f"Found {len(communities)} communities in the knowledge graph:"]
        
        for i, community in enumerate(communities[:5], 1):
            community_list = list(community)[:10]
            answer_parts.append(f"\nCommunity {i} ({len(community)} members):")
            for member in community_list[:5]:
                answer_parts.append(f"  • {member}")
            if len(community) > 5:
                answer_parts.append(f"  ... and {len(community) - 5} more")
        
        if len(communities) > 5:
            answer_parts.append(f"\n... and {len(communities) - 5} more communities")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {
                'num_communities': len(communities),
                'communities': [list(c) for c in communities[:5]]
            },
            'visualization_hint': 'communities'
        }
    
    def _semantic_search(self, query: str) -> Dict[str, Any]:
        """Fallback semantic search when no pattern matches"""
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Generate embeddings for entities if not done
        if not self.kg.entity_embeddings:
            self.kg.generate_embeddings()
        
        # Find most similar entities
        similarities = []
        for entity, embedding in self.kg.entity_embeddings.items():
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                embedding.reshape(1, -1)
            )[0][0]
            similarities.append((entity, similarity))
        
        # Sort and get top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:10]
        
        answer_parts = [f"Most relevant entities for '{query}':"]
        for entity, similarity in top_results:
            entity_type = self.graph.nodes[entity].get('type', 'ENTITY')
            answer_parts.append(f"  • {entity} ({entity_type}) - relevance: {similarity:.3f}")
        
        return {
            'answer': '\n'.join(answer_parts),
            'data': {
                'query': query,
                'results': top_results
            },
            'visualization_hint': 'search_results'
        }
    
    def _find_best_match(self, text: str) -> Optional[str]:
        """Find best matching entity in the graph"""
        text_lower = text.lower().strip()
        
        # First try exact match
        for node in self.graph.nodes():
            if node.lower() == text_lower:
                return node
        
        # Try partial match
        for node in self.graph.nodes():
            if text_lower in node.lower() or node.lower() in text_lower:
                return node
        
        # Try fuzzy match using embeddings
        if not self.kg.entity_embeddings:
            self.kg.generate_embeddings()
        
        text_embedding = self.embedding_model.encode([text])[0]
        best_match = None
        best_similarity = 0
        
        for entity, embedding in self.kg.entity_embeddings.items():
            similarity = cosine_similarity(
                text_embedding.reshape(1, -1),
                embedding.reshape(1, -1)
            )[0][0]
            
            if similarity > best_similarity and similarity > 0.5:
                best_similarity = similarity
                best_match = entity
        
        return best_match
