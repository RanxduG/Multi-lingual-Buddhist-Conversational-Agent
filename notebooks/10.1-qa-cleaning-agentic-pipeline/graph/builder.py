from langgraph.graph import StateGraph, END
from state.qa_state import QAState
from nodes.moderation import moderation_node
from nodes.english_refinement import english_refinement_node
from nodes.sinhala_refinement import sinhala_refinement_node
from nodes.quality_check import quality_check_node
from nodes.sinhala_validation import sinhala_validation_node
from nodes.approve import approve_node
from nodes.reject import reject_node
from graph.router import (
    route_after_moderation,
    route_after_quality_check,
    route_after_validation,
)


def build_graph():
    graph = StateGraph(QAState)

    graph.add_node("moderate", moderation_node)
    graph.add_node("refine_english", english_refinement_node)
    graph.add_node("refine_sinhala", sinhala_refinement_node)
    graph.add_node("quality_check", quality_check_node)
    graph.add_node("validate_sinhala", sinhala_validation_node)
    graph.add_node("approve", approve_node)
    graph.add_node("reject", reject_node)

    graph.set_entry_point("moderate")

    # Moderation → refine or reject
    graph.add_conditional_edges("moderate", route_after_moderation, {
        "refine_english": "refine_english",
        "reject": "reject",
    })

    # English refinement always flows into Sinhala refinement
    graph.add_edge("refine_english", "refine_sinhala")

    # Sinhala refinement always flows into quality check
    graph.add_edge("refine_sinhala", "quality_check")

    # Quality check → validate, retry both refinements, or reject
    graph.add_conditional_edges("quality_check", route_after_quality_check, {
        "validate_sinhala": "validate_sinhala",
        "refine_english": "refine_english",   # Retry — loops back through BOTH refinements
        "reject": "reject",
    })

    # Validation → approve or reject (no retry on validation failure)
    graph.add_conditional_edges("validate_sinhala", route_after_validation, {
        "approve": "approve",
        "reject": "reject",
    })

    graph.add_edge("approve", END)
    graph.add_edge("reject", END)

    return graph.compile()
