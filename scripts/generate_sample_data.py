"""Generate sample dataset for local testing (1000 synthetic documents)."""
import json
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.ingest import ingest_document
import asyncio


DEPARTMENTS = ["Finance", "HR", "IT", "Legal", "Operations", "Sales", "Marketing"]
SOURCES = ["email", "document_upload", "database_export", "manual_entry"]
SUSPICIOUS_KEYWORDS = [
    "unauthorized", "duplicate", "anomaly", "overpayment", "discount",
    "exception", "waiver", "bypass", "override", "urgent", "expedited"
]


def generate_sample_document(doc_id: int):
    """Generate a single synthetic document."""
    department = random.choice(DEPARTMENTS)
    source = random.choice(SOURCES)
    is_suspicious = random.random() < 0.15  # 15% suspicious
    
    # Build document content
    content_parts = [
        f"Document ID: {doc_id:04d}\n",
        f"Date: {(datetime.utcnow() - timedelta(days=random.randint(0, 365))).date()}\n",
        f"Department: {department}\n",
        f"Amount: ${random.randint(100, 100000)}\n",
        f"Transaction Type: {'Purchase' if random.random() < 0.6 else 'Transfer'}\n",
    ]
    
    if is_suspicious:
        content_parts.append(f"Status: {random.choice(SUSPICIOUS_KEYWORDS)}\n")
    
    # Add random data fields
    content_parts.append(f"Total: {random.randint(1000, 50000)}\n")
    content_parts.append(f"Count: {random.randint(1, 100)}\n")
    content_parts.append(f"Sum: {random.randint(500, 30000)}\n")
    
    content = "".join(content_parts)
    
    return {
        "title": f"Document_{doc_id:04d}_{department}",
        "content": content,
        "metadata": {
            "source": source,
            "department": department,
            "is_suspicious": is_suspicious,
            "doc_number": f"DOC-2024-{doc_id:06d}",
            "tags": ["audit", "2024", department.lower()],
        }
    }


async def generate_and_ingest_batch(start_id: int, batch_size: int):
    """Generate and ingest a batch of documents."""
    tasks = []
    
    for i in range(batch_size):
        doc = generate_sample_document(start_id + i)
        tasks.append(ingest_document(doc))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
    print(f"Batch {start_id}-{start_id + batch_size - 1}: {successful}/{batch_size} successful")
    
    return successful


async def main():
    """Generate 1000 sample documents."""
    total_docs = 1000
    batch_size = 100
    total_successful = 0
    
    print(f"Generating {total_docs} sample documents...")
    print("=" * 60)
    
    for batch_idx in range(0, total_docs, batch_size):
        successful = await generate_and_ingest_batch(batch_idx, batch_size)
        total_successful += successful
    
    print("=" * 60)
    print(f"Total: {total_successful}/{total_docs} documents successfully ingested")
    
    # Save sample to file for reference
    sample_doc = generate_sample_document(0)
    with open('sample_document.json', 'w') as f:
        json.dump(sample_doc, f, indent=2)
    print("\nSample document saved to sample_document.json")


if __name__ == "__main__":
    asyncio.run(main())
