import openai
import numpy as np

def get_embedding(text: str, model="text-embedding-ada-002") -> np.ndarray:
    """
    Return a 1536-dim embedding as a numpy array.
    """
    if not text.strip():
        return np.zeros(1536, dtype=np.float32)
    response = openai.Embedding.create(model=model, input=[text])
    emb = response["data"][0]["embedding"]
    return np.array(emb, dtype=np.float32)
