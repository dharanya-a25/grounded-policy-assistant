# Design Decisions

## Retrieval Design
- **Semantic Search**: We use the `sentence-transformers` library (`all-MiniLM-L6-v2`) because it's highly performant, operates entirely locally for the embedding step, and is excellent at matching paraphrase queries to dense text clauses.
- **Clause-level Chunking**: The policy manual is parsed at the exact clause level (e.g., `§2.4.1`) using regular expressions, maintaining the structural integrity required for precise citations.

## Refusal Threshold & Grounding
- The LLM is prompted strictly to evaluate whether the retrieved context contains *sufficient* information to answer the question. If it does not, it is instructed to return a strict `REFUSAL`. This mitigates hallucination and prevents the AI from substituting general knowledge.

## Contradiction Handling
- If two retrieved clauses provide conflicting information (such as different time limits for reporting), the system is prompted to catch this and return a `CONFLICT DETECTED` response, citing both clauses. This ensures the system does not silently resolve ambiguities that should be handled by a supervisor.

## Trade-offs
- **LLM as Evaluator vs Hardcoded Rules**: We rely on a powerful LLM (`gemini-2.5-flash`) for both evidence evaluation and answer generation. The trade-off is relying on an external API, but this drastically improves the system's ability to handle paraphrasing, edge cases, and complex reasoning compared to hardcoded keyword rules, adhering to the project's requirement of not hardcoding answers.

# Day 2 Amendment — Amendment No. 2026-01

1. **What changed:** The system now extracts a claim date from user queries, determines if the claim falls under the pre-amendment or post-amendment period, and injects the corresponding rules/amendments into the LLM context.
2. **How the amendment is loaded:** It is parsed at runtime by `src/parser.py` (similarly to the base manual, chunked into `Amendment-X.Y` clauses) and indexed by `src/retriever.py` dynamically if applicable.
3. **How the effective date is handled:** Defined in `src/policy_version.py`. Dates before `2026-03-01` trigger `PRE_AMENDMENT`, meaning amendment clauses are stripped from retrieval. Dates on or after trigger `POST_AMENDMENT`.
4. **How claim dates are extracted:** Natural language date extraction is performed using a lightweight LLM call (`src/date_parser.py`) which translates phrases like "February 2026" into a normalized `YYYY-MM-DD` string.
5. **How the system chooses the applicable policy version:** `src/policy_version.py` converts the extracted date and compares it against the hardcoded March 1, 2026 effective date.
6. **What happens when no claim date is provided:** The system determines the version as `UNKNOWN`. It retrieves both base and amendment clauses and asks the evaluator LLM if the answer *would* differ depending on the date. If yes, it triggers a `REFUSAL` and asks the user for a date. If no, it answers normally.
7. **How conflicts between original and amended provisions are handled:** For `POST_AMENDMENT` claims, the prompt explicitly instructs the LLM that the amendment *overrides* the base rules and resolves the reporting contradiction (14 days everywhere). For `PRE_AMENDMENT` claims, the original contradiction (§4.3.2 vs §9.1.4) is maintained and still flagged as a conflict.
8. **What existing functionality was preserved:** All original core systems (semantic retrieval, strict LLM evaluations, exact citations, and contradiction tracking) are untouched, just enhanced with temporal context.
9. **What code/design was intentionally NOT changed:** We did not modify any of the three original `.md` files. We did not switch away from `sentence-transformers` to a different RAG provider, as it remains highly efficient.
10. **What you would have done differently if you had known about this requirement on Day 1:** If this was known on Day 1, I would have structured the base parser to emit a timestamp/validity range for every clause object inherently (e.g., `{ text: "...", valid_from: "2000-01-01", valid_to: "2026-02-28" }`), allowing the retriever to natively filter out invalid clauses before they even reach the LLM, rather than relying on prompt-engineering to teach the LLM about overrides.
