import sys
import os
import warnings
import logging
from dotenv import load_dotenv

# Completely silence STDERR to prevent ANY warnings, stack traces, or debug logs
# as requested by the user: "Do NOT show: stack traces, debug logs, warnings"
sys.stderr = open(os.devnull, 'w')

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("google.genai").setLevel(logging.ERROR)
logging.getLogger("google-generativeai").setLevel(logging.ERROR)

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.retriever import Retriever
from src.evaluator import build_evaluation_prompt
from src.answerer import Answerer
from src.date_parser import DateParser
from src.policy_version import determine_policy_version

def main():
    print("Initializing Grounded RAG Assistant...")
    
    # Check for API Key
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("\nERROR:")
        print("GEMINI_API_KEY is not configured.")
        print("Please create a .env file or set the required environment variable.")
        sys.exit(1)
        
    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        policy_path = os.path.join(root_dir, "policy-manual.md")
        amd_path = os.path.join(root_dir, "Amendment No. 2026-01.md")
        
        print("Loading policy manual...")
        print("Loading amendment...")
        print("Initializing retrieval...")
        retriever = Retriever(policy_path, amd_path)
        print("Initializing AI model...")
        answerer = Answerer()
        date_parser = DateParser()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        sys.exit(1)
        
    print("Ready. Type your question or 'exit' to quit.\n")
    
    question_count = 0
    while True:
        try:
            question = input("> ")
            if question.strip().lower() in ['exit', 'quit']:
                break
            if not question.strip():
                continue
                
            claim_date = date_parser.extract_claim_date(question)
            policy_version = determine_policy_version(claim_date)
                
            include_amd = policy_version.name in ["POST_AMENDMENT", "UNKNOWN"]
            top_clauses = retriever.retrieve(question, top_k=7, include_amendment=include_amd)
            
            prompt = build_evaluation_prompt(question, top_clauses, claim_date, policy_version)
            response = answerer.generate_response(prompt, top_clauses)
            
            print("\n" + response + "\n")
            
            question_count += 1
            if question_count >= 10:
                print("Maximum number of questions reached.\nExiting...")
                break 

            
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    main()
