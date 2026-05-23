from mcp.server.fastmcp import FastMCP
from src.configs.db import get_all_notes, create_note, delete_note

# Initialize FastMCP. We name it 'mpc' to match the structured file name.
mpc = FastMCP("Notes Server")

@mpc.tool()
async def get_my_notes() -> str:
    """Retrieve all stored notes from the persistent SQLite database."""
    notes = await get_all_notes()
    if not notes:
        return "You have no notes stored."
    
    formatted_notes = []
    for idx, n in enumerate(notes, 1):
        formatted_notes.append(f"[{idx}] (ID: {n['id']}) at {n['created_at']}:\n{n['content']}\n")
    return "\n".join(formatted_notes)

@mpc.tool()
async def add_note(content: str) -> str:
    """Save a new note with the specified text content into the database."""
    note = await create_note(content)
    return f"Successfully added note (ID: {note['id']}): '{content}'"

@mpc.tool()
async def add_notes(content: str) -> str:
    """Save a new note with the specified text content into the database (Alias for add_note)."""
    return await add_note(content)

@mpc.tool()
async def delete_note_tool(id: int) -> str:
    """Delete a note by its ID from the persistent SQLite database."""
    deleted = await delete_note(id)
    if deleted:
        return f"Successfully deleted note with ID: {id}."
    return f"Note with ID: {id} was not found in the database."

@mpc.tool()
async def remove_note(id: int) -> str:
    """Delete a note by its ID from the persistent SQLite database (Alias for delete_note)."""
    return await delete_note_tool(id)