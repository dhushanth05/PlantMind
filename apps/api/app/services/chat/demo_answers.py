from app.domain.chat.schemas import ChatResponse


NO_EVIDENCE_FOLLOW_UPS = [
    "Upload an SOP",
    "Upload a maintenance manual",
    "Upload an incident report",
]


DEMO_ANSWERS: dict[str, ChatResponse] = {
    "which sop should be followed before maintenance": ChatResponse(
        answer="Demo Mode: Follow the approved maintenance SOP for the asset, including Lockout/Tagout, pressure isolation, PPE verification, and supervisor approval before work begins.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["What PPE is required?", "Show maintenance checklist.", "Explain Lockout Tagout."],
    ),
    "what ppe is required": ChatResponse(
        answer="Demo Mode: Required PPE includes safety helmet, eye protection, chemical-resistant gloves, protective footwear, and any task-specific face or respiratory protection listed in the maintenance procedure.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["What are the shutdown steps?", "Explain Lockout Tagout.", "What inspections are required?"],
    ),
    "what are the shutdown steps": ChatResponse(
        answer="Demo Mode: Shutdown steps are: notify operations, stop the equipment, isolate energy sources, depressurize the line, apply Lockout/Tagout, verify zero energy, and obtain supervisor approval.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["Show maintenance checklist.", "What PPE is required?", "How to respond to an oil leak?"],
    ),
    "what is pump p204": ChatResponse(
        answer="Demo Mode: Pump P204 is treated as a maintainable industrial pump asset in PlantMind. Use uploaded maintenance records, SOPs, and incident reports for evidence-grounded details about its service history.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["What are common failure modes?", "Show maintenance checklist.", "What inspections are required?"],
    ),
    "show maintenance checklist": ChatResponse(
        answer="Demo Mode: Maintenance checklist: confirm work permit, verify PPE, isolate and lock out energy, depressurize equipment, inspect seals and bearings, check for leaks, document findings, and obtain supervisor sign-off.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["What PPE is required?", "What are the shutdown steps?", "What inspections are required?"],
    ),
    "explain lockout tagout": ChatResponse(
        answer="Demo Mode: Lockout/Tagout prevents unexpected energization by isolating energy sources, applying locks and tags, verifying zero energy, and controlling release of stored pressure or electrical energy before maintenance.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["Which SOP should be followed before maintenance?", "What are the shutdown steps?", "Show maintenance checklist."],
    ),
    "what are common failure modes": ChatResponse(
        answer="Demo Mode: Common pump failure modes include seal leakage, bearing wear, coupling misalignment, cavitation, blocked suction, overheating, vibration, and lubrication breakdown.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["How to respond to an oil leak?", "What inspections are required?", "Summarize uploaded document."],
    ),
    "how to respond to an oil leak": ChatResponse(
        answer="Demo Mode: Respond to an oil leak by stopping work if unsafe, isolating the source, containing the spill, notifying supervision, using appropriate PPE, cleaning with approved materials, and recording the incident.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["What PPE is required?", "What inspections are required?", "Show maintenance checklist."],
    ),
    "what inspections are required": ChatResponse(
        answer="Demo Mode: Required inspections usually include visual leak checks, seal and gasket inspection, bearing temperature review, vibration check, lubrication condition, coupling alignment, and post-maintenance functional verification.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["Show maintenance checklist.", "What are common failure modes?", "Summarize uploaded document."],
    ),
    "summarize uploaded document": ChatResponse(
        answer="Demo Mode: The uploaded document should be summarized by extracting the asset, maintenance task, hazards, isolation steps, PPE requirements, inspection points, approvals, and any incident or failure-mode evidence.",
        confidence=0.62,
        citations=[],
        related_assets=["P204"],
        follow_up_questions=["Which SOP should be followed before maintenance?", "What PPE is required?", "What inspections are required?"],
    ),
}


def get_demo_answer(question: str) -> ChatResponse | None:
    normalized = question.strip().lower().rstrip("?.!")
    return DEMO_ANSWERS.get(normalized)
