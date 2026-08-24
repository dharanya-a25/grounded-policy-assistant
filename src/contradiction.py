def format_contradiction(clause_1, clause_2):
    return f"""CONFLICT DETECTED
CLAUSE 1: {clause_1}
CLAUSE 2: {clause_2}
NEXT STEP:
Refer the question to a supervisor or appropriate program administrator."""
