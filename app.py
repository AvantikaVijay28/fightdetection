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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>Rivox — Fight Detection</title>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg: #080c10;
            --surface: #0e1419;
            --border: rgba(255,255,255,0.07);
            --accent: #e8ff47;
            --accent-dim: rgba(232,255,71,0.12);
            --red: #ff4545;
            --red-dim: rgba(255,69,69,0.12);
            --green: #3dffa0;
            --green-dim: rgba(61,255,160,0.12);
            --text: #f0f4f8;
            --muted: #5a6a7a;
            --card-radius: 20px;
        }

        html, body {
            height: 100%;
            background: var(--bg);
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100dvh;
            padding: 0 0 40px;
        }

        /* ── Header ── */
        header {
            width: 100%;
            padding: 20px 24px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid var(--border);
        }

        .logo-dot {
            width: 10px; height: 10px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 10px var(--accent);
            flex-shrink: 0;
        }

        .logo-text {
            font-family: 'Syne', sans-serif;
            font-weight: 800;
            font-size: 18px;
            letter-spacing: -0.3px;
            color: var(--text);
        }

        .logo-text span { color: var(--accent); }

        .badge {
            margin-left: auto;
            font-size: 11px;
            font-weight: 500;
            color: var(--muted);
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            padding: 4px 10px;
            border-radius: 20px;
            letter-spacing: 0.5px;
        }

        /* ── Main card ── */
        .card {
            width: calc(100% - 32px);
            max-width: 480px;
            margin-top: 28px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--card-radius);
            overflow: hidden;
        }

        .card-inner { padding: 24px; }

        .section-label {
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 14px;
        }

        /* ── Upload zone ── */
        .upload-zone {
            border: 1.5px dashed rgba(232,255,71,0.3);
            border-radius: 14px;
            padding: 32px 20px;
            text-align: center;
            cursor: pointer;
            transition: border-color 0.2s, background 0.2s;
            position: relative;
            background: rgba(232,255,71,0.03);
        }

        .upload-zone:active { background: var(--accent-dim); }
        .upload-zone.has-file { border-color: rgba(232,255,71,0.6); }

        .upload-icon {
            font-size: 32px;
            margin-bottom: 10px;
            display: block;
        }

        .upload-title {
            font-family: 'Syne', sans-serif;
            font-weight: 600;
            font-size: 15px;
            color: var(--text);
            margin-bottom: 4px;
        }

        .upload-sub {
            font-size: 12px;
            color: var(--muted);
        }

        #fileInput { display: none; }

        /* ── Video preview ── */
        #preview {
            display: none;
            width: 100%;
            border-radius: 12px;
            margin-top: 16px;
            max-height: 220px;
            object-fit: cover;
            background: #000;
        }

        /* ── Divider ── */
        .divider {
            height: 1px;
            background: var(--border);
            margin: 24px 0;
        }

        /* ── Analyze button ── */
        .btn-analyze {
            width: 100%;
            padding: 16px;
            border-radius: 14px;
            border: none;
            background: var(--accent);
            color: #080c10;
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.3px;
            cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
            -webkit-tap-highlight-color: transparent;
        }

        .btn-analyze:active { transform: scale(0.98); opacity: 0.9; }
        .btn-analyze:disabled { opacity: 0.4; cursor: not-allowed; }

        /* ── Loading ── */
        #loading {
            display: none;
            text-align: center;
            padding: 28px 0 8px;
        }

        .spinner-ring {
            width: 40px; height: 40px;
            border: 3px solid rgba(232,255,71,0.15);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 14px;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .loading-text {
            font-size: 13px;
            color: var(--muted);
            letter-spacing: 0.3px;
        }

        /* ── Result ── */
        #result-card {
            display: none;
            margin-top: 20px;
            border-radius: 14px;
            padding: 20px;
            border: 1px solid var(--border);
        }

        #result-card.fight {
            background: var(--red-dim);
            border-color: rgba(255,69,69,0.25);
        }

        #result-card.no-fight {
            background: var(--green-dim);
            border-color: rgba(61,255,160,0.25);
        }

        .result-emoji { font-size: 28px; margin-bottom: 8px; display: block; }

        .result-label {
            font-family: 'Syne', sans-serif;
            font-weight: 800;
            font-size: 22px;
            margin-bottom: 12px;
        }

        .result-label.fight { color: var(--red); }
        .result-label.no-fight { color: var(--green); }

        .result-stats {
            display: flex;
            gap: 12px;
        }

        .stat {
            flex: 1;
            background: rgba(255,255,255,0.04);
            border-radius: 10px;
            padding: 12px;
        }

        .stat-label {
            font-size: 10px;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 4px;
        }

        .stat-value {
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 18px;
            color: var(--text);
        }

        /* ── Chart card ── */
        #chart-card {
            display: none;
            width: calc(100% - 32px);
            max-width: 480px;
            margin-top: 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--card-radius);
            padding: 24px;
        }

        .chart-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .chart-title {
            font-family: 'Syne', sans-serif;
            font-weight: 700;
            font-size: 14px;
            color: var(--text);
        }

        .live-pill {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
            color: var(--accent);
            background: var(--accent-dim);
            border-radius: 20px;
            padding: 4px 10px;
        }

        .live-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: var(--accent);
            animation: pulse 1s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        canvas { width: 100% !important; }
    </style>
</head>
<body>

<header>
    <div class="logo-dot"></div>
    <div class="logo-text">Rivo<span>x</span></div>
    <div class="badge">FIGHT DETECT</div>
