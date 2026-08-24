# Grounded RAG Assistant (Day 2 Amendment Edition)

This is the solution for **Brite Spark 2026 — Problem 1: The Grounded Answer**, including the Day 2 temporal policy amendment requirements.

## What This Project Does

This system is an interactive Retrieval-Augmented Generation (RAG) assistant designed to accurately answer policy questions strictly based on the provided official documents:
1. `policy-manual.md` (Base Policy)
2. `Amendment No. 2026-01.md` (Amendment)

**Key Features:**
- **Strict Grounding:** The assistant will only provide answers derived from the provided texts. It will not use outside knowledge or "hallucinate".
- **Date-Sensitive Policy Versioning:** The assistant automatically detects the claim date in user questions and applies the correct rules (the base policy before March 1, 2026, and the amended policy on/after March 1, 2026).
- **Exact Citations:** Every answer includes exact clause-level citations (e.g., `§4.3.2` or `Amendment-2.1`).
- **Refusals:** If a question is unsupported by the manual, or if the question's answer depends on a claim date that wasn't provided, it cleanly refuses to answer and suggests the next step.
- **Contradiction Handling:** Flags unresolved contradictions in the policy text.

## Prerequisites
- **Python 3.9+**
- A valid **Google Gemini API Key** (Provides the LLM capabilities for evaluation and date extraction).

## Installation

Create a virtual environment and install dependencies:
```bash
python -m venv .venv
# Activate the venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

## API Key Configuration
This project uses Google Gemini. You must provide an API key.

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and replace `your_gemini_api_key_here` with your actual API key.

*Note: The application will immediately exit with a clear error if the API key is not configured.*

## Running the Application
The entire application runs through a single main entry point. 

Run the interactive CLI:
```bash
python src/main.py
```

### Example Questions
Once the CLI says "Ready.", you can ask:
- **Normal:** "What is the maximum resource limit?"
- **Pre-Amendment:** "What is the earnings disregard for a claim dated February 15, 2026?"
- **Post-Amendment:** "What is the earnings disregard for a claim dated April 10, 2026?"
- **Missing Date Refusal:** "What is the earnings disregard?"
- **Unsupported Refusal:** "Does the program provide dental insurance?"
- **Contradiction:** "How many days do I have to report a change in my income for a claim in January 2026?"

## Running Evaluation Tests
To run the automated 10-question test suite (which validates refusals, contradictions, citations, and date logic):
```bash
python tests/run_evaluation.py
```
*(Note: There is a 4-second delay between test cases to respect Gemini Free Tier rate limits).*
