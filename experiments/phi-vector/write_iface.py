"""Write interface — act -> trace vector + amplitudes. DESIGN §7.2.

Deterministic projector (fork decision 3: embedding/lm_head, no training):
the content embedding (mean-pool of the act content tokens from the core's own
embedding table) IS the trace vector; the d x d projector is the identity.
Amplitudes come from bank.deposit_amplitudes (loudness x cap x layer emphasis).
"""
import numpy as np
import mlx.core as mx

class WriteIface:
    def __init__(self, embed_tokens, tokenizer):
        self.embed = embed_tokens          # nn.Embedding [vocab, d], quantized weights ok
        self.tok = tokenizer

    def content_vector(self, text: str) -> "np.ndarray [d] fp16":
        ids = self.tok.encode(text)
        if not ids: ids = [self.tok.eos_token_id]
        embs = self.embed(ids)             # [n, d] (bfloat16)
        mean = mx.mean(embs.astype(mx.float32), axis=0)
        return np.array(mean, copy=False).astype(np.float16)