</header>

<div class="card">
    <div class="card-inner">

        <div class="section-label">Upload Video</div>

        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
            <span class="upload-icon">🎬</span>
            <div class="upload-title" id="uploadTitle">Tap to select video</div>
            <div class="upload-sub">MP4, MOV, AVI supported</div>
        </div>
        <input type="file" id="fileInput" accept="video/*">

        <video id="preview" controls playsinline></video>

        <div class="divider"></div>

        <button class="btn-analyze" onclick="uploadFile()" id="analyzeBtn">Analyze Video</button>

        <div id="loading">
            <div class="spinner-ring"></div>
            <div class="loading-text">Analyzing movement patterns...</div>
        </div>

        <div id="result-card">
            <span class="result-emoji" id="resultEmoji"></span>
            <div class="result-label" id="resultLabel"></div>
            <div class="result-stats">
                <div class="stat">
                    <div class="stat-label">Confidence</div>
                    <div class="stat-value" id="statConfidence">—</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Max Intensity</div>
                    <div class="stat-value" id="statIntensity">—</div>
                </div>
            </div>
        </div>

    </div>
</div>

<div id="chart-card">
    <div class="chart-header">
        <div class="chart-title">Movement Intensity</div>
        <div class="live-pill" id="livePill">
            <div class="live-dot"></div>
            LIVE
        </div>
    </div>
    <canvas id="chart" height="180"></canvas>
</div>

<script>
let selectedFile = null;
let chartInstance = null;

document.getElementById("fileInput").addEventListener("change", function () {
    selectedFile = this.files[0];
    if (!selectedFile) return;
    document.getElementById("uploadTitle").innerText = selectedFile.name;
    document.getElementById("uploadZone").classList.add("has-file");
    const preview = document.getElementById("preview");
    preview.src = URL.createObjectURL(selectedFile);
    preview.style.display = "block";
});

function uploadFile() {
    if (!selectedFile) { alert("Please select a video file first."); return; }

    const btn = document.getElementById("analyzeBtn");
    btn.disabled = true;

    document.getElementById("loading").style.display = "block";
    document.getElementById("result-card").style.display = "none";
    document.getElementById("chart-card").style.display = "none";

    const formData = new FormData();
    formData.append("file", selectedFile);

    fetch("/predict", { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            document.getElementById("loading").style.display = "none";
            btn.disabled = false;

            if (data.error) {
                alert("Error: " + data.error);
                return;
            }

            const isFight = data.prediction === "Fight";
            const resultCard = document.getElementById("result-card");
            resultCard.className = isFight ? "fight" : "no-fight";
            resultCard.style.display = "block";

            document.getElementById("resultEmoji").innerText = isFight ? "🚨" : "✅";
            const label = document.getElementById("resultLabel");
            label.innerText = isFight ? "Fight Detected" : "No Fight";
            label.className = "result-label " + (isFight ? "fight" : "no-fight");

            document.getElementById("statConfidence").innerText =
                (data.confidence * 100).toFixed(0) + "%";
            document.getElementById("statIntensity").innerText =
                data.max_intensity.toFixed(1);

            // ── Animated chart ──
            const chartCard = document.getElementById("chart-card");
            chartCard.style.display = "block";

            const threshold = 6;
            const rawData = data.intensity_data;
            const labels = rawData.map((_, i) => i + 1);

            if (chartInstance) chartInstance.destroy();

            const ctx = document.getElementById("chart").getContext("2d");

            // Gradient fill
            const gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, isFight ? "rgba(255,69,69,0.35)" : "rgba(61,255,160,0.35)");
            gradient.addColorStop(1, "rgba(0,0,0,0)");

            const lineColor = isFight ? "#ff4545" : "#3dffa0";

            chartInstance = new Chart(ctx, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Intensity",
                            data: new Array(rawData.length).fill(null),
                            borderColor: lineColor,
                            backgroundColor: gradient,
                            borderWidth: 2.5,
                            tension: 0.4,
                            pointRadius: 0,
                            fill: true,
                        },
                        {
                            label: "Threshold",
                            data: labels.map(() => threshold),
                            borderColor: "rgba(232,255,71,0.5)",
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            pointRadius: 0,
                            fill: false,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    animation: false,
                    interaction: { mode: "index", intersect: false },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: "#0e1419",
                            borderColor: "rgba(255,255,255,0.1)",
                            borderWidth: 1,
                            titleColor: "#5a6a7a",
                            bodyColor: "#f0f4f8",
                            padding: 10,
                        }
                    },
                    scales: {
                        x: {
                            title: { display: false },
                            ticks: { color: "#5a6a7a", font: { size: 10 }, maxTicksLimit: 8 },
                            grid: { color: "rgba(255,255,255,0.04)" }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: "#5a6a7a", font: { size: 10 } },
                            grid: { color: "rgba(255,255,255,0.04)" }
                        }
                    }
                }
            });

            // Animate data point by point
            let i = 0;
            const livePill = document.getElementById("livePill");
            const interval = setInterval(() => {
                if (i >= rawData.length) {
                    clearInterval(interval);
                    livePill.style.display = "none";
                    return;
                }
                chartInstance.data.datasets[0].data[i] = rawData[i];
                chartInstance.update("none");
                i++;
            }, 80);
        })
        .catch(() => {
            document.getElementById("loading").style.display = "none";
            btn.disabled = false;
            alert("Something went wrong. Please try again.");
        });
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