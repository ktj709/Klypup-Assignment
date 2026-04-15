from dataclasses import dataclass


@dataclass
class DocumentHit:
    title: str
    snippet: str
    source_ref: str


# Baseline stub: swap with FAISS index lookup in next iteration.
def retrieve_documents(query: str) -> list[DocumentHit]:
    return [
        DocumentHit(
            title="Sample Earnings Transcript",
            snippet=f"Matched filing context for query: {query[:120]}",
            source_ref="local://docs/sample-transcript.txt",
        )
    ]
