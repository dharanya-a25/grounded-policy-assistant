import re

def extract_citations(text):
    """
    Extracts clause IDs from the SOURCE section (e.g., §4.3.2 and Amendment-2.1)
    """
    if "SOURCE" in text:
        source_text = text.split("SOURCE")[-1]
    else:
        source_text = text
        
    citations = re.findall(r'(?:§|)?(\d+\.\d+(?:\.\d+)?)', source_text)
    amd_citations = re.findall(r'Amendment-\d+\.\d+', source_text)
    
    cleaned = [f"§{num}" for num in citations]
    return cleaned + amd_citations
