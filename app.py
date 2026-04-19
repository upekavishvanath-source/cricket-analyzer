"""
╔══════════════════════════════════════════════════════════════════╗
║        CRICKET SHOT POWER ANALYZER  —  Streamlit Web App         ║
║                                                                  ║
║  Install dependencies:                                           ║
║      pip install streamlit opencv-python mediapipe numpy pillow  ║
║                                                                  ║
║  Run locally:                                                    ║
║      streamlit run app.py                                        ║
║                                                                  ║
║  Deploy: Push to GitHub → connect to Streamlit Community Cloud   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os
import subprocess
import shutil
from collections import deque

# ══════════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Cricket Shot Power Analyzer",
    page_icon="🏏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════
#  CUSTOM CSS — dark neon theme
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* ── Cricket Photo URLs (free Pexels images) ── */
    /* Hero:   https://images.pexels.com/photos/3628912/pexels-photo-3628912.jpeg */
    /* Action: https://images.pexels.com/photos/2263436/pexels-photo-2263436.jpeg */

    /* ── Global ── */
    html, body {
        background-color: #0a0c0a !important;
        color: #e8e8e8;
        font-family: 'Courier New', monospace;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #0a0c0a !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: blur(8px);
    }
    [data-testid="stSidebar"] { background: #0f130f; }

    /* ── Hero Banner with Cricket Photo ── */
    .hero-banner {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 20px;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image: url('https://images.pexels.com/photos/3628912/pexels-photo-3628912.jpeg?auto=compress&cs=tinysrgb&w=1200');
        background-size: cover;
        background-position: center 30%;
        filter: brightness(0.25) saturate(0.5);
        z-index: 0;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(10,12,10,0.9) 100%);
        z-index: 1;
    }
    .hero-content {
        position: relative;
        z-index: 2;
        padding: 30px 20px;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: bold;
        color: #fff;
        font-family: 'Courier New', monospace;
        letter-spacing: 3px;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    .hero-title span { color: #39ff14; }
    .hero-sub {
        color: #7a9a7a;
        font-size: 12px;
        line-height: 1.7;
        max-width: 500px;
        margin: 0 auto 16px;
    }
    .badge-row {
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }
    .badge {
        background: rgba(57,255,20,0.12);
        border: 1px solid rgba(57,255,20,0.3);
        color: #39ff14;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 10px;
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
    }

    /* ── Upload area with cricket action photo ── */
    .upload-hero {
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 14px;
        padding: 20px;
    }
    .upload-hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image: url('https://images.pexels.com/photos/2263436/pexels-photo-2263436.jpeg?auto=compress&cs=tinysrgb&w=1000');
        background-size: cover;
        background-position: center;
        filter: brightness(0.15) saturate(0.3);
        z-index: 0;
    }
    .upload-hero-content {
        position: relative;
        z-index: 1;
    }
    .upload-hero h3 {
        color: #fff !important;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        font-size: 1.1rem !important;
        margin-bottom: 4px;
    }
    .upload-hero h3 span { color: #39ff14; }

    /* ── Stats strip ── */
    .stats-strip {
        display: flex;
        justify-content: space-around;
        background: #0f130f;
        border: 1px solid #1e2a1e;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 18px;
        text-align: center;
    }
    .stat-item .snum { font-size: 20px; font-weight: bold; color: #39ff14; font-family: 'Courier New', monospace; }
    .stat-item .slbl { font-size: 9px; color: #445544; letter-spacing: 1px; }

    /* ── How It Works steps ── */
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 18px;
    }
    .step-box {
        background: #111811;
        border: 1px solid #1e2a1e;
        border-radius: 8px;
        padding: 14px 10px;
        text-align: center;
    }
    .step-num {
        width: 26px; height: 26px; border-radius: 50%;
        background: rgba(57,255,20,0.1);
        border: 1px solid rgba(57,255,20,0.3);
        color: #39ff14; font-size: 11px; font-weight: bold;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 8px;
    }
    .step-box h4 { font-size: 9px; color: #ccc; letter-spacing: .5px; margin-bottom: 3px; }
    .step-box p  { font-size: 8px; color: #445544; line-height: 1.5; }

    /* ── Gear cards with stadium bg ── */
    .gear-section {
        position: relative;
        border-radius: 10px;
        overflow: hidden;
        padding: 20px;
        margin-top: 16px;
    }
    .gear-section::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image: url('https://images.pexels.com/photos/3628912/pexels-photo-3628912.jpeg?auto=compress&cs=tinysrgb&w=1200');
        background-size: cover;
        background-position: center 60%;
        filter: brightness(0.1) saturate(0.2);
        z-index: 0;
    }
    .gear-section::after {
        content: '';
        position: absolute;
        inset: 0;
        background: rgba(10,12,10,0.7);
        z-index: 1;
    }
    .gear-content {
        position: relative;
        z-index: 2;
    }
    .gear-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    .gear-card {
        background: #111811;
        border: 1px solid #1e2a1e;
        border-radius: 6px;
        padding: 10px 6px;
        text-align: center;
        transition: all .2s;
    }
    .gear-card:hover { border-color: #39ff14; background: rgba(57,255,20,0.05); }
    .gear-card .gico { font-size: 18px; margin-bottom: 4px; display: block; }
    .gear-card .gname { font-size: 9px; color: #7a9a7a; }
    .aff-note { font-size: 9px; color: #334433; text-align: center; margin-top: 8px; }

    /* ── Typography ── */
    h1 { color: #39ff14 !important; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    h2, h3, h4 { color: #e8e8e8 !important; font-family: 'Courier New', monospace; }
    p, li, label, span { color: #e8e8e8; }

    /* ── Buttons ── */
    .stButton > button {
        background: #111811;
        color: #39ff14;
        border: 1px solid #1e2a1e;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        letter-spacing: 1px;
        padding: 0.6rem 1.8rem;
        border-radius: 6px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #39ff14;
        color: #0a0c0a;
        border-color: #39ff14;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        border: 1px dashed #1e2a1e !important;
        border-radius: 8px;
        background: #0f130f !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #39ff14, #00aaff);
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #111811;
        border: 1px solid #1e2a1e;
        border-radius: 8px;
        padding: 12px;
    }
    [data-testid="stMetricLabel"] > div { color: #445544 !important; font-family: 'Courier New', monospace; font-size: 12px; }
    [data-testid="stMetricValue"] > div { color: #39ff14 !important; font-family: 'Courier New', monospace; }

    /* ── Alerts ── */
    .stAlert { border-radius: 6px; font-family: 'Courier New', monospace; }

    /* ── Video ── */
    video { border-radius: 8px; border: 1px solid #1e2a1e; }

    /* ── Divider ── */
    hr { border-color: #1e2a1e; }

    /* ── Info boxes ── */
    .info-card {
        background: #111811;
        border: 1px solid #1e2a1e;
        border-left: 3px solid #39ff14;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 12px 0;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #c0c0c0;
    }
    .stat-badge {
        display: inline-block;
        background: #0f130f;
        border: 1px solid #1e2a1e;
        border-radius: 4px;
        padding: 4px 10px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #00aaff;
        margin: 2px 4px;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  CONSTANTS  (identical to desktop version)
# ══════════════════════════════════════════════════════════════════

SHORTS_W, SHORTS_H   = 1080, 1920
NEON_GREEN           = (57, 255, 20)
NEON_BLUE            = (255, 160, 10)
WHITE                = (255, 255, 255)
DARK_PANEL           = (15, 15, 15)
ROLLING_WINDOW       = 10
SCALE_FACTOR         = 8.0
PIXELS_PER_METER     = 120.0
MAX_SPEED_KMH        = 160.0
METER_X              = SHORTS_W - 90
METER_TOP            = 400
METER_BOT            = 1400
METER_W              = 55
FREE_MAX_SECONDS     = 5.0       # Hard limit for free tier

mp_pose = mp.solutions.pose

IDX = {
    "NOSE":       mp_pose.PoseLandmark.NOSE.value,
    "L_SHOULDER": mp_pose.PoseLandmark.LEFT_SHOULDER.value,
    "R_SHOULDER": mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
    "L_ELBOW":    mp_pose.PoseLandmark.LEFT_ELBOW.value,
    "R_ELBOW":    mp_pose.PoseLandmark.RIGHT_ELBOW.value,
    "L_WRIST":    mp_pose.PoseLandmark.LEFT_WRIST.value,
    "R_WRIST":    mp_pose.PoseLandmark.RIGHT_WRIST.value,
    "L_HIP":      mp_pose.PoseLandmark.LEFT_HIP.value,
    "R_HIP":      mp_pose.PoseLandmark.RIGHT_HIP.value,
    "L_KNEE":     mp_pose.PoseLandmark.LEFT_KNEE.value,
    "R_KNEE":     mp_pose.PoseLandmark.RIGHT_KNEE.value,
    "L_ANKLE":    mp_pose.PoseLandmark.LEFT_ANKLE.value,
    "R_ANKLE":    mp_pose.PoseLandmark.RIGHT_ANKLE.value,
    "L_FOOT":     mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value,
    "R_FOOT":     mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value,
}

SKELETON_CONNECTIONS = [
    ("L_SHOULDER", "R_SHOULDER"),
    ("L_HIP",      "R_HIP"),
    ("L_SHOULDER", "L_HIP"),
    ("R_SHOULDER", "R_HIP"),
    ("L_SHOULDER", "L_ELBOW"), ("L_ELBOW", "L_WRIST"),
    ("R_SHOULDER", "R_ELBOW"), ("R_ELBOW", "R_WRIST"),
    ("L_HIP", "L_KNEE"), ("L_KNEE", "L_ANKLE"), ("L_ANKLE", "L_FOOT"),
    ("R_HIP", "R_KNEE"), ("R_KNEE", "R_ANKLE"), ("R_ANKLE", "R_FOOT"),
    ("NOSE", "L_SHOULDER"), ("NOSE", "R_SHOULDER"),
]


# ══════════════════════════════════════════════════════════════════
#  CORE HELPER FUNCTIONS  (identical logic to desktop version)
# ══════════════════════════════════════════════════════════════════

def lm_px(landmarks, idx, w, h):
    lm = landmarks[idx]
    return int(lm.x * w), int(lm.y * h)


def euclidean(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def to_shorts(frame):
    h, w     = frame.shape[:2]
    scale    = SHORTS_H / h
    new_w    = int(w * scale)
    resized  = cv2.resize(frame, (new_w, SHORTS_H))
    if new_w >= SHORTS_W:
        x0 = (new_w - SHORTS_W) // 2
        return resized[:, x0: x0 + SHORTS_W].copy()
    else:
        canvas       = np.zeros((SHORTS_H, SHORTS_W, 3), dtype=np.uint8)
        x0           = (SHORTS_W - new_w) // 2
        canvas[:, x0: x0 + new_w] = resized
        return canvas


def draw_skeleton(frame, landmarks, fw, fh):
    pts = {name: lm_px(landmarks, idx, fw, fh) for name, idx in IDX.items()}
    for a, b in SKELETON_CONNECTIONS:
        if a in pts and b in pts:
            cv2.line(frame, pts[a], pts[b], NEON_GREEN, 6,  cv2.LINE_AA)
            cv2.line(frame, pts[a], pts[b], WHITE,      2,  cv2.LINE_AA)
    for pt in pts.values():
        cv2.circle(frame, pt, 9, NEON_GREEN, -1, cv2.LINE_AA)
        cv2.circle(frame, pt, 5, WHITE,      -1, cv2.LINE_AA)
    return pts


def draw_power_meter(frame, ratio):
    cv2.rectangle(frame, (METER_X, METER_TOP), (METER_X + METER_W, METER_BOT), DARK_PANEL, -1)
    cv2.rectangle(frame, (METER_X, METER_TOP), (METER_X + METER_W, METER_BOT), NEON_GREEN, 2)
    if ratio > 0:
        fill_h  = int((METER_BOT - METER_TOP) * ratio)
        fill_y0 = METER_BOT - fill_h
        r       = int(255 * ratio)
        g       = int(255 * (1 - ratio))
        cv2.rectangle(frame, (METER_X + 2, fill_y0), (METER_X + METER_W - 2, METER_BOT), (0, g, r), -1)
    cv2.putText(frame, "POWER",  (METER_X - 15, METER_TOP - 25), cv2.FONT_HERSHEY_DUPLEX, 1.0, NEON_GREEN, 3, cv2.LINE_AA)
    cv2.putText(frame, f"{int(ratio * 100)}%", (METER_X - 5, METER_BOT + 45), cv2.FONT_HERSHEY_DUPLEX, 1.2, WHITE, 3, cv2.LINE_AA)


def draw_hud(frame, speed_kmh, peak_kmh, frame_no):
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (SHORTS_W, 160), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)
    cv2.putText(frame, "CRICKET SHOT ANALYZER", (30, 70),  cv2.FONT_HERSHEY_DUPLEX, 1.6, NEON_GREEN, 4, cv2.LINE_AA)
    cv2.putText(frame, f"Frame: {frame_no:04d}",  (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (180, 180, 180), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Bat Speed: {speed_kmh:.1f} km/h", (30, 240), cv2.FONT_HERSHEY_DUPLEX, 1.5, NEON_BLUE, 4, cv2.LINE_AA)
    if peak_kmh > 0:
        cv2.putText(frame, f"PEAK: {peak_kmh:.1f} km/h",   (30, 310), cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 80, 255), 5, cv2.LINE_AA)


# ══════════════════════════════════════════════════════════════════
#  VIDEO PROCESSING  (web-adapted, with Streamlit progress updates)
# ══════════════════════════════════════════════════════════════════

def process_video(input_path: str) -> dict:
    """
    Runs the full MediaPipe + OpenCV analysis pipeline.
    Returns a dict with output_path, peak_kmh, and frame_count.
    Writes an H.264 .mp4 via FFmpeg if available, else mp4v fallback.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return {"error": "Cannot open video file. Please try a different file."}

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # ── Write to a temp mp4 ──────────────────────────────────────
    tmp_raw  = tempfile.NamedTemporaryFile(suffix="_raw.mp4",  delete=False)
    tmp_out  = tempfile.NamedTemporaryFile(suffix="_out.mp4",  delete=False)
    raw_path = tmp_raw.name
    out_path = tmp_out.name
    tmp_raw.close()
    tmp_out.close()

    # Try avc1 (H.264 in mp4 container) — works on most systems
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(raw_path, fourcc, fps, (SHORTS_W, SHORTS_H))
    if not writer.isOpened():
        # Fallback to mp4v if avc1 unavailable
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(raw_path, fourcc, fps, (SHORTS_W, SHORTS_H))

    # ── Streamlit UI placeholders ────────────────────────────────
    progress_bar  = st.progress(0, text="Starting analysis…")
    col1, col2, col3, col4 = st.columns(4)
    ph_frame      = col1.empty()
    ph_speed      = col2.empty()
    ph_peak       = col3.empty()
    ph_power      = col4.empty()

    # ── Tracking state ───────────────────────────────────────────
    prev_wrist_L = None
    prev_wrist_R = None
    speed_buffer = deque(maxlen=ROLLING_WINDOW)
    peak_kmh     = 0.0
    frame_no     = 0

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_no += 1
            frame     = to_shorts(frame)
            fh, fw    = frame.shape[:2]

            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            current_kmh = 0.0

            if result.pose_landmarks:
                lms = result.pose_landmarks.landmark
                pts = draw_skeleton(frame, lms, fw, fh)

                wL      = pts["L_WRIST"]
                wR      = pts["R_WRIST"]
                speed_L = euclidean(prev_wrist_L, wL) if prev_wrist_L else 0.0
                speed_R = euclidean(prev_wrist_R, wR) if prev_wrist_R else 0.0

                raw = max(speed_L, speed_R) * SCALE_FACTOR
                speed_buffer.append(raw)

                current_speed_uf  = float(np.mean(speed_buffer))
                raw_pixels_moved  = current_speed_uf / SCALE_FACTOR
                meters_moved      = raw_pixels_moved / PIXELS_PER_METER
                m_s               = meters_moved * fps
                current_kmh       = m_s * 3.6

                if current_kmh > peak_kmh:
                    peak_kmh = current_kmh

                prev_wrist_L = wL
                prev_wrist_R = wR
            else:
                prev_wrist_L = None
                prev_wrist_R = None

            power_ratio = min(current_kmh / MAX_SPEED_KMH, 1.0)
            draw_power_meter(frame, power_ratio)
            draw_hud(frame, current_kmh, peak_kmh, frame_no)

            writer.write(frame)

            # ── Update Streamlit UI every 5 frames ──────────────
            if frame_no % 5 == 0 or frame_no == 1:
                pct = int((frame_no / total_frames) * 100) if total_frames > 0 else 0
                progress_bar.progress(
                    min(pct, 100),
                    text=f"Analysing… frame {frame_no}/{total_frames} — {current_kmh:.1f} km/h"
                )
                ph_frame.metric("Frame",      f"{frame_no}")
                ph_speed.metric("Bat Speed",  f"{current_kmh:.1f} km/h")
                ph_peak.metric("Peak Speed",  f"{peak_kmh:.1f} km/h")
                ph_power.metric("Power",      f"{int(power_ratio * 100)}%")

    cap.release()
    writer.release()

    progress_bar.progress(100, text="Analysis complete! Re-encoding for browser…")

    # ── Re-encode with FFmpeg for guaranteed browser compatibility ─
    ffmpeg_path = shutil.which("ffmpeg")
    final_path  = out_path

    if ffmpeg_path:
        try:
            cmd = [
                ffmpeg_path, "-y",
                "-i", raw_path,
                "-vcodec", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",   # required for browser compatibility
                "-movflags", "+faststart",  # allows streaming before full download
                out_path,
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            os.unlink(raw_path)          # clean up raw file
            final_path = out_path
        except Exception as e:
            # FFmpeg failed — fall back to the raw mp4
            final_path = raw_path
    else:
        # No FFmpeg — use raw output directly (may not play in all browsers)
        final_path = raw_path

    progress_bar.progress(100, text="Done! ✅")

    return {
        "output_path": final_path,
        "peak_kmh":    round(peak_kmh, 1),
        "frame_count": frame_no,
        "fps":         round(fps, 1),
    }


# ══════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════

def main():

    # ── HERO BANNER with cricket photo background ────────────────
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-content">
            <div class="badge-row">
                <span class="badge">MEDIAPIPE AI</span>
                <span class="badge">OPENCV</span>
                <span class="badge">FREE TOOL</span>
                <span class="badge">NO SIGNUP</span>
            </div>
            <div class="hero-title">🏏 CRICKET SHOT<br><span>POWER ANALYZER</span></div>
            <div class="hero-sub">
                Upload your batting clip — our AI tracks your skeleton frame-by-frame,
                calculates real bat speed in km/h, and overlays a live power meter on your video.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Strip ──────────────────────────────────────────────
    st.markdown("""
    <div class="stats-strip">
        <div class="stat-item"><div class="snum">160</div><div class="slbl">MAX KM/H TRACKED</div></div>
        <div class="stat-item"><div class="snum">15+</div><div class="slbl">BODY LANDMARKS</div></div>
        <div class="stat-item"><div class="snum">30fps</div><div class="slbl">FRAME ANALYSIS</div></div>
        <div class="stat-item"><div class="snum">FREE</div><div class="slbl">NO ACCOUNT NEEDED</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── How It Works ─────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:11px;color:#39ff14;letter-spacing:2px;margin-bottom:4px;font-family:'Courier New',monospace">HOW IT WORKS</div>
    <div class="steps-grid">
        <div class="step-box">
            <div class="step-num">1</div>
            <div style="font-size:18px;margin-bottom:6px">📂</div>
            <h4>UPLOAD CLIP</h4>
            <p>Upload your MP4/AVI batting video (max 5s free)</p>
        </div>
        <div class="step-box">
            <div class="step-num">2</div>
            <div style="font-size:18px;margin-bottom:6px">🦴</div>
            <h4>POSE DETECTION</h4>
            <p>MediaPipe maps 15+ body landmarks every frame</p>
        </div>
        <div class="step-box">
            <div class="step-num">3</div>
            <div style="font-size:18px;margin-bottom:6px">⚡</div>
            <h4>BAT SPEED CALC</h4>
            <p>Wrist velocity converted to km/h with physics math</p>
        </div>
        <div class="step-box">
            <div class="step-num">4</div>
            <div style="font-size:18px;margin-bottom:6px">🎬</div>
            <h4>DOWNLOAD VIDEO</h4>
            <p>Get your video with neon skeleton + power meter</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Affiliate / Gear Section (sidebar) ──────────────────────
    with st.sidebar:
        st.markdown("### 🏏 Cricket Gear")
        st.markdown("""
        Upgrade your game with top-rated equipment:

        - 🏏 [Cricket Bats on Amazon](https://www.amazon.com/s?k=cricket+bat)
        - 🧤 [Batting Gloves](https://www.amazon.com/s?k=cricket+batting+gloves)
        - 🦺 [Batting Pads](https://www.amazon.com/s?k=cricket+batting+pads)
        - ⛑️ [Helmets](https://www.amazon.com/s?k=cricket+helmet)
        - 🎥 [Action Cameras (for recording)](https://www.amazon.com/s?k=action+camera+sports)

        ---
        *Affiliate links — we earn a small commission at no extra cost to you.*
        """)
        st.divider()
        st.markdown("### 🔓 Unlock Pro")
        st.markdown("""
        Want unlimited video length, batch analysis, and HD export?

        **[→ Contact us to upgrade](mailto:your@email.com)**
        """)

    # ── Upload Area with cricket photo background ────────────────
    st.markdown("""
    <div class="upload-hero">
        <div class="upload-hero-content">
            <h3>ANALYZE YOUR <span>SHOT NOW</span></h3>
            <p style="font-size:11px;color:#7a9a7a;margin-bottom:10px;font-family:'Courier New',monospace">
                ⚠️ Free Tier: Max 5-second video &nbsp;·&nbsp;
                <a href="mailto:your@email.com" style="color:#ff9900">Unlock unlimited →</a>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Free Tier Warning ────────────────────────────────────────
    st.markdown("""
    <div class="info-card">
        ⚠️ <strong>Free Tool Limit:</strong> Max 5-second video. Longer videos will not be processed.
    </div>
    """, unsafe_allow_html=True)

    # ── File Uploader ────────────────────────────────────────────
    uploaded = st.file_uploader(
        label="📂 Drag & drop or click to browse — MP4 · AVI · MOV · MKV",
        type=["mp4", "avi", "mov", "mkv"],
        help="Supported formats: MP4, AVI, MOV, MKV — max 5 seconds (free tier)",
    )

    if not uploaded:
        st.markdown("""
        <div class="info-card">
            💡 <strong>Tips for best results:</strong><br>
            • Record from a fixed camera position (side-on angle is ideal)<br>
            • Ensure the batsman's full body is visible in frame<br>
            • Good lighting helps MediaPipe detect the skeleton accurately<br>
            • 30fps or higher gives more accurate bat speed readings
        </div>
        """, unsafe_allow_html=True)

        # ── Gear Section with photo background (shown before upload) ──
        st.markdown("""
        <div class="gear-section">
            <div class="gear-content">
                <div style="text-align:center;margin-bottom:4px;font-size:11px;color:#39ff14;letter-spacing:2px;font-family:'Courier New',monospace">ELEVATE YOUR GAME</div>
                <div style="text-align:center;font-size:9px;color:#445544;margin-bottom:10px;font-family:'Courier New',monospace">Top-rated cricket gear — trusted by players at every level</div>
                <div class="gear-grid">
                    <a href="https://www.amazon.com/s?k=cricket+bat" target="_blank" style="text-decoration:none">
                        <div class="gear-card"><span class="gico">🏏</span><div class="gname">Cricket Bats</div></div>
                    </a>
                    <a href="https://www.amazon.com/s?k=cricket+batting+gloves" target="_blank" style="text-decoration:none">
                        <div class="gear-card"><span class="gico">🧤</span><div class="gname">Batting Gloves</div></div>
                    </a>
                    <a href="https://www.amazon.com/s?k=cricket+batting+pads" target="_blank" style="text-decoration:none">
                        <div class="gear-card"><span class="gico">🦺</span><div class="gname">Batting Pads</div></div>
                    </a>
                    <a href="https://www.amazon.com/s?k=cricket+helmet" target="_blank" style="text-decoration:none">
                        <div class="gear-card"><span class="gico">⛑️</span><div class="gname">Helmets</div></div>
                    </a>
                    <a href="https://www.amazon.com/s?k=action+camera+sports" target="_blank" style="text-decoration:none">
                        <div class="gear-card"><span class="gico">🎥</span><div class="gname">Action Cams</div></div>
                    </a>
                </div>
                <div class="aff-note">Affiliate links — helps keep this tool free ❤️</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Save Upload to Temp File ─────────────────────────────────
    suffix = os.path.splitext(uploaded.name)[-1].lower() or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded.read())
        input_path = tmp.name

    # ── Duration Check ───────────────────────────────────────────
    cap       = cv2.VideoCapture(input_path)
    frames    = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps_check = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()

    duration = frames / fps_check if fps_check > 0 else 0

    st.markdown(f"""
    <div class="info-card">
        📹 <strong>{uploaded.name}</strong> &nbsp;|&nbsp;
        <span class="stat-badge">{frames} frames</span>
        <span class="stat-badge">{fps_check:.1f} fps</span>
        <span class="stat-badge">{duration:.2f}s</span>
    </div>
    """, unsafe_allow_html=True)

    if duration > FREE_MAX_SECONDS:
        os.unlink(input_path)
        st.error(
            f"❌ Video is **{duration:.1f} seconds** — exceeds the 5-second free limit.\n\n"
            f"[Click here to unlock unlimited processing time](mailto:your@email.com)"
        )
        return

    # ── Analyse Button ───────────────────────────────────────────
    st.markdown("---")
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        analyse = st.button("⚡  Analyze Shot", use_container_width=True)

    if not analyse:
        return

    # ── Run Analysis ─────────────────────────────────────────────
    st.markdown("#### 📊 Live Analysis")
    result = process_video(input_path)

    # Clean up temp input
    try:
        os.unlink(input_path)
    except Exception:
        pass

    if "error" in result:
        st.error(f"❌ {result['error']}")
        return

    # ── Results ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🏆 Analysis Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Peak Bat Speed",  f"{result['peak_kmh']} km/h")
    c2.metric("Frames Processed", str(result['frame_count']))
    c3.metric("Video FPS",        f"{result['fps']}")

    # Power rating label
    pkm = result["peak_kmh"]
    if pkm >= 120:
        rating = "💥 EXPLOSIVE"
    elif pkm >= 80:
        rating = "⚡ POWERFUL"
    elif pkm >= 50:
        rating = "🎯 MODERATE"
    else:
        rating = "🏏 DEVELOPING"

    st.markdown(f"""
    <div class="info-card" style="border-left-color: #00aaff; text-align:center;">
        <strong style="font-size:1.4rem;">{rating}</strong><br>
        <span style="color:#666677;">Peak bat speed: {pkm} km/h</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Output Video ─────────────────────────────────────────────
    st.markdown("#### 🎬 Analyzed Video (with Skeleton & Power Meter)")

    out_path = result["output_path"]
    if os.path.exists(out_path):
        with open(out_path, "rb") as vf:
            video_bytes = vf.read()

        st.video(video_bytes)

        st.download_button(
            label="⬇️  Download Analyzed Video",
            data=video_bytes,
            file_name="cricket_shot_analysis.mp4",
            mime="video/mp4",
            use_container_width=True,
        )

        # Clean up output temp file
        try:
            os.unlink(out_path)
        except Exception:
            pass
    else:
        st.warning("Output video file not found. Try downloading from the server logs.")

    # ── Gear Section with cricket photo background ───────────────
    st.markdown("""
    <div class="gear-section">
        <div class="gear-content">
            <div style="text-align:center;margin-bottom:4px;font-size:11px;color:#39ff14;letter-spacing:2px;font-family:'Courier New',monospace">ELEVATE YOUR GAME</div>
            <div style="text-align:center;font-size:9px;color:#445544;margin-bottom:10px;font-family:'Courier New',monospace">Top-rated cricket gear — trusted by players at every level</div>
            <div class="gear-grid">
                <a href="https://www.amazon.com/s?k=cricket+bat" target="_blank" style="text-decoration:none">
                    <div class="gear-card"><span class="gico">🏏</span><div class="gname">Cricket Bats</div></div>
                </a>
                <a href="https://www.amazon.com/s?k=cricket+batting+gloves" target="_blank" style="text-decoration:none">
                    <div class="gear-card"><span class="gico">🧤</span><div class="gname">Batting Gloves</div></div>
                </a>
                <a href="https://www.amazon.com/s?k=cricket+batting+pads" target="_blank" style="text-decoration:none">
                    <div class="gear-card"><span class="gico">🦺</span><div class="gname">Batting Pads</div></div>
                </a>
                <a href="https://www.amazon.com/s?k=cricket+helmet" target="_blank" style="text-decoration:none">
                    <div class="gear-card"><span class="gico">⛑️</span><div class="gname">Helmets</div></div>
                </a>
                <a href="https://www.amazon.com/s?k=action+camera+sports" target="_blank" style="text-decoration:none">
                    <div class="gear-card"><span class="gico">🎥</span><div class="gname">Action Cams</div></div>
                </a>
            </div>
            <div class="aff-note">Affiliate links — helps keep this tool free ❤️</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
