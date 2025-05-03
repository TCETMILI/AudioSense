from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import logger
import time
from transformers import pipeline
from collections import defaultdict

app = FastAPI(title="AudioSense Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    audio_sample: list[float] = Field(..., min_length=1)
    sample_rate: int           = Field(16000)
    predictions: list

# Modeli yükle (AST)
classifier = pipeline(
    "audio-classification",
    model="MIT/ast-finetuned-audioset-10-10-0.4593"
)

# Parametreler
CHUNK_S    = 3.0  # saniye
MAX_CHUNKS = 4    # en fazla işlenecek parça sayısı

def format_label(label: str):
    title = label.replace("_", " ").capitalize()
    return title

def build_text_summary(top3: list[tuple[str,float]]):
    """
    En baskın 3 etiketi insan dili cümlesiyle özetler,
    tamamen dinamik fallback kullanır.
    """
    if not top3:
        return "⚠️ Ses tespit edilemedi."
    titles = [ format_label(lbl) for lbl, _ in top3 ]
    if len(titles) == 1:
        return f"Kayıtta ağırlıklı olarak {titles[0]} var."
    if len(titles) == 2:
        return f"Kayıtta ağırlıklı olarak {titles[0]} ve {titles[1]} var."
    # 3 veya daha fazla
    return (
        f"Kayıtta ağırlıklı olarak {titles[0]}, "
        f"arka planda {titles[1]} ve ufak bir {titles[2]} tespit edildi."
    )

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    # A) NumPy dönüşümü
    start_ts = time.time()
    audio_np = np.array(req.audio_sample, dtype=np.float32)
    sr       = req.sample_rate
    total_s  = len(audio_np) / sr
    logger.log(f"Received {len(audio_np)} samples (~{total_s:.1f}s) @ {sr}Hz")

    # B) Chunk’lama ve sınır
    chunk_size = int(CHUNK_S * sr)
    raw_chunks = [
        audio_np[i : i + chunk_size]
        for i in range(0, len(audio_np), chunk_size)
        if len(audio_np[i : i + chunk_size]) > 0
    ]
    chunks = raw_chunks[:MAX_CHUNKS]
    logger.log(f"Slicing into {len(raw_chunks)} chunks, processing {len(chunks)}")

    # C) Model tahmini
    all_preds = []
    for idx, chunk in enumerate(chunks):
        try:
            preds = classifier(chunk, sampling_rate=sr, top_k=3)
        except Exception as e:
            logger.log(f"Chunk {idx} error: {e}")
            preds = []
        all_preds.append(preds)

    # D) Aggregate & top-3
    agg = defaultdict(list)
    for preds in all_preds:
        for p in preds:
            lbl   = p.get("label")
            score = p.get("score")
            if lbl and (score is not None):
                agg[lbl].append(score)

    avg_scores = {
        lbl: sum(scores)/len(scores)
        for lbl, scores in agg.items()
        if scores
    }
    top3 = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:3]

    # E) Tek cümlelik özet
    prefix = "🎵 "
    text_summary = prefix + build_text_summary(top3)

    preds_list = [
        {"label": lbl, "score": float(scr)}
        for lbl, scr in top3
    ]

    duration = time.time() - start_ts
    logger.log(f"Finished analyze in {duration:.2f}s, returning {len(top3)} preds")

    return {
        "status": "OK",
        "total_duration_s": total_s,
        "processed_chunks": len(chunks),
        "summary": text_summary,
        "predictions": preds_list
    }
