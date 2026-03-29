from flask import Flask, request, jsonify
import os
from fight_detect import detect_fight

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return upload_page()

@app.route("/upload")
def upload_page():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Rivox Fight Detection</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0f172a, #020617); color: white; text-align: center; padding-top: 40px; }
        .box { background: rgba(30, 41, 59, 0.9); padding: 30px; border-radius: 20px; width: 500px; margin: auto; box-shadow: 0px 0px 30px rgba(0,0,0,0.6); }
        .upload-area { border: 2px dashed #22c55e; padding: 30px; border-radius: 12px; cursor: pointer; margin-top: 20px; }
        video { margin-top: 15px; width: 100%; border-radius: 10px; display: none; }
        button { margin-top: 20px; padding: 12px; width: 100%; border-radius: 10px; border: none; background: #22c55e; color: white; font-weight: bold; cursor: pointer; }
        #loading { display: none; margin-top: 20px; }
        .spinner { border: 4px solid #1e293b; border-top: 4px solid #22c55e; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: auto; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        #result { margin-top: 20px; font-size: 18px; }
        canvas { margin-top: 25px; }
    </style>
</head>
<body>
<div class="box">
    <h2>🔥 Rivox Fight Detection</h2>
    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
        <p id="uploadText">📁 Click to upload video</p>
    </div>
    <input type="file" id="fileInput" accept="video/*" style="display:none">
    <video id="preview" controls></video>
    <button onclick="uploadFile()">Analyze Video</button>
    <div id="loading">
        <div class="spinner"></div>
        <p>Processing...</p>
    </div>
    <div id="result"></div>
    <canvas id="chart"></canvas>
</div>
<script>
let selectedFile = null;
let chartInstance = null;

document.getElementById("fileInput").addEventListener("change", function() {
    selectedFile = this.files[0];
    if (!selectedFile) return;
    document.getElementById("uploadText").innerText = "📁 " + selectedFile.name;
    let preview = document.getElementById("preview");
    preview.src = URL.createObjectURL(selectedFile);
    preview.style.display = "block";
});

function uploadFile() {
    if (!selectedFile) { alert("Please select a video file"); return; }
    let formData = new FormData();
    formData.append("file", selectedFile);
    document.getElementById("loading").style.display = "block";
    document.getElementById("result").innerHTML = "";

    fetch("/predict", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        document.getElementById("loading").style.display = "none";
        if (data.error) {
            document.getElementById("result").innerHTML = "<span style='color:red'>❌ " + data.error + "</span>";
            return;
        }
        document.getElementById("result").innerHTML =
            data.prediction === "Fight"
            ? "<span style='color:red'>🚨 Fight Detected</span><br>Confidence: " + data.confidence + "<br>Max Intensity: " + data.max_intensity
            : "<span style='color:lightgreen'>✅ No Fight</span><br>Confidence: " + data.confidence + "<br>Max Intensity: " + data.max_intensity;

        const ctx = document.getElementById("chart").getContext("2d");
        if (chartInstance) chartInstance.destroy();
        const threshold = 6;
        const labels = data.intensity_data.map((_, i) => "Frame " + (i + 1));
        let animatedData = new Array(data.intensity_data.length).fill(null);

        chartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    { label: "Movement Intensity", data: animatedData, borderWidth: 3, tension: 0.3, pointRadius: 3 },
                    { label: "Fight Threshold", data: labels.map(() => threshold), borderWidth: 2, borderDash: [6,6], pointRadius: 0 }
                ]
            },
            options: {
                responsive: true,
                animation: false,
                plugins: { legend: { labels: { color: "white" } } },
                scales: {
                    x: { title: { display:true, text:"Frames", color:"white" }, ticks:{color:"white", maxTicksLimit:6}, grid:{color:"rgba(255,255,255,0.1)"} },
                    y: { title: { display:true, text:"Movement Intensity", color:"white" }, ticks:{color:"white"}, grid:{color:"rgba(255,255,255,0.1)"}, beginAtZero:true }
                }
            }
        });

        let i = 0;
        let interval = setInterval(() => {
            if (i >= data.intensity_data.length) { clearInterval(interval); return; }
            chartInstance.data.datasets[0].data[i] = data.intensity_data[i];
            chartInstance.update();
            i++;
        }, 100);
    })
    .catch(() => {
        document.getElementById("loading").style.display = "none";
        document.getElementById("result").innerHTML = "<span style='color:red'>❌ Error occurred</span>";
    });
}
</script>
</body>
</html>
'''

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