from src.retriever import Retriever
from src.evaluator import build_evaluation_prompt
from src.answerer import Answerer
from src.date_parser import DateParser
from src.policy_version import determine_policy_version
import json

def run_demo():
    print("=== INITIALIZING DEMO ===")
    retriever = Retriever("policy-manual.md", "Amendment No. 2026-01.md")
    answerer = Answerer()
    date_parser = DateParser()
    
    demos = [
        {
            "name": "DEMO 1: A normal question with a pre-amendment claim date",
            "question": "What is the earnings disregard for a claim dated February 15, 2026?"
        },
        {
            "name": "DEMO 2: The same/similar question with a post-amendment claim date",
            "question": "What is the earnings disregard for a claim dated April 10, 2026?"
        },
        {
            "name": "DEMO 3: A question without a claim date where date matters",
            "question": "What is the earnings disregard?"
        },
        {
            "name": "DEMO 4: An unsupported question",
            "question": "Does the program provide additional funds for purchasing pet food?"
        },
        {
            "name": "DEMO 5: A contradiction/conflict question",
            "question": "How many days do I have to report a change in my income for a claim in January 2026?"
        }
    ]
    
    for demo in demos:
        print(f"\n{'='*50}\n{demo['name']}\nQuestion: {demo['question']}\n{'-'*50}")
        
        claim_date = date_parser.extract_claim_date(demo['question'])
        policy_version = determine_policy_version(claim_date)
        
        print(f"Detected Claim Date: {claim_date}")
        print(f"Selected Policy Version: {policy_version.name}")
        
        include_amd = policy_version.name in ["POST_AMENDMENT", "UNKNOWN"]
        top_clauses = retriever.retrieve(demo['question'], top_k=5, include_amendment=include_amd)
        
        print("\nRetrieved Clauses:")
        for c in top_clauses:
            print(f"- {c['id']}")
            
        prompt = build_evaluation_prompt(demo['question'], top_clauses, claim_date, policy_version)
        response = answerer.generate_response(prompt, top_clauses)
        
        print("\nSystem Output:")
        print(response)
        import time
        time.sleep(4)

if __name__ == "__main__":
    run_demo()
