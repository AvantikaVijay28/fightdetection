from flask import Flask, request, jsonify
import os
from fight_detect import detect_fight

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Rivox — Fight Detection</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg: #04080f;
            --surface: #080f1a;
            --surface2: #0c1525;
            --border: rgba(0,200,255,0.08);
            --border-bright: rgba(0,200,255,0.22);
            --cyan: #00c8ff;
            --cyan-dim: rgba(0,200,255,0.1);
            --cyan-glow: rgba(0,200,255,0.25);
            --red: #ff3a3a;
            --red-dim: rgba(255,58,58,0.1);
            --red-glow: rgba(255,58,58,0.3);
            --green: #00ff9d;
            --green-dim: rgba(0,255,157,0.1);
            --green-glow: rgba(0,255,157,0.3);
            --text: #e2eaf5;
            --muted: #3d5470;
            --r: 16px;
        }
        html { height: 100%; }
        body {
            min-height: 100dvh;
            background: var(--bg);
            color: var(--text);
            font-family: "Space Grotesk", sans-serif;
            -webkit-font-smoothing: antialiased;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-bottom: 48px;
        }
        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.03) 2px,rgba(0,0,0,0.03) 4px);
            pointer-events: none;
            z-index: 0;
        }
        * { position: relative; z-index: 1; }

        header {
            width: 100%;
            max-width: 520px;
            padding: 24px 20px 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .hx-mark {
            width: 32px; height: 32px;
            border: 1.5px solid var(--cyan);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 0 12px var(--cyan-glow), inset 0 0 8px var(--cyan-dim);
        }
        .hx-mark svg { width: 16px; height: 16px; }
        .brand {
            font-family: "Space Mono", monospace;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 2px;
            color: var(--cyan);
            text-transform: uppercase;
        }
        .version {
            margin-left: auto;
            font-family: "Space Mono", monospace;
            font-size: 10px;
            color: var(--muted);
            letter-spacing: 1px;
            border: 1px solid var(--border-bright);
            padding: 4px 8px;
            border-radius: 4px;
        }

        .card {
            width: calc(100% - 32px);
            max-width: 520px;
            margin-top: 20px;
            background: var(--surface);
            border: 1px solid var(--border-bright);
            border-radius: var(--r);
            overflow: hidden;
        }
        .card-top {
            border-bottom: 1px solid var(--border);
            padding: 14px 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .dot { width: 6px; height: 6px; border-radius: 50%; }
        .dot-r { background: #ff453a; }
        .dot-y { background: #ffd60a; }
        .dot-g { background: #34c759; }
        .card-label {
            margin-left: 8px;
            font-family: "Space Mono", monospace;
            font-size: 10px;
            color: var(--muted);
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .card-inner { padding: 20px; }

        .upload-zone {
            border: 1px dashed var(--border-bright);
            border-radius: 12px;
            padding: 28px 16px;
            text-align: center;
            cursor: pointer;
            background: var(--cyan-dim);
            transition: border-color 0.2s;
            -webkit-tap-highlight-color: transparent;
        }
        .upload-zone.has-file { border-color: var(--cyan); border-style: solid; }
        .upload-icon-wrap {
            width: 48px; height: 48px;
            border: 1px solid var(--border-bright);
            border-radius: 12px;
            margin: 0 auto 12px;
            display: flex; align-items: center; justify-content: center;
            background: var(--surface2);
        }
        .upload-icon-wrap svg { width: 22px; height: 22px; stroke: var(--cyan); fill: none; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
        .upload-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
        .upload-sub { font-family: "Space Mono", monospace; font-size: 10px; color: var(--muted); letter-spacing: 0.5px; }
        #fileInput { display: none; }
        video#preview {
            display: none;
            width: 100%;
            border-radius: 10px;
            margin-top: 14px;
            max-height: 200px;
            object-fit: cover;
            background: #000;
            border: 1px solid var(--border-bright);
        }

        .btn {
            width: 100%;
            margin-top: 16px;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid var(--cyan);
            background: var(--cyan-dim);
            color: var(--cyan);
            font-family: "Space Mono", monospace;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 0 16px var(--cyan-glow);
            -webkit-tap-highlight-color: transparent;
        }
        .btn:active { background: rgba(0,200,255,0.2); }
        .btn:disabled { opacity: 0.35; cursor: not-allowed; box-shadow: none; }

        #loading { display: none; text-align: center; padding: 24px 0 8px; }
        .radar { width: 48px; height: 48px; margin: 0 auto 14px; position: relative; }
        .radar::before { content: ""; position: absolute; inset: 0; border: 1.5px solid var(--cyan); border-radius: 50%; opacity: 0.3; }
        .radar::after { content: ""; position: absolute; inset: 4px; border: 1.5px solid var(--cyan); border-top-color: transparent; border-radius: 50%; animation: spin 0.9s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading-txt { font-family: "Space Mono", monospace; font-size: 11px; color: var(--cyan); letter-spacing: 1.5px; animation: blink 1.2s ease-in-out infinite; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }

        #result-block { display: none; margin-top: 16px; border-radius: 12px; padding: 18px; border: 1px solid; }
        #result-block.fight { border-color: rgba(255,58,58,0.4); background: var(--red-dim); }
        #result-block.no-fight { border-color: rgba(0,255,157,0.3); background: var(--green-dim); }
        .result-row { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
        .result-icon { width: 48px; height: 48px; border-radius: 12px; border: 1px solid; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .fight .result-icon { border-color: rgba(255,58,58,0.5); background: rgba(255,58,58,0.1); box-shadow: 0 0 20px var(--red-glow); }
        .no-fight .result-icon { border-color: rgba(0,255,157,0.4); background: rgba(0,255,157,0.08); box-shadow: 0 0 20px var(--green-glow); }
        .result-icon svg { width: 24px; height: 24px; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
        .fight .result-icon svg { stroke: var(--red); }
        .no-fight .result-icon svg { stroke: var(--green); }
        .result-label { font-family: "Space Mono", monospace; font-weight: 700; font-size: 18px; letter-spacing: 1px; text-transform: uppercase; line-height: 1.2; }
        .fight .result-label { color: var(--red); }
        .no-fight .result-label { color: var(--green); }
        .result-sub { font-size: 11px; color: var(--muted); margin-top: 3px; font-family: "Space Mono", monospace; }
        .stats-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .stat-box { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
        .stat-label { font-family: "Space Mono", monospace; font-size: 9px; letter-spacing: 1px; text-transform: uppercase; color: var(--muted); margin-bottom: 5px; }
        .stat-val { font-family: "Space Mono", monospace; font-weight: 700; font-size: 22px; }
        .fight .stat-val { color: var(--red); }
        .no-fight .stat-val { color: var(--green); }

        #graph-card {
            width: calc(100% - 32px);
            max-width: 520px;
            margin-top: 14px;
            background: var(--surface);
            border: 1px solid var(--border-bright);
            border-radius: var(--r);
            overflow: hidden;
        }
        .graph-header {
            border-bottom: 1px solid var(--border);
            padding: 14px 20px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .graph-title { font-family: "Space Mono", monospace; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); }
        .live-badge { display: flex; align-items: center; gap: 5px; font-family: "Space Mono", monospace; font-size: 9px; letter-spacing: 1px; color: var(--cyan); border: 1px solid var(--border-bright); padding: 3px 8px; border-radius: 4px; }
        .live-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--cyan); animation: blink 1s ease-in-out infinite; }
        .graph-inner { padding: 16px 20px 20px; }
        .graph-empty { height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }
        .graph-empty-line { width: 100%; height: 1px; background: repeating-linear-gradient(90deg, var(--border-bright) 0, var(--border-bright) 4px, transparent 4px, transparent 12px); }
        .graph-empty-txt { font-family: "Space Mono", monospace; font-size: 10px; color: var(--muted); letter-spacing: 1px; text-align: center; }
        canvas#chart { display: none; width: 100% !important; }
    </style>
</head>
<body>

<header>
    <div class="hx-mark">
        <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 2L14 5.5V10.5L8 14L2 10.5V5.5L8 2Z" stroke="#00c8ff" stroke-width="1.2"/>
            <circle cx="8" cy="8" r="2" fill="#00c8ff"/>
        </svg>
    </div>
    <div class="brand">Rivox</div>
    <div class="version">v2.0</div>
</header>

<div class="card">
    <div class="card-top">
        <div class="dot dot-r"></div>
        <div class="dot dot-y"></div>
        <div class="dot dot-g"></div>
        <div class="card-label">Input Module</div>
    </div>
    <div class="card-inner">
        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon-wrap">
                <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <div class="upload-title" id="uploadTitle">Tap to upload video</div>
            <div class="upload-sub">MP4 &middot; MOV &middot; AVI &middot; MKV</div>
        </div>
        <input type="file" id="fileInput" accept="video/*">
        <video id="preview" controls playsinline></video>

        <button class="btn" id="analyzeBtn" onclick="analyze()">&#9654; &nbsp; Run Analysis</button>

        <div id="loading">
            <div class="radar"></div>
            <div class="loading-txt">Scanning frames...</div>
        </div>

        <div id="result-block">
            <div class="result-row">
                <div class="result-icon">
                    <svg id="icon-fight" viewBox="0 0 24 24" style="display:none">
                        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                    <svg id="icon-nofight" viewBox="0 0 24 24" style="display:none">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                </div>
                <div>
                    <div class="result-label" id="resultLabel"></div>
                    <div class="result-sub" id="resultSub"></div>
                </div>
            </div>
            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-label">Confidence</div>
                    <div class="stat-val" id="statConf">—</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Peak Intensity</div>
                    <div class="stat-val" id="statInt">—</div>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="graph-card">
    <div class="graph-header">
        <div class="graph-title">Movement Intensity</div>
        <div class="live-badge" id="liveBadge" style="display:none">
            <div class="live-dot"></div>LIVE
        </div>
    </div>
    <div class="graph-inner">
        <div class="graph-empty" id="graphEmpty">
            <div class="graph-empty-line"></div>
            <div class="graph-empty-txt">Awaiting analysis...</div>
            <div class="graph-empty-line"></div>
        </div>
        <canvas id="chart" height="180"></canvas>
    </div>
</div>

<script>
let selectedFile = null, chartInstance = null;

document.getElementById("fileInput").addEventListener("change", function () {
    selectedFile = this.files[0];
    if (!selectedFile) return;
    document.getElementById("uploadTitle").textContent = selectedFile.name;
    document.getElementById("uploadZone").classList.add("has-file");
    const v = document.getElementById("preview");
    v.src = URL.createObjectURL(selectedFile);
    v.style.display = "block";
});

function analyze() {
    if (!selectedFile) { alert("Please select a video first."); return; }
    const btn = document.getElementById("analyzeBtn");
    btn.disabled = true;
    document.getElementById("loading").style.display = "block";
    document.getElementById("result-block").style.display = "none";

    const fd = new FormData();
    fd.append("file", selectedFile);

    fetch("/predict", { method: "POST", body: fd })
        .then(r => r.json())
        .then(data => {
            document.getElementById("loading").style.display = "none";
            btn.disabled = false;
            if (data.error) { alert("Error: " + data.error); return; }

            const isFight = data.prediction === "Fight";
            const rb = document.getElementById("result-block");
            rb.className = isFight ? "fight" : "no-fight";
            rb.style.display = "block";

            document.getElementById("icon-fight").style.display   = isFight ? "block" : "none";
            document.getElementById("icon-nofight").style.display = isFight ? "none"  : "block";
            document.getElementById("resultLabel").textContent = isFight ? "Fight Detected" : "No Fight";
            document.getElementById("resultSub").textContent   = isFight
                ? "Aggressive activity identified"
                : "No threatening activity detected";
            document.getElementById("statConf").textContent = (data.confidence * 100).toFixed(0) + "%";
            document.getElementById("statInt").textContent  = data.max_intensity.toFixed(1);

            renderGraph(data.intensity_data, isFight);
        })
        .catch(() => {
            document.getElementById("loading").style.display = "none";
            btn.disabled = false;
            alert("Something went wrong. Please try again.");
        });
}

function renderGraph(rawData, isFight) {
    const lineColor = isFight ? "#ff3a3a" : "#00ff9d";
    const fillColor = isFight ? "rgba(255,58,58,0.15)" : "rgba(0,255,157,0.12)";

    document.getElementById("graphEmpty").style.display = "none";
    const canvas = document.getElementById("chart");
    canvas.style.display = "block";

    if (chartInstance) chartInstance.destroy();

    const ctx = canvas.getContext("2d");
    const labels = rawData.map((_, i) => i + 1);
    const animData = new Array(rawData.length).fill(null);

    chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [
                { label: "Intensity", data: animData, borderColor: lineColor, backgroundColor: fillColor, borderWidth: 2, tension: 0.4, pointRadius: 0, fill: true },
                { label: "Threshold", data: labels.map(() => 6), borderColor: "rgba(0,200,255,0.4)", borderWidth: 1, borderDash: [5,5], pointRadius: 0, fill: false }
            ]
        },
        options: {
            responsive: true, animation: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#080f1a", borderColor: "rgba(0,200,255,0.2)", borderWidth: 1,
                    titleColor: "#3d5470", bodyColor: "#e2eaf5", padding: 10, displayColors: false,
                    callbacks: {
                        title: items => "Frame " + items[0].label,
                        label: item => item.dataset.label === "Intensity"
                            ? "Intensity: " + (item.raw !== null ? item.raw.toFixed(2) : "—")
                            : "Threshold: 6"
                    }
                }
            },
            scales: {
                x: { ticks: { color: "#3d5470", font: { family: "'Space Mono', monospace", size: 9 }, maxTicksLimit: 8 }, grid: { color: "rgba(0,200,255,0.05)" }, border: { color: "rgba(0,200,255,0.1)" } },
                y: { beginAtZero: true, ticks: { color: "#3d5470", font: { family: "'Space Mono', monospace", size: 9 } }, grid: { color: "rgba(0,200,255,0.05)" }, border: { color: "rgba(0,200,255,0.1)" } }
            }
        }
    });

    let i = 0;
    const badge = document.getElementById("liveBadge");
    badge.style.display = "flex";
    const iv = setInterval(() => {
        if (i >= rawData.length) { clearInterval(iv); badge.style.display = "none"; return; }
        chartInstance.data.datasets[0].data[i] = rawData[i];
        chartInstance.update("none");
        i++;
    }, 80);
}
</script>
</body>
</html>'''


@app.route("/")
def home():
    return HTML


@app.route("/upload")
def upload_page():
    return HTML


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty file name"})
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        result = detect_fight(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)