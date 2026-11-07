from __future__ import annotations

BASELINE_IDEAS: list[dict] = [
    {
        "name": "Meeting Notes Chatbot",
        "one_liner": "An AI chatbot that summarizes meetings.",
        "should_reject_obvious": True,
        "tags": ["chatbot", "meetings"],
    },
    {
        "name": "Generic RAG over PDFs",
        "one_liner": "Upload PDFs and ask questions with embeddings.",
        "should_reject_obvious": True,
        "tags": ["rag", "pdf"],
    },
    {
        "name": "Agent Escrow",
        "one_liner": "Programmable hold-and-release for autonomous AI commerce.",
        "should_reject_obvious": False,
        "tags": ["agents", "payments"],
    },
    {
        "name": "Capability Firewall",
        "one_liner": "Deny-by-default tool permissions for computer-use agents.",
        "should_reject_obvious": False,
        "tags": ["security", "agents"],
    },
    {
        "name": "Yet Another Copilot",
        "one_liner": "AI coding assistant for your IDE.",
        "should_reject_obvious": True,
        "tags": ["copilot", "ide"],
    },
]


def baseline_names() -> list[str]:
    return [str(item["name"]) for item in BASELINE_IDEAS]
