"""
Tools package for CRM Agent.
Contains specialized tools that the agent can invoke to take actions.
"""

from app.tools.log_interaction_tool import LogInteractionTool
from app.tools.edit_interaction_tool import EditInteractionTool

__all__ = ["LogInteractionTool", "EditInteractionTool"]
