import json
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

# ==============================
# CONFIG — EDIT THESE
# ==============================
QDRANT_URL = "https://a21f5be5-d41b-4c39-98e2-5daf7f6148ad.us-west-2-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.zC9KNvcPMOaGhLPy4xmoBlfuDnEMIba6KQgjwfxbdnM"
COLLECTION_NAME = "nu_itcs_rag"

DATASET_PATH = r"D:\courses\Senior sems1\Grad 1\ai-professor-deployed\nu_itcs_rag_dataset_156.jsonl"

BATCH_SIZE = 16          # smaller = safer
TIMEOUT_SECONDS = 300    # much safer for cloud
MAX_RETRIES = 5

# 1) Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2) Load dataset
items = []
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    for line in f:
        items.append(json.loads(line))
print("Loaded", len(items), "entries")

# 3) Embed
texts = [f"Question: {it['question']}\nAnswer: {it['answer']}" for it in items]
vectors = model.encode(texts, show_progress_bar=True)

# 4) Connect with bigger timeout
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=TIMEOUT_SECONDS)

# 5) Create collection (no deprecated recreate_collection)
VECTOR_SIZE = vectors.shape[1]
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=qm.VectorParams(size=VECTOR_SIZE, distance=qm.Distance.COSINE),
)

def upsert_with_retry(points, batch_num):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
            print(f"✅ Batch {batch_num} uploaded ({len(points)} points)")
            return
        except Exception as e:
            print(f"⚠️ Batch {batch_num} attempt {attempt} failed: {type(e).__name__}: {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(2 * attempt)

# 6) Batch upsert
total = len(items)
batch_num = 0

for start in range(0, total, BATCH_SIZE):
    batch_num += 1
    end = min(start + BATCH_SIZE, total)

    points = []
    for it, vec in zip(items[start:end], vectors[start:end]):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, it["id"]))

        payload = {
            "id_str": it["id"],
            "category": it.get("category"),
            "question": it.get("question"),
            "answer": it.get("answer"),
            "tags": it.get("tags", []),
            "source": it.get("source"),
            "text": f"Question: {it['question']}\nAnswer: {it['answer']}",
        }

        points.append(qm.PointStruct(id=point_id, vector=vec.tolist(), payload=payload))

    upsert_with_retry(points, batch_num)

print(f"🎉 Done! Uploaded {total} points to '{COLLECTION_NAME}'")