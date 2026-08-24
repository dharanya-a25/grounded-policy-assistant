import re
import os

def parse_manual(filepath):
    """
    Parses the policy manual and returns a dictionary of clauses.
    Keys are clause IDs (e.g., '§1.1.1').
    Values are the full text of the clause, including the preceding header.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    clauses = {}
    current_clause_id = None
    current_clause_text = []
    current_header = ""

    lines = content.split('\n')
    clause_pattern = re.compile(r'^\*\*(\d+\.\d+\.\d+)\*\*\s+(.*)')
    
    for line in lines:
        if line.startswith('## '):
            current_header = line.strip()
            if current_clause_id:
                clauses[current_clause_id] = '\n'.join(current_clause_text).strip()
                current_clause_id = None
                current_clause_text = []
        elif match := clause_pattern.match(line):
            if current_clause_id:
                clauses[current_clause_id] = '\n'.join(current_clause_text).strip()
            
            clause_num = match.group(1)
            current_clause_id = f"§{clause_num}"
            current_clause_text = []
            if current_header:
                current_clause_text.append(current_header)
            current_clause_text.append(line)
        elif current_clause_id:
            current_clause_text.append(line)

    if current_clause_id:
        clauses[current_clause_id] = '\n'.join(current_clause_text).strip()

    return clauses

def parse_amendment(filepath):
    """
    Parses the amendment document into chunks.
    Keys are amendment paragraphs (e.g., 'Amendment-1.1').
    """
    if not os.path.exists(filepath):
        return {}
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    clauses = {}
    current_clause_id = None
    current_clause_text = []
    current_header = ""

    lines = content.split('\n')
    clause_pattern = re.compile(r'^\*\*(\d+\.\d+)\*\*\s+(.*)')
    
    for line in lines:
        if line.startswith('## '):
            current_header = line.strip()
            if current_clause_id:
                clauses[current_clause_id] = '\n'.join(current_clause_text).strip()
                current_clause_id = None
                current_clause_text = []
        elif match := clause_pattern.match(line):
            if current_clause_id:
                clauses[current_clause_id] = '\n'.join(current_clause_text).strip()
            
            clause_num = match.group(1)
            current_clause_id = f"Amendment-{clause_num}"
            current_clause_text = []
            if current_header:
                current_clause_text.append(current_header)
            current_clause_text.append(line)
        elif current_clause_id:
            current_clause_text.append(line)

    if current_clause_id:
        clauses[current_clause_id] = '\n'.join(current_clause_text).strip()

    return clauses

if __name__ == "__main__":
    clauses = parse_manual("policy-manual.md")
    print(f"Parsed {len(clauses)} clauses.")
    amd_clauses = parse_amendment("Amendment No. 2026-01.md")
    print(f"Parsed {len(amd_clauses)} amendment clauses.")
