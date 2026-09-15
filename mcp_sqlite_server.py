import sys
import os
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LabInventoryServer")
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "lab_inventory.db"))


@mcp.tool()
def search_inventory(compound: str) -> str:
    """Searches the laboratory inventory database for a specific chemical compound.

    Args:
        compound: Name of the chemical compound (e.g., 'salicylic acid').

    Returns:
        Details about stock level, location, purity, and GHS hazard statements.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT compound_name, formula, cas_number, quantity_g, purity, location, hazard_ghs 
            FROM inventory 
            WHERE LOWER(compound_name) = LOWER(?)
        """, (compound.strip(),))
        row = cursor.fetchone()
        conn.close()

        if row:
            name, formula, cas, qty, purity, loc, hazard = row
            return (
                f"--- LAB INVENTORY STATUS ---\n"
                f"Compound: {name}\n"
                f"Formula: {formula}\n"
                f"CAS Number: {cas}\n"
                f"Current Stock: {qty} grams\n"
                f"Purity: {purity}\n"
                f"Storage Location: {loc}\n"
                f"GHS Hazard Warnings: {hazard}\n"
            )
        else:
            return f"Compound '{compound}' was not found in the laboratory inventory."
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return f"Database error: {e}"


@mcp.tool()
def get_synthesis_procedure(target_compound: str) -> str:
    """Retrieves standard operating synthesis procedures and precautions for a target chemical.

    Args:
        target_compound: Name of the chemical compound to synthesize (e.g., 'aspirin').

    Returns:
        Details about raw reagents, reaction steps, and experimental precautions.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT target_compound, reagents_required, procedure_steps, safety_precautions 
            FROM synthesis_procedures 
            WHERE LOWER(target_compound) = LOWER(?)
        """, (target_compound.strip(),))
        row = cursor.fetchone()
        conn.close()

        if row:
            target, reagents, steps, safety = row
            return (
                f"--- SYNTHESIS PROCEDURE FOR {target.upper()} ---\n"
                f"Required Reagents: {reagents}\n"
                f"Procedure Steps: {steps}\n"
                f"Safety Precautions: {safety}\n"
            )
        else:
            return f"Synthesis procedure for '{target_compound}' not found in database."
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return f"Database error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
