"""
Graph Visualization Module
Creates interactive visualizations of the knowledge graph
"""

from pyvis.network import Network
import networkx as nx
from typing import Dict, List, Any, Optional
import json
import os


class GraphVisualizer:
    """Creates interactive visualizations of the knowledge graph"""
    
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.color_map = {
            'PERSON': '#FF6B6B',
            'ORG': '#4ECDC4',
            'GPE': '#45B7D1',
            'DATE': '#96CEB4',
            'CONCEPT': '#FFEAA7',
            'NOUN_PHRASE': '#DFE6E9',
            'ENTITY': '#74B9FF',
            'TECH': '#A29BFE',
            'LOC': '#55A3FF',
            'default': '#B2BEC3'
        }
    
    def create_interactive_graph(
        self, 
        output_file: str = 'knowledge_graph.html',
        subset_nodes: Optional[List[str]] = None,
        max_nodes: int = 500,
        physics: bool = True
    ) -> str:
        """
        Create an interactive HTML visualization of the graph
        
        Args:
            output_file: Output HTML file path
            subset_nodes: Optional list of nodes to include
            max_nodes: Maximum number of nodes to display
            physics: Enable physics simulation
            
        Returns:
            Path to the created HTML file
        """
        # Create network
        net = Network(
            height='750px', 
            width='100%', 
            bgcolor='#222222', 
            font_color='white',
            notebook=False,
            directed=True
        )
        
        # Configure physics
        if physics:
            net.barnes_hut(
                gravity=-80000,
                central_gravity=0.3,
                spring_length=100,
                spring_strength=0.001,
                damping=0.09
            )
        else:
            net.toggle_physics(False)
        
        # Select nodes to visualize
        if subset_nodes:
            nodes_to_show = subset_nodes
        else:
            # Select top nodes by PageRank
            if self.graph.number_of_nodes() > max_nodes:
                pagerank = nx.pagerank(self.graph, max_iter=100)
                top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
                nodes_to_show = [node for node, _ in top_nodes]
            else:
                nodes_to_show = list(self.graph.nodes())
        
        # Create subgraph
        subgraph = self.graph.subgraph(nodes_to_show)
        
        # Add nodes
        for node in subgraph.nodes():
            node_data = self.graph.nodes[node]
            node_type = node_data.get('type', 'default')
            color = self.color_map.get(node_type, self.color_map['default'])
            
            # Calculate node size based on degree
            degree = self.graph.degree(node)
            size = min(10 + degree * 2, 50)
            
            # Create hover text
            hover_text = self._create_hover_text(node, node_data)
            
            net.add_node(
                node,
                label=node[:30] + '...' if len(node) > 30 else node,
                color=color,
                size=size,
                title=hover_text,
                font={'size': 12}
            )
        
        # Add edges
        edge_counts = {}
        for source, target, data in subgraph.edges(data=True):
            relation = data.get('relation', 'related_to')
            
            # Track multiple edges between same nodes
            edge_key = (source, target)
            if edge_key in edge_counts:
                edge_counts[edge_key] += 1
                relation = f"{relation} ({edge_counts[edge_key]})"
            else:
                edge_counts[edge_key] = 1
            
            net.add_edge(
                source, 
                target,
                title=relation,
                label=relation if len(relation) < 20 else '',
                color='#636e72',
                arrows='to',
                smooth={'type': 'curvedCW', 'roundness': 0.2}
            )
        
        # Add navigation buttons and search
        net.set_options("""
        var options = {
            "nodes": {
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "font": {
                    "size": 12,
                    "face": "Tahoma"
                }
            },
            "edges": {
                "color": {
                    "inherit": false
                },
                "smooth": {
                    "type": "continuous"
                },
                "font": {
                    "size": 10,
                    "align": "middle"
                }
            },
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -30000,
                    "centralGravity": 0.3,
                    "springLength": 95
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "stabilization": {
                    "enabled": true,
                    "iterations": 200
                }
            },
            "interaction": {
                "hover": true,
                "navigationButtons": true,
                "keyboard": {
                    "enabled": true
                },
                "multiselect": true,
                "dragView": true,
                "zoomView": true
            }
        }
        """)
        
        # Save the graph
        net.save_graph(output_file)
        
        # Add custom styling and features
        self._enhance_html(output_file)
        
        return output_file
    
    def _create_hover_text(self, node: str, node_data: Dict) -> str:
        """Create hover text for a node"""
        lines = [f"<b>{node}</b>"]
        
        if 'type' in node_data:
            lines.append(f"Type: {node_data['type']}")
        
        if 'pagerank' in node_data:
            lines.append(f"PageRank: {node_data['pagerank']:.4f}")
        
        if 'degree_centrality' in node_data:
            lines.append(f"Degree Centrality: {node_data['degree_centrality']:.4f}")
        
        # Add connection count
        in_degree = self.graph.in_degree(node)
        out_degree = self.graph.out_degree(node)
        lines.append(f"Connections: {in_degree} in, {out_degree} out")
        
        return "<br>".join(lines)
    
    def _enhance_html(self, filepath: str) -> None:
        """Add custom styling and features to the HTML file"""
        with open(filepath, 'r') as f:
            html_content = f.read()
        
        # Add custom CSS and controls
        custom_html = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            #mynetwork {
                border: 2px solid #333;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .controls {
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(255,255,255,0.95);
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                z-index: 1000;
                max-width: 300px;
            }
            .controls h3 {
                margin-top: 0;
                color: #333;
                font-size: 18px;
            }
            .controls input {
                width: 100%;
                padding: 8px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            .controls button {
                padding: 8px 15px;
                margin: 5px 5px 5px 0;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.3s;
            }
            .controls button:hover {
                background: #764ba2;
            }
            .legend {
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(255,255,255,0.95);
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                z-index: 1000;
            }
            .legend h4 {
                margin-top: 0;
                color: #333;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin: 5px 0;
                font-size: 14px;
            }
            .legend-color {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                margin-right: 8px;
                border: 1px solid #333;
            }
            .info {
                position: absolute;
                bottom: 10px;
                left: 10px;
                background: rgba(255,255,255,0.95);
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                z-index: 1000;
                font-size: 14px;
            }
        </style>
        
        <div class="controls">
            <h3>Graph Controls</h3>
            <input type="text" id="searchNode" placeholder="Search for a node...">
            <button onclick="searchAndFocus()">Search</button>
            <button onclick="resetZoom()">Reset View</button>
            <button onclick="togglePhysics()">Toggle Physics</button>
            <button onclick="fitNetwork()">Fit to Screen</button>
        </div>
        
        <div class="legend">
            <h4>Node Types</h4>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                <span>Person</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4ECDC4;"></div>
                <span>Organization</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #45B7D1;"></div>
                <span>Location</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFEAA7;"></div>
                <span>Concept</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #A29BFE;"></div>
                <span>Technology</span>
            </div>
        </div>
        
        <div class="info" id="info">
            <span id="nodeCount">Nodes: 0</span> | 
            <span id="edgeCount">Edges: 0</span> | 
            <span id="selectedInfo">Click on a node for details</span>
        </div>
        
        <script>
            var physicsEnabled = true;
            
            function searchAndFocus() {
                var searchTerm = document.getElementById('searchNode').value.toLowerCase();
                if (searchTerm) {
                    var nodeId = null;
                    network.body.data.nodes.forEach(function(node) {
                        if (node.label.toLowerCase().includes(searchTerm)) {
                            nodeId = node.id;
                        }
                    });
                    
                    if (nodeId) {
                        network.selectNodes([nodeId]);
                        network.focus(nodeId, {
                            scale: 1.5,
                            animation: {
                                duration: 1000,
                                easingFunction: 'easeInOutQuad'
                            }
                        });
                    } else {
                        alert('Node not found!');
                    }
                }
            }
            
            function resetZoom() {
                network.fit({
                    animation: {
                        duration: 1000,
                        easingFunction: 'easeInOutQuad'
                    }
                });
            }
            
            function togglePhysics() {
                physicsEnabled = !physicsEnabled;
                network.setOptions({physics: {enabled: physicsEnabled}});
            }
            
            function fitNetwork() {
                network.fit();
            }
            
            // Update info when network is ready
            network.on("stabilizationIterationsDone", function () {
                document.getElementById('nodeCount').innerText = 'Nodes: ' + network.body.data.nodes.length;
                document.getElementById('edgeCount').innerText = 'Edges: ' + network.body.data.edges.length;
            });
            
            // Show node info on click
            network.on("click", function (params) {
                if (params.nodes.length > 0) {
                    var nodeId = params.nodes[0];
                    var node = network.body.data.nodes.get(nodeId);
                    document.getElementById('selectedInfo').innerText = 'Selected: ' + node.label;
                }
            });
            
            // Enable search on Enter key
            document.getElementById('searchNode').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchAndFocus();
                }
            });
        </script>
        """
        
        # Insert custom HTML before </body>
        html_content = html_content.replace('</body>', custom_html + '</body>')
        
        with open(filepath, 'w') as f:
            f.write(html_content)
    
    def create_subgraph_visualization(
        self, 
        center_nodes: List[str], 
        depth: int = 2,
        output_file: str = 'subgraph.html'
    ) -> str:
        """
        Create visualization of subgraph around specific nodes
        
        Args:
            center_nodes: List of central nodes
            depth: Depth of neighbors to include
            output_file: Output HTML file path
            
        Returns:
            Path to the created HTML file
        """
        # Get all nodes within depth
        nodes_to_include = set(center_nodes)
        
        for _ in range(depth):
            new_nodes = set()
            for node in nodes_to_include:
                if node in self.graph:
                    new_nodes.update(self.graph.predecessors(node))
                    new_nodes.update(self.graph.successors(node))
            nodes_to_include.update(new_nodes)
        
        return self.create_interactive_graph(
            output_file=output_file,
            subset_nodes=list(nodes_to_include),
            physics=True
        )
