import sys
import json
import threading
import time
import subprocess
from flask import Flask, render_template, Response, stream_with_context

app = Flask(__name__)

current_gpu_stats = {
    "video0": 0, "video1": 0, "render": 0, 
    "blitter": 0, "videoenhance0": 0, "videoenhance1": 0, 
    "unknown": 0
}

current_clients = []
current_client_stats = {}

def parse_gpu_stream():
    global current_gpu_stats, current_clients, current_client_stats
    buffer = ""
    brace_balance = 0

    process = subprocess.Popen(
        ["intel_gpu_top", "-J"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in process.stdout:
        stripped = line.strip()

        if not stripped or stripped in ['[', ']']:
            continue

        buffer += line
        brace_balance += line.count('{')
        brace_balance -= line.count('}')

        if brace_balance == 0 and buffer.strip():
            try:
                current_clients = []
                json_str = buffer.strip().rstrip(',')
                data = json.loads(json_str)
                
                engines = data.get('engines', {})
                clients = data.get('clients', {})

                current_clients.clear()
                current_clients.extend(clients.keys())

                current_client_stats = {client: stats for client, stats in current_client_stats.items() if client in current_clients}

                for client, stats in clients.items():
                    engine_classes = stats.get('engine-classes', {})

                    video = engine_classes.get('Video', {}).get('busy', 0)
                    videoenhance = engine_classes.get('VideoEnhance', {}).get('busy', 0)
                    render = engine_classes.get('Render/3D', {}).get('busy', 0)
                    blitter = engine_classes.get('Blitter', {}).get('busy', 0)
                    unknown = engine_classes.get('[unknown]', {}).get('busy', 0)
                    

                    current_client_stats[client] = {
                        "name": stats.get('name', ''),
                        "pid": stats.get('pid', ''),
                        "Video": int(float(video)),
                        "Video Enhance": int(float(videoenhance)),
                        "Render": int(float(render)),
                        "Blitter": int(float(blitter)),
                        "Unknown": int(float(unknown))
                    }
                    
                current_gpu_stats = {
                    "video0": int(engines.get('Video/0', {}).get('busy', 0)),
                    "video1": int(engines.get('Video/1', {}).get('busy', 0)),
                    "render": int(engines.get('Render/3D/0', {}).get('busy', 0)),
                    "blitter": int(engines.get('Blitter/0', {}).get('busy', 0)),
                    "videoenhance0": int(engines.get('VideoEnhance/0', {}).get('busy', 0)),
                    "videoenhance1": int(engines.get('VideoEnhance/1', {}).get('busy', 0)),
                    "unknown": int(engines.get('Unknown/0', {}).get('busy', 0))
                }

            except json.JSONDecodeError as e:
                sys.stderr.write(f"Error parsing chunk: {e}\n")
            
            buffer = ""
            brace_balance = 0
            current_clients = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream-data')
def stream_data():
    def generate():
        while True:
            json_data = json.dumps(current_gpu_stats)
            yield f"data: {json_data}\n\n"
            time.sleep(0.5) 

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/client-stats')
def client_stats():
    def generate():
        while True:
            json_data = json.dumps(current_client_stats)
            yield f"data: {json_data}\n\n"
            time.sleep(0.5)  

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    t = threading.Thread(target=parse_gpu_stream, daemon=True)
    t.start()

    print("Starting WebUI on http://localhost:5000")
    print("Waiting for JSON input on stdin...")
    
    app.run(host='0.0.0.0', port=5000, debug=False)