import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.retriever import Retriever
from src.evaluator import build_evaluation_prompt
from src.answerer import Answerer
from src.citations import extract_citations
from src.date_parser import DateParser
from src.policy_version import determine_policy_version
import time

def run_evaluation():
    try:
        retriever = Retriever("policy-manual.md", "Amendment No. 2026-01.md")
        answerer = Answerer()
        date_parser = DateParser()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return

    with open("tests/evaluation.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    passed = 0
    
    print("Starting evaluation...")
    for t in tests:
        print(f"\n--- Test {t['id']}: {t['question']}")
        
        claim_date = date_parser.extract_claim_date(t['question'])
        policy_version = determine_policy_version(claim_date)
        
        include_amd = policy_version.name in ["POST_AMENDMENT", "UNKNOWN"]
        top_clauses = retriever.retrieve(t['question'], top_k=7, include_amendment=include_amd)
        
        prompt = build_evaluation_prompt(t['question'], top_clauses, claim_date, policy_version)
        response = answerer.generate_response(prompt, top_clauses)
        
        # Analyze response
        if "CONFLICT DETECTED" in response:
            actual_type = "CONFLICT"
        elif "REFUSAL" in response:
            actual_type = "REFUSAL"
        elif "ANSWER" in response:
            actual_type = "ANSWER"
        else:
            actual_type = "UNKNOWN"
            
        citations = extract_citations(response)
        
        # Check pass/fail
        type_match = actual_type == t['expected_type']
        
        # Check citations if needed
        # For ANSWER and CONFLICT, expected citations should be present
        citation_match = True
        if actual_type in ["ANSWER", "CONFLICT"]:
            for expected_citation in t['expected_citations']:
                if expected_citation not in citations:
                    citation_match = False
                    
        is_pass = type_match and citation_match
        if is_pass:
            passed += 1
            print("Status: PASS")
        else:
            print(f"Status: FAIL (Expected: {t['expected_type']}, Got: {actual_type})")
            print("Expected citations:", t['expected_citations'], ", Got:", citations)
        
        # Free Tier Rate Limit Handling
        time.sleep(4)

    print(f"\nEvaluation Complete: {passed}/{len(tests)} passed.")

if __name__ == "__main__":
    run_evaluation()
