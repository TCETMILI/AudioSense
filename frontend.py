import gradio as gr
import requests
import soundfile as sf
import librosa
import numpy as np
import matplotlib.pyplot as plt

BACKEND_URL = "http://127.0.0.1:8000/analyze"

def plot_energy(y, sr):
    frame_len = int(0.1 * sr)
    energy = np.array([np.mean(y[i : i + frame_len] ** 2)
                       for i in range(0, len(y), frame_len)])
    times = np.arange(len(energy)) * (frame_len / sr)
    fig, ax = plt.subplots(figsize=(10,3))
    ax.fill_between(times, energy, color="#69b3a2", alpha=0.6)
    ax.plot(times, energy, color="#054a29", linewidth=1)
    ax.set_title("Enerji Zaman Serisi", fontsize=14, pad=10)
    ax.set_xlabel("Saniye", fontsize=12)
    ax.set_ylabel("Enerji", fontsize=12)
    ax.grid(linestyle=":", linewidth=0.5, color="gray", alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return fig

def plot_spectral_centroid(y, sr):
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    times    = librosa.times_like(centroid, sr=sr)
    fig, ax = plt.subplots(figsize=(10,3))
    ax.plot(times, centroid, linestyle='-', marker='o', markersize=3,
            markerfacecolor="#ff7f0e", markeredgewidth=0,
            color="#d62728", linewidth=1.2, alpha=0.8)
    ax.set_title("Spektral Merkez Zaman Serisi", fontsize=14, pad=10)
    ax.set_xlabel("Zaman (s)", fontsize=12)
    ax.set_ylabel("Merkez Frekans (Hz)", fontsize=12)
    ax.grid(linestyle="--", linewidth=0.5, color="gray", alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    return fig

def plot_prediction(preds):
    if not preds:
        return None
    labels = [p["label"] for p in preds]
    scores = [p["score"] for p in preds]
    fig, ax = plt.subplots(figsize=(8,3))
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, scores, align='center',
                   color=["#1f77b4","#ff7f0e","#2ca02c"][:len(labels)],
                   alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xlabel("Skor", fontsize=12)
    ax.set_title("Top-3 Tahmin Skorları", fontsize=14, pad=10)
    ax.invert_yaxis()
    ax.grid(axis='x', linestyle=":", linewidth=0.5, color="gray", alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.01, bar.get_y() + bar.get_height()/2,
                f"{w:.2f}", va='center', fontsize=11)
    fig.tight_layout()
    return fig

def analyze_audio(audio_path, sample_rate):
    # 1) Girdi kontrolü
    if audio_path is None:
        return ("⚠️ Lütfen önce ses kaydı yapın veya dosya yükleyin.",
                None, None, None, "", None)

     # 2) audio_path tipine göre unpack
    try:
        if isinstance(audio_path, tuple):
            # numpy modunda gelmiş: (sr, data)
            sr, audio_data = audio_path
        else:
            # filepath modunda gelmiş
            audio_data, sample_rate = sf.read(audio_path)
        # stereo ise mono’ya indir
        audio_data = audio_data.astype(np.float32)
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)
        if sample_rate != 16000:
             audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
             sample_rate = 16000
    except Exception as e:
        return (f"⚠️ Önizleme hatası: {e}", None, None, None, "", None)
    # 3) Backend’e gönder
    try:
        resp = requests.post(
            BACKEND_URL,
            json={
                "audio_sample": audio_data.tolist(),
                "sample_rate": sr,
                "predictions": []
            },
            timeout=60
        )
        resp.raise_for_status()
        j = resp.json()
    except Exception as e:
        return (f"⚠️ API hatası: {e}", None, None, None, "", None)

    summary = j.get("summary", "⚠️ Beklenmedik çıktı.")
    preds   = j.get("predictions", [])
    top3    = sorted(preds, key=lambda x: x["score"], reverse=True)

    # 4) Grafikleri oluştur
    fig_e   = plot_energy(audio_data, sr)
    fig_sc  = plot_spectral_centroid(audio_data, sr)
    fig_bar = plot_prediction(top3)

    return (summary, fig_e, fig_sc, fig_bar)



with gr.Blocks(title="AudioSense", theme="hmb/amethyst") as demo:
    title = gr.Markdown("## 🎵 AudioSense")

    sample_rate = gr.State(16000) 
    input = gr.Audio(label="🎤 Ses Kaydet / Yükle", type="numpy")
    btn = gr.Button("🔍 Analiz Et", variant="primary", size="sm")
    summary = gr.Textbox("", label="📝 Özet")

    with gr.Tabs():
        with gr.TabItem("Enerji Grafiği"): 
            energy_plot = gr.Plot(label="📈 Enerji Zaman Serisi")
        with gr.TabItem("Spektral Merkez Grafik"): 
            centroid_plot = gr.Plot(label="🔊 Spektral Merkez Zaman Serisi")
        with gr.TabItem("Tahmini Grafik"): 
            top3_plot = gr.Plot(label="📊 Top-3 Tahmin Skorları")
    # Callback sonrası hem summary hem de grafikleri güncelle
    btn.click(fn=analyze_audio,
              inputs=[input, sample_rate],
              outputs=[summary, energy_plot, centroid_plot, top3_plot],
              show_progress=True)

if __name__ == "__main__":
    demo.launch()