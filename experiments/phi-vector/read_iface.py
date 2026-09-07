"""Read interface — trace vectors -> resident prefix before attention. DESIGN §7.3, §4.

The read projector is the identity (same fork decision): trace vectors live in the
core's embedding space, so the prefix enters the stream exactly where token
embeddings enter it. The model's own embed_scale (= sqrt(hidden_size)) is applied
at injection, matching the scale of normal token embeddings.
"""
import mlx.core as mx
mx_f32 = mx.float32 if hasattr(mx, "float32") else mx.bfloat16

class ReadIface:
    def __init__(self, embed_scale: float, dials: dict):
        self.embed_scale = embed_scale
        self.prefix_depth = dials.get("prefix_depth", 12)   # show dials (Fork 7)

    def prefix_embeddings(self, bank) -> "mx.array [1, n, d] or None":
        pv = bank.prefix_vectors(self.prefix_depth)          # [n, d] amplitude-scaled
        if pv is None: return None
        # NOTE: the model applies embed_scale to input_embeddings internally;
        # pre-scaling here would double it (verified by diagnostic).
        return pv.astype(mx.bfloat16)[None]
