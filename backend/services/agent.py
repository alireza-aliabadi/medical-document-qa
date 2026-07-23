"""Medical AI agent with tool calling."""

import ast
import logging
import operator
from dataclasses import dataclass

from backend.services.rag import RAGService
from backend.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


@dataclass
class ToolResult:
    name: str
    output: str


class MedicalAgentService:
    """Agent orchestrating search, calculator, and drug lookup tools."""

    def __init__(self, rag: RAGService) -> None:
        self.rag = rag
        self.vector_store = VectorStoreService()

    async def run(self, query: str, tools: list[str] | None = None) -> tuple[str, list[dict]]:
        enabled = set(tools or ["search", "calculator"])
        tool_results: list[ToolResult] = []

        if "search" in enabled:
            results = await self.rag.retrieve(query)
            summary = "\n".join(r.content[:200] for r in results[:3]) or "No results."
            tool_results.append(ToolResult(name="search", output=summary))

        if "calculator" in enabled and any(c.isdigit() for c in query):
            expr = self._extract_expression(query)
            if expr:
                try:
                    value = self._safe_eval(expr)
                    tool_results.append(ToolResult(name="calculator", output=str(value)))
                except Exception as exc:
                    tool_results.append(ToolResult(name="calculator", output=f"Error: {exc}"))

        if "drug_lookup" in enabled:
            drug = self._extract_drug_name(query)
            tool_results.append(
                ToolResult(
                    name="drug_lookup",
                    output=(
                        f"Drug info stub for '{drug}': consult formulary for dosing/interactions."
                    ),
                )
            )

        tool_calls = [{"tool": t.name, "result": t.output} for t in tool_results]
        context = "\n".join(f"{t.name}: {t.output}" for t in tool_results)
        prompt = f"Using tool outputs:\n{context}\n\nAnswer the question: {query}"
        answer = await self.rag.generate_answer(prompt)
        return answer, tool_calls

    @staticmethod
    def _extract_expression(query: str) -> str | None:
        for token in query.replace("=", " ").split():
            if any(op in token for op in ("+", "-", "*", "/")) and any(c.isdigit() for c in token):
                return token.strip("?.")
        return None

    @staticmethod
    def _safe_eval(expression: str) -> float:
        node = ast.parse(expression, mode="eval").body

        def _eval(n: ast.AST) -> float:
            if isinstance(n, ast.Constant) and isinstance(n.value, int | float):
                return float(n.value)
            if isinstance(n, ast.BinOp) and type(n.op) in SAFE_OPERATORS:
                return float(SAFE_OPERATORS[type(n.op)](_eval(n.left), _eval(n.right)))
            if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
                return -_eval(n.operand)
            raise ValueError("Unsupported expression")

        return _eval(node)

    @staticmethod
    def _extract_drug_name(query: str) -> str:
        keywords = ("drug", "medication", "dose", "prescription")
        for keyword in keywords:
            if keyword in query.lower():
                return query.split(keyword)[-1].strip(" ?.:,")[:64] or "unknown"
        return "unknown"
