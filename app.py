import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm
from collections import Counter

st.set_page_config(page_title="Simulasi Proyek FITE", layout="wide")

# =========================
# DATA AKTIVITAS
# =========================

activities = {
    'A': ['Persiapan & Perizinan', [], 1, 1.5, 2],
    'B': ['Pondasi & Struktur Bawah', ['A'], 2, 3, 4],
    'C': ['Struktur Lantai 1-2', ['B'], 3, 4, 5],
    'D': ['Struktur Lantai 3-4', ['C'], 3, 4, 5],
    'E': ['Struktur Lantai 5 & Atap', ['D'], 2, 3, 4],
    'F': ['MEP Kasar', ['C'], 2, 3, 4],
    'G': ['Instalasi Listrik', ['E','F'], 2, 3, 4],
    'H': ['Finishing', ['G'], 3, 4, 6],
    'I': ['Lab Khusus', ['G'], 4, 6, 9],
    'J': ['Perangkat Lab', ['I'], 1, 2, 3],
    'K': ['Testing', ['H','J'], 1, 1.5, 2]
}

# =========================
# FUNGSI PERT
# =========================

def pert_sample(a, m, b):
    mean = (a + 4*m + b) / 6
    std = (b - a) / 6
    return max(0.1, np.random.normal(mean, std))

# =========================
# HITUNG CPM
# =========================

def calculate_project(durations):
    es, ef = {}, {}

    for act in activities:
        preds = activities[act][1]

        if not preds:
            es[act] = 0
        else:
            es[act] = max(ef[p] for p in preds)

        ef[act] = es[act] + durations[act]

    total = max(ef.values())

    # critical path sederhana
    cp = [k for k in ef if ef[k] == total or any(ef[k] == es[s] for s in activities if k in activities[s][1])]

    return total, cp

# =========================
# MONTE CARLO
# =========================

def simulate(n, accelerate=False):
    results = []
    paths = []

    for _ in range(n):
        durations = {}

        for act, data in activities.items():
            d = pert_sample(data[2], data[3], data[4])

            # faktor risiko
            if np.random.rand() < 0.2:
                d += np.random.uniform(1,3)

            # percepatan
            if accelerate and act in ['C','D','I']:
                d *= 0.8

            durations[act] = d

        total, cp = calculate_project(durations)
        results.append(total)
        paths.append(tuple(cp))

    return np.array(results), paths

# =========================
# UI
# =========================

st.title("🏗️ Simulasi Proyek Gedung FITE 5 Lantai")

col1, col2 = st.columns(2)

with col1:
    n_sim = st.slider("Jumlah Simulasi", 100, 10000, 3000)

with col2:
    deadline = st.slider("Deadline (bulan)", 10, 30, 20)

run = st.button("🚀 Jalankan Simulasi")

# =========================
# OUTPUT
# =========================

if run:
    results, paths = simulate(n_sim)

    st.subheader("📊 Statistik Proyek")
    mean = np.mean(results)
    std = np.std(results)

    st.write(f"Durasi rata-rata: **{mean:.2f} bulan**")
    st.write(f"Risiko (std dev): **{std:.2f}**")

    # Critical Path
    st.subheader("🔗 Critical Path Dominan")
    cp = Counter(paths).most_common(1)[0][0]
    st.write(" → ".join(cp))

    # Probabilitas
    st.subheader("🎯 Probabilitas Deadline")
    z = (deadline - mean) / std if std > 0 else 0
    prob = norm.cdf(z)
    st.write(f"Probabilitas selesai ≤ {deadline} bulan: **{prob*100:.2f}%**")

    # Grafik
    st.subheader("📈 Distribusi Durasi")
    fig, ax = plt.subplots()
    ax.hist(results, bins=40)
    ax.set_xlabel("Durasi")
    ax.set_ylabel("Frekuensi")
    st.pyplot(fig)

    # =========================
    # SIMULASI RESOURCE
    # =========================

    st.subheader("⚡ Simulasi Percepatan Resource")

    fast_results, _ = simulate(n_sim, accelerate=True)

    fast_mean = np.mean(fast_results)

    st.write(f"Durasi Normal: **{mean:.2f} bulan**")
    st.write(f"Durasi Dipercepat: **{fast_mean:.2f} bulan**")
    st.write(f"Penghematan: **{mean - fast_mean:.2f} bulan**")

    # =========================
    # TABEL AKTIVITAS
    # =========================

    st.subheader("📋 Detail Aktivitas")

    df = pd.DataFrame([
        {
            "ID": k,
            "Aktivitas": v[0],
            "Optimis": v[2],
            "Most Likely": v[3],
            "Pesimis": v[4]
        }
        for k,v in activities.items()
    ])

    st.dataframe(df)