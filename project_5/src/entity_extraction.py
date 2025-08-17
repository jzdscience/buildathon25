"""
Entity and Relationship Extraction Module
Uses NLP to extract entities, concepts, and relationships from text
"""

import spacy
from typing import List, Dict, Any, Tuple, Set
import re
from collections import defaultdict
from tqdm import tqdm


class EntityExtractor:
    """Extracts entities and relationships from text using NLP"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize with spaCy model"""
        try:
            self.nlp = spacy.load(model_name)
        except:
            print(f"Model {model_name} not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
            
        # Add custom entity patterns
        self._add_custom_patterns()
        
    def _add_custom_patterns(self):
        """Add custom patterns for better entity recognition"""
        # Add ruler for pattern-based matching
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        patterns = [
            # Technical terms
            {"label": "TECH", "pattern": [{"LOWER": {"IN": ["api", "database", "algorithm", "framework", "library"]}}]},
            # Concepts
            {"label": "CONCEPT", "pattern": [{"POS": "NOUN", "DEP": {"IN": ["nsubj", "dobj"]}}]},
        ]
        
        ruler.add_patterns(patterns)
    
    def extract_entities_and_relations(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract entities and relationships from documents
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Dictionary containing entities and relationships
        """
        all_entities = defaultdict(set)
        all_relationships = []
        entity_contexts = defaultdict(list)
        
        for doc_data in tqdm(documents, desc="Extracting entities"):
            doc = self.nlp(doc_data['content'][:1000000])  # Limit text length for processing
            
            # Extract named entities
            entities = self._extract_entities(doc)
            for entity_type, entity_list in entities.items():
                all_entities[entity_type].update(entity_list)
                
                # Store context for each entity
                for entity in entity_list:
                    entity_contexts[entity].append({
                        'source': doc_data['title'],
                        'type': entity_type
                    })
            
            # Extract relationships
            relationships = self._extract_relationships(doc)
            all_relationships.extend(relationships)
            
            # Extract key concepts
            concepts = self._extract_concepts(doc)
            all_entities['CONCEPT'].update(concepts)
        
        # Convert sets to lists for JSON serialization
        entities_dict = {k: list(v) for k, v in all_entities.items()}
        
        # Deduplicate and clean relationships
        unique_relationships = self._deduplicate_relationships(all_relationships)
        
        return {
            'entities': entities_dict,
            'relationships': unique_relationships,
            'entity_contexts': dict(entity_contexts),
            'statistics': {
                'total_entities': sum(len(v) for v in entities_dict.values()),
                'total_relationships': len(unique_relationships),
                'entity_types': list(entities_dict.keys())
            }
        }
    
    def _extract_entities(self, doc) -> Dict[str, Set[str]]:
        """Extract named entities from spaCy doc"""
        entities = defaultdict(set)
        
        for ent in doc.ents:
            # Clean and normalize entity text
            entity_text = self._normalize_text(ent.text)
            if len(entity_text) > 2:  # Filter out very short entities
                entities[ent.label_].add(entity_text)
        
        # Also extract noun chunks as potential concepts
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Limit to reasonable length
                entities['NOUN_PHRASE'].add(self._normalize_text(chunk.text))
        
        return entities
    
    def _extract_relationships(self, doc) -> List[Dict[str, str]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Extract subject-verb-object relationships
        for token in doc:
            if token.pos_ == "VERB":
                subject = None
                obj = None
                
                for child in token.children:
                    if child.dep_ == "nsubj":
                        subject = self._get_entity_span(child)
                    elif child.dep_ in ["dobj", "pobj"]:
                        obj = self._get_entity_span(child)
                
                if subject and obj:
                    relationships.append({
                        'source': self._normalize_text(subject),
                        'relation': token.lemma_,
                        'target': self._normalize_text(obj),
                        'context': token.sent.text[:200]
                    })
        
        # Extract relationships from dependency patterns
        for ent1 in doc.ents:
            for ent2 in doc.ents:
                if ent1 != ent2 and ent1.start < ent2.start:
                    # Check if entities are in the same sentence
                    if ent1.sent == ent2.sent:
                        # Extract the text between entities as potential relation
                        between_text = doc.text[ent1.end_char:ent2.start_char].strip()
                        if len(between_text.split()) <= 5:  # Short connecting phrase
                            relationships.append({
                                'source': self._normalize_text(ent1.text),
                                'relation': 'related_to',
                                'target': self._normalize_text(ent2.text),
                                'context': ent1.sent.text[:200]
                            })
        
        return relationships
    
    def _extract_concepts(self, doc) -> Set[str]:
        """Extract key concepts from the document"""
        concepts = set()
        
        # Extract important noun phrases
        for chunk in doc.noun_chunks:
            # Filter based on dependency and POS tags
            if chunk.root.dep_ in ['nsubj', 'dobj', 'pobj'] and len(chunk.text.split()) <= 3:
                concepts.add(self._normalize_text(chunk.text))
        
        # Extract terms with high frequency (simplified TF approach)
        word_freq = defaultdict(int)
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                word_freq[token.lemma_] += 1
        
        # Add high-frequency terms as concepts
        for word, freq in word_freq.items():
            if freq >= 3 and len(word) > 3:
                concepts.add(word)
        
        return concepts
    
    def _get_entity_span(self, token) -> str:
        """Get the full entity span for a token"""
        # Check if token is part of a named entity
        for ent in token.doc.ents:
            if token.i >= ent.start and token.i < ent.end:
                return ent.text
        
        # Otherwise, get the subtree
        return ' '.join([t.text for t in token.subtree])
    
    def _normalize_text(self, text: str) -> str:
        """Normalize entity text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters at the beginning/end
        text = text.strip('.,;:!?"\'')
        # Capitalize properly
        if text and not text[0].isupper():
            text = text.capitalize()
        return text
    
    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships"""
        seen = set()
        unique = []
        
        for rel in relationships:
            key = (rel['source'], rel['relation'], rel['target'])
            if key not in seen:
                seen.add(key)
                unique.append(rel)
        
        return unique
