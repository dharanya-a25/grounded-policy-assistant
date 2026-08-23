import sys
import os
sys.path.append(os.path.abspath('.'))
from src.retriever import Retriever

r = Retriever("policy-manual.md", "Amendment No. 2026-01.md")
res = r.retrieve("Can I receive benefits for a service that is not mentioned in the manual?")
for c in res:
    print(f"{c['id']}: {c['score']}")
