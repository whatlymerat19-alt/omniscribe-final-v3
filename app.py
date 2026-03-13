import os
import requests
import base64
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Configuration
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb" # ID de la voix de Marcus

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniScribe Master v3</title>
    <style>
        body { background: #050505; color: #e0e0e0; font-family: 'Courier New', monospace; text-align: center; padding: 20px; }
        h1 { color: #8b0000; text-shadow: 2px 2px 5px #000; letter-spacing: 3px; }
        textarea { width: 100%; height: 100px; background: #111; color: #ff0000; border: 1px solid #440000; border-radius: 8px; padding: 10px; font-family: monospace; }
        .preview-box { width: 100%; height: 300px; background: #000; border: 2px solid #1a1a1a; margin-top: 20px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
        .btn-gen { width: 100%; padding: 15px; background: #600; color: #fff; border: none; border-radius: 5px; font-weight: bold; margin-top: 15px; cursor: pointer; border-bottom: 3px solid #300; }
        .btn-gen:active { border-bottom: none; transform: translateY(2px); }
        #status { font-size: 12px; color: #555; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>OMNISCRIBE MASTER</h1>
    <textarea id="prompt" placeholder="Écris ton script ici..."></textarea>
    <button class="btn-gen" id="genBtn" onclick="talk()">PARLER AVEC MARCUS</button>
    <div id="status">Système prêt.</div>
    <div class="preview-box" id="vView">
        <audio id="audioPlayer" controls style="display:none; width:90%;"></audio>
        <span id="placeholder">MARCUS EN ATTENTE</span>
    </div>

    <script>
        async function talk() {
            const text = document.getElementById('prompt').value;
            const btn = document.getElementById('genBtn');
            const status = document.getElementById('status');
            const player = document.getElementById('audioPlayer');
            
            if(!text) return alert("Le script est vide.");
            
            btn.disabled = true;
            btn.innerText = "MARCUS RÉFLÉCHIT...";
            status.innerText = "Connexion sécurisée en cours...";

            try {
                const response = await fetch('/speak', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });

                const data = await response.json();

                if(response.ok && data.audio) {
                    const blob = await (await fetch("data:audio/mpeg;base64," + data.audio)).blob();
                    player.src = URL.createObjectURL(blob);
                    player.style.display = "block";
                    document.getElementById('placeholder').style.display = "none";
                    player.play();
                    status.innerText = "Transmission terminée.";
                } else {
                    alert("Erreur : " + (data.details || "Vérifie ta clé sur Render"));
                    status.innerText = "Échec de la connexion.";
                }
            } catch (e) {
                status.innerText = "Erreur réseau.";
            }
            btn.disabled = false;
            btn.innerText = "PARLER AVEC MARCUS";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_CONTENT

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get("text")
    
    if not API_KEY:
        return jsonify({"error": "Config Error", "details": "ELEVENLABS_API_KEY non trouvée"}), 500

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.7}
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            audio_b64 = base64.b64encode(res.content).decode('utf-8')
            return jsonify({"audio": audio_b64})
        return jsonify({"error": "API Error", "details": res.text}), res.status_code
    except Exception as e:
        return jsonify({"error": "Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
