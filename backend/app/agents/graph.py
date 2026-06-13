"""
JurisFind LangGraph State Machine.

Compiles the complete agent graph and exposes a module-level singleton
(`juris_graph`) for use in the FastAPI route.

Graph topology:
    classifier  ──► general_chat   ──► END
                ──► document_chat  ──► END
                ──► corpus_search  ──► END
                ──► END  (blocked — non-legal question)
"""
import logging

from langgraph.graph import END, StateGraph

from app.agents.nodes.classifier import classifier_node, route_after_classifier
from app.agents.nodes.corpus_search import corpus_search_node
from app.agents.nodes.document_chat import document_chat_node
from app.agents.nodes.general_chat import general_chat_node
from app.agents.state import JurisFindState

logger = logging.getLogger(__name__)


def _blocked_node(state: JurisFindState) -> JurisFindState:
    """
    Synthetic terminal node for non-legal questions.

    Sets the answer to a friendly rejection message so the FastAPI layer
    can stream it like any other response, then routes to END.
    """
    return {
        **state,
        "answer": (
            "I am a specialised legal AI focused on Indian law and the judiciary. "
            "Please ask questions related to law, legal procedures, court systems, "
            "or legal concepts."
        ),
        "citations":        [],
        "retrieved_chunks": [],
    }


def build_graph() -> StateGraph:
    """Compile and return the JurisFind StateGraph."""
    graph = StateGraph(JurisFindState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("classifier",    classifier_node)
    graph.add_node("general_chat",  general_chat_node)
    graph.add_node("document_chat", document_chat_node)
    graph.add_node("corpus_search", corpus_search_node)
    graph.add_node("blocked",       _blocked_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    graph.set_entry_point("classifier")

    # ── Conditional routing after classifier ──────────────────────────────────
    graph.add_conditional_edges(
        "classifier",
        route_after_classifier,
        {
            "general":        "general_chat",
            "document_chat":  "document_chat",
            "corpus_search":  "corpus_search",
            "blocked":        "blocked",
        },
    )

    # ── All terminal nodes lead to END ────────────────────────────────────────
    graph.add_edge("general_chat",  END)
    graph.add_edge("document_chat", END)
    graph.add_edge("corpus_search", END)
    graph.add_edge("blocked",       END)

    compiled = graph.compile()
    logger.info("JurisFind LangGraph compiled successfully.")
    return compiled


# Module-level singleton — built once at import time
juris_graph = build_graph()
