"""Tests for knowledge graph extraction."""

from backend.services.knowledge_graph import KnowledgeGraphService


def test_extract_entities_and_relations():
    text = "Metformin treats diabetes. Chemotherapy is used for cancer."
    graph = KnowledgeGraphService().extract(text)
    assert len(graph.nodes) >= 2
    assert any(n.entity_type == "disease" for n in graph.nodes)
    assert len(graph.edges) >= 1
