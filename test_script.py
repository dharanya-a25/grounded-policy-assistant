from src.retriever import Retriever
from src.evaluator import build_evaluation_prompt
from src.answerer import Answerer
from src.date_parser import DateParser
from src.policy_version import determine_policy_version

def run_tests():
    print("=== INITIALIZING TESTS ===")
    retriever = Retriever("policy-manual.md", "Amendment No. 2026-01.md")
    answerer = Answerer()
    date_parser = DateParser()
    
    questions = [
        "What is the maximum resource limit?",
        "Who is eligible for the program?",
        "How many days do I have to report a change?",
        "What documents are required for an application?",
        "Does the program provide dental insurance?",
        "Can I receive benefits for a service that is not mentioned in the manual?",
        "What is the resource limit for a claim dated February 15, 2026?",
        "What is the resource limit for a claim dated April 15, 2026?",
        "How many days do I have to report a change in my income for a claim in January 2026?",
        "Can I get a free car?"
    ]
    
    for i, q in enumerate(questions):
        print(f"\n{'='*50}\nTEST {i+1}\nQuestion: {q}\n{'-'*50}")
        
        claim_date = date_parser.extract_claim_date(q)
        policy_version = determine_policy_version(claim_date)
        
        print(f"Detected Claim Date: {claim_date}")
        print(f"Selected Policy Version: {policy_version.name}")
        
        include_amd = policy_version.name in ["POST_AMENDMENT", "UNKNOWN"]
        top_clauses = retriever.retrieve(q, top_k=7, include_amendment=include_amd)
        
        prompt = build_evaluation_prompt(q, top_clauses, claim_date, policy_version)
        response = answerer.generate_response(prompt, top_clauses)
        
        print("\nSystem Output:")
        print(response)

if __name__ == "__main__":
    run_tests()
