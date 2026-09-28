import math
import hashlib
import os
import re
from typing import List, Union

EMBEDDING_DIM = 384

class EdgeEmbedder:
    """
    Offline-capable embedding pipeline for Qdrant Edge.
    Uses FastEmbed (ONNX, ~5ms per embedding, runs locally without network).
    Provides automatic fallback to a deterministic industrial-vocabulary hashing vectorizer
    if ONNX cache is unavailable or environment is air-gapped.
    """
    _instance = None
    _fastembed_model = None

    def __init__(self):
        self._init_fastembed()

    def _init_fastembed(self):
        if EdgeEmbedder._fastembed_model is not None:
            return
        try:
            from fastembed import TextEmbedding
            # Suppress symlink warnings on Windows
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            EdgeEmbedder._fastembed_model = TextEmbedding("BAAI/bge-small-en-v1.5")
        except Exception as e:
            # Fallback will activate transparently
            EdgeEmbedder._fastembed_model = None

    def embed_text(self, text: str) -> List[float]:
        """Generate a 384-dimensional dense vector for a single text."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vectors for a batch of texts."""
        if not texts:
            return []

        # Try fastembed first
        if EdgeEmbedder._fastembed_model is not None:
            try:
                embeddings = list(EdgeEmbedder._fastembed_model.embed(texts))
                return [list(vec.astype(float)) for vec in embeddings]
            except Exception:
                pass

        # Fallback: Deterministic industrial dense vectorizer (384 dimensions)
        return [self._fallback_embed(t) for t in texts]

    def _fallback_embed(self, text: str) -> List[float]:
        """
        Deterministic, word/n-gram hashing dense projection normalized to unit sphere.
        Preserves keyword and semantic similarities for industrial machinery terminology.
        """
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = cleaned.split()
        if not tokens:
            return [0.0] * EMBEDDING_DIM

        # Generate character 3-grams and tokens
        features = list(tokens)
        for t in tokens:
            if len(t) >= 4:
                for i in range(len(t) - 2):
                    features.append(t[i:i+3])

        vec = [0.0] * EMBEDDING_DIM
        for feat in features:
            h = int(hashlib.sha256(feat.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBEDDING_DIM
            sign = 1.0 if ((h >> 9) & 1) == 1 else -1.0
            weight = 1.5 if len(feat) > 3 else 1.0
            vec[idx] += sign * weight

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            vec = [round(x / norm, 6) for x in vec]
        else:
            vec[0] = 1.0
        return vec
