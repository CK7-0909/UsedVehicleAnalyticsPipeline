import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer
from .config import SPECS_DIR, CHROMA_PATH, EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("car_specs")


def chunk_text(text: str, size: int = 150, overlap: int = 30) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size - overlap)]


def model_slug_to_name(slug: str) -> str:
    """honda_accord -> Honda Accord -- used for metadata filtering later"""
    return slug.replace("_", " ").title()


def ingest():
    paths = glob.glob(f"{SPECS_DIR}/*.md")
    ids, chunks, metas = [], [], []
    for path in paths:
        slug = os.path.splitext(os.path.basename(path))[0]
        car_model = model_slug_to_name(slug)
        text = open(path).read()
        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{slug}-{i}")
            chunks.append(chunk)
            metas.append({"model": car_model, "model_slug": slug})

    embeddings = model.encode(chunks).tolist()
    collection.upsert(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metas)
    print(f"Ingested {len(chunks)} chunks from {len(paths)} spec docs.")


if __name__ == "__main__":
    ingest()