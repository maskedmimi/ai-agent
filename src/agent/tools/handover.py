"""
src/agent/tools/handover.py

Simulated escalation to a human advisor. No real integration (no phone
system, no ticketing) — this is a demo stub standing in for what a platform
like Cognigy calls a "handover" node: it logs the reason and returns a
pre-formatted confirmation the agent can read back to the customer.
"""

import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def transfer_to_human(raison: str) -> str:
    """
    Transfer the conversation to a human advisor. Use this when the
    customer explicitly asks to speak to a person, or when they are stuck
    and the available tools (appointment booking, FAQ) can't resolve their
    request.

    Args:
        raison (str): A short description of why the handover is needed
            (e.g. "le client demande un conseiller", "question hors FAQ").

    Returns:
        str: A pre-formatted confirmation sentence to read back to the
        customer.
    """
    logger.info("Handover to human advisor requested: %s", raison)
    return (
        "Je vous transfère à un conseiller qui va pouvoir vous aider. "
        "Merci de rester en ligne."
    )


TOOLS = [transfer_to_human]
