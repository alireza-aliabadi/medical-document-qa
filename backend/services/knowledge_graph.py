"""Medical knowledge graph extraction (rule-based stub)."""

import re
from dataclasses import dataclass, field


@dataclass
class KnowledgeNode:
    id: str
    label: str
    entity_type: str


@dataclass
class KnowledgeEdge:
    source: str
    target: str
    relation: str


@dataclass
class KnowledgeGraph:
    nodes: list[KnowledgeNode] = field(default_factory=list)
    edges: list[KnowledgeEdge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nodes": [n.__dict__ for n in self.nodes],
            "edges": [e.__dict__ for e in self.edges],
        }


class KnowledgeGraphService:
    DISEASE_PATTERN = re.compile(
        r"\b(diabetes|hypertension|asthma|cancer|pneumonia|stroke|covid-19)\b",
        re.IGNORECASE,
    )
    DRUG_PATTERN = re.compile(
        r"\b(aspirin|metformin|insulin|ibuprofen|amoxicillin|lisinopril)\b",
        re.IGNORECASE,
    )
    TREATMENT_PATTERN = re.compile(
        r"\b(chemotherapy|radiation|surgery|physical therapy|vaccination)\b",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> KnowledgeGraph:
        graph = KnowledgeGraph()
        node_index: dict[str, KnowledgeNode] = {}

        def add_node(label: str, entity_type: str) -> KnowledgeNode:
            key = f"{entity_type}:{label.lower()}"
            if key not in node_index:
                node = KnowledgeNode(id=key, label=label, entity_type=entity_type)
                node_index[key] = node
                graph.nodes.append(node)
            return node_index[key]

        diseases = [m.group(0) for m in self.DISEASE_PATTERN.finditer(text)]
        drugs = [m.group(0) for m in self.DRUG_PATTERN.finditer(text)]
        treatments = [m.group(0) for m in self.TREATMENT_PATTERN.finditer(text)]

        for disease in diseases:
            d_node = add_node(disease, "disease")
            for drug in drugs:
                drug_node = add_node(drug, "drug")
                graph.edges.append(
                    KnowledgeEdge(source=drug_node.id, target=d_node.id, relation="treats")
                )
            for treatment in treatments:
                tx_node = add_node(treatment, "treatment")
                graph.edges.append(
                    KnowledgeEdge(source=tx_node.id, target=d_node.id, relation="used_for")
                )

        return graph
