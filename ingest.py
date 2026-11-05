import json, uuid
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

ROOT = Path(__file__).resolve().parent
docs = json.loads((ROOT/"data"/"documents.json").read_text(encoding="utf-8"))
storage = ROOT/"storage"
storage.mkdir(exist_ok=True)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = QdrantClient(path=str(storage/"qdrant"))
collection = "permission_chunks"
size = model.get_sentence_embedding_dimension()
if client.collection_exists(collection):
    client.delete_collection(collection)
client.create_collection(collection_name=collection,
    vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE))
for field in ["tenant_id","allowed_roles","allowed_users","doc_id"]:
    client.create_payload_index(collection_name=collection, field_name=field,
                                field_schema=models.PayloadSchemaType.KEYWORD)

def chunks(text, size=110, overlap=20):
    words=text.split()
    out=[]
    start=0
    while start<len(words):
        end=min(start+size,len(words))
        out.append(" ".join(words[start:end]))
        if end==len(words): break
        start=end-overlap
    return out

points=[]
for doc in docs:
    if not doc.get("tenant_id"):
        raise ValueError(f"Document {doc.get('doc_id')} has no tenant_id; refusing ingestion")
    for i, chunk in enumerate(chunks(doc["text"])):
        vector=model.encode(chunk, normalize_embeddings=True).tolist()
        payload={k:doc[k] for k in ["doc_id","tenant_id","title","classification","allowed_roles","allowed_users"]}
        payload.update({"text":chunk,"chunk_index":i})
        points.append(models.PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))
client.upsert(collection_name=collection, points=points)
print(f"Ingested {len(points)} chunks from {len(docs)} documents into {collection}.")
