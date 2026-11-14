import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"

def cosine_similarity(vector_a:np.ndarray,vector_b:np.ndarray)->float:

    dot_product=np.dot(vector_a,vector_b)
    length_a=np.linalg.norm(vector_a)
    length_b=np.linalg.norm(vector_b)
    return float(dot_product/(length_a * length_b))

model = SentenceTransformer(MODEL_NAME,device="cpu")
texts = [
    "How tall must a guard be?",
    "Height of Guards",
    "Required Smoke Alarms",
]
vectors = model.encode(texts)

print("numbers per vector:", len(vectors[0]))
print("first 5 numbers:", vectors[0][:5])
print("question vs Height of Guards:   ", round(cosine_similarity(vectors[0], vectors[1]), 3))
print("question vs Required Smoke Alarms:", round(cosine_similarity(vectors[0], vectors[2]), 3))