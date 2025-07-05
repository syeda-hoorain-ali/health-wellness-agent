from agents import RunContextWrapper, function_tool
from typing import Dict, Any, Optional

from src.context import InjuryNote, UserSessionContext


@function_tool(strict_mode=False)
async def add_injury_note(
    ctx: RunContextWrapper[UserSessionContext],
    injury_description: str,
    severity_level: str,
    affected_body_parts: list[str],
    restrictions: list[str],
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add injury information to the user's session context.
    
    This tool stores injury details that will be used to adapt workout recommendations
    and provide safe exercise alternatives.
    
    Args:
        injury_description: Detailed description of the injury or limitation
        severity_level: Level of severity (mild, moderate, severe)
        affected_body_parts: List of body parts affected by the injury
        restrictions: List of movements or exercises to avoid
        notes: Additional notes or context about the injury
    
    Returns:
        Dict containing the stored injury information and confirmation message
    """
    
    injury_note = InjuryNote(
        injury_description=injury_description,
        severity_level=severity_level,
        affected_body_parts=affected_body_parts,
        restrictions=restrictions,
        notes=notes
    )
    
    # Store in context
    ctx.context.injury_notes.append(injury_note)
    
    return {
        "injury_note": injury_note.model_dump(),
        "message": f"Injury information recorded: {injury_description} (Severity: {severity_level})",
        "affected_parts": affected_body_parts,
        "restrictions": restrictions
    }
