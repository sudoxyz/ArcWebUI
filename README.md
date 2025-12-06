# GPU Stream Monitor

This project provides a real-time web-based interface to monitor GPU engine usage and client statistics using `intel_gpu_top`.

## Features
- Real-time GPU engine usage visualization.
- Client-specific GPU usage metrics.
- Dynamic updates using Server-Sent Events (SSE).
- Responsive UI built with Bootstrap.

## Requirements
- Python 3.x
- Flask
- `intel_gpu_top` (part of Intel GPU Tools)

## Setup
1. Install dependencies:
   ```bash
   pip install flask
   ```
2. Run the application:
   ```bash
   python3 app.py
   ```
3. Open your browser and navigate to `http://localhost:5000`.

## File Structure
- `app.py`: Main Flask application.
- `templates/index.html`: Frontend HTML with Bootstrap.

## Notes
- Ensure `intel_gpu_top` is installed and accessible in your PATH.