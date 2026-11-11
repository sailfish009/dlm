#!/usr/bin/env python3
"""PyTorch reference for the tiny transformer, without import-time training."""
import math, random
from pathlib import Path
import torch
from torch import nn

D = 32
HEADS = 2
D_FF = 64
NUM_LAYERS = 2
MAX_LENGTH = 32

EN_CN_PAIRS = [
    ("there is a cat under the table", "桌子 下面 有 一只 猫"),
    ("there is a dog on the chair", "椅子 上面 有 一只 狗"),
    ("there is a cat on the chair", "椅子 上面 有 一只 猫"),
    ("there is a dog under the table", "桌子 下面 有 一只 狗"),
    ("there is a small cat on the table", "桌子 上面 有 一只 小 猫"),
    ("there is a small dog under the chair", "椅子 下面 有 一只 小 狗"),
    ("there is a black cat under the chair", "椅子 下面 有 一只 黑色 猫"),
    ("there is a black dog on the table", "桌子 上面 有 一只 黑色 狗"),
]

SOURCE_WORDS = sorted({w for en, _ in EN_CN_PAIRS for w in en.split()})
TARGET_WORDS = ["<BOS>", "<EOS>"] + sorted({w for _, cn in EN_CN_PAIRS for w in cn.split()})
SOURCE_IDS = {w: i for i, w in enumerate(SOURCE_WORDS)}
TARGET_IDS = {w: i for i, w in enumerate(TARGET_WORDS)}
BOS = TARGET_IDS["<BOS>"]
EOS = TARGET_IDS["<EOS>"]

def examples():
    out = []
    for en, cn in EN_CN_PAIRS:
        src = [SOURCE_IDS[w] for w in en.split()]
        tgt = [BOS] + [TARGET_IDS[w] for w in cn.split()] + [EOS]
        out.append((torch.tensor(src, dtype=torch.long),
                    torch.tensor(tgt, dtype=torch.long)))
    return out

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_length):
        super().__init__()
        pe = torch.zeros(max_length, d_model)
        for pos in range(max_length):
            for i in range(d_model // 2):
                angle = pos / (10000.0 ** (2 * i / d_model))
                pe[pos, 2 * i] = math.sin(angle)
                pe[pos, 2 * i + 1] = math.cos(angle)
        self.register_buffer("pe", pe)

    def forward(self, x):
        return torch.stack([x[pos] + self.pe[pos] for pos in range(len(x))])

class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, D)
        self.position = PositionalEncoding(D, MAX_LENGTH)

    def forward(self, token_ids):
        return self.position(self.embedding(token_ids) * math.sqrt(D))

def attention(q, k, v, causal=False):
    scores = q @ k.T / math.sqrt(q.shape[-1])
    if causal:
        mask = torch.triu(torch.ones_like(scores, dtype=torch.bool), diagonal=1)
        scores = scores.masked_fill(mask, float("-inf"))
    weights = torch.softmax(scores, dim=-1)
    return weights @ v

class AttentionHead(nn.Module):
    def __init__(self):
        super().__init__()
        hd = D // HEADS
        self.q_proj = nn.Linear(D, hd)
        self.k_proj = nn.Linear(D, hd)
        self.v_proj = nn.Linear(D, hd)

    def forward(self, query, key, value, causal=False):
        return attention(self.q_proj(query), self.k_proj(key), self.v_proj(value), causal)

class MultiHeadAttention(nn.Module):
    def __init__(self):
        super().__init__()
        self.heads = nn.ModuleList([AttentionHead() for _ in range(HEADS)])
        self.out_proj = nn.Linear(D, D)

    def forward(self, query, key, value, causal=False):
        joined = torch.cat([h(query, key, value, causal) for h in self.heads], dim=-1)
        return self.out_proj(joined)

class FeedForward(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(D, D_FF), nn.ReLU(), nn.Linear(D_FF, D))

    def forward(self, x):
        return self.network(x)

class EncoderLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.self_mha = MultiHeadAttention()
        self.ffn = FeedForward()
        self.norm1 = nn.LayerNorm(D)
        self.norm2 = nn.LayerNorm(D)

    def forward(self, x):
        x = self.norm1(x + self.self_mha(x, x, x))
        return self.norm2(x + self.ffn(x))

class Encoder(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.layers = nn.ModuleList([EncoderLayer() for _ in range(n)])

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

class DecoderLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.self_attn = MultiHeadAttention()
        self.cross_attn = MultiHeadAttention()
        self.ffn = FeedForward()
        self.norm1 = nn.LayerNorm(D)
        self.norm2 = nn.LayerNorm(D)
        self.norm3 = nn.LayerNorm(D)

    def forward(self, x, enc):
        x = self.norm1(x + self.self_attn(x, x, x, causal=True))
        x = self.norm2(x + self.cross_attn(x, enc, enc))
        return self.norm3(x + self.ffn(x))

class Decoder(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.layers = nn.ModuleList([DecoderLayer() for _ in range(n)])

    def forward(self, x, enc):
        for layer in self.layers:
            x = layer(x, enc)
        return x

class Transformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.source_embedding = TokenEmbedding(len(SOURCE_WORDS))
        self.target_embedding = TokenEmbedding(len(TARGET_WORDS))
        self.encoder = Encoder(NUM_LAYERS)
        self.decoder = Decoder(NUM_LAYERS)
        self.output_projection = nn.Linear(D, len(TARGET_WORDS))

    def encode(self, source):
        return self.encoder(self.source_embedding(source))

    def decode(self, target, enc):
        return self.output_projection(self.decoder(self.target_embedding(target), enc))

    def forward(self, source, target):
        return self.decode(target, self.encode(source))

def train(seed=42, epochs=100, lr=0.003, verbose=True):
    random.seed(seed); torch.manual_seed(seed); torch.set_num_threads(1)
    model = Transformer()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.CrossEntropyLoss()
    data = examples()
    losses = []
    model.train()
    for epoch in range(epochs):
        random.shuffle(data)
        total = 0.0
        for src, tgt in data:
            logits = model(src, tgt[:-1])
            loss = crit(logits, tgt[1:])
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item()
        losses.append(total / len(data))
        if verbose and (epoch == 0 or (epoch + 1) % 20 == 0):
            print(f"epoch {epoch+1:3d} loss {losses[-1]:.4f}")
    model.eval()
    return model, losses

@torch.no_grad()
def greedy(model, english, max_steps=16, return_logits=False):
    model.eval()
    src = torch.tensor([SOURCE_IDS[w] for w in english.split()], dtype=torch.long)
    enc = model.encode(src)
    prefix = [BOS]
    logits_trace = []
    for _ in range(min(max_steps, MAX_LENGTH)):
        logits = model.decode(torch.tensor(prefix, dtype=torch.long), enc)
        last = logits[-1]
        logits_trace.append(last.tolist())
        nxt = int(last.argmax())
        if nxt == EOS:
            break
        prefix.append(nxt)
    text = "".join(TARGET_WORDS[i] for i in prefix[1:])
    return (text, logits_trace) if return_logits else text

def save_checkpoint(model, path):
    torch.save({'state_dict': model.state_dict(),
                'source_words': SOURCE_WORDS, 'target_words': TARGET_WORDS}, path)

def load_checkpoint(path):
    ck = torch.load(path, map_location='cpu', weights_only=False)
    model = Transformer()
    model.load_state_dict(ck['state_dict'])
    model.eval()
    return model

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    model, losses = train()
    save_checkpoint(model, root / 'checkpoint.pt')
    for en, _ in EN_CN_PAIRS:
        print(f"{en:45s} -> {greedy(model, en)}")
