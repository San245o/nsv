# nsv
# 🛠️ FastTrimmer (Backend)

> 🚀 Smart Video Trimming & Geo-Temporal Analytics Engine for Highway Monitoring  
> 🏁 Submission for NHAI Hackathon 2025 — Backend Module

---

## 🧠 Overview

**FastTrimmer** is an intelligent backend system that processes highway surveillance videos to:
- Extract **GPS coordinates**, **timestamps**, and **OCR text** from each frame
- Enable **fast, location-based video trimming** through a REST API
- Deliver **actionable insights** in seconds for road incident detection, maintenance audits, and highway analytics

Built for scalable highway monitoring with NHAI use-cases in mind.

---

## 🎯 Key Features

✅ Frame-by-frame **OCR processing** (OpenCV + Tesseract)  
✅ Extraction of **Latitude, Longitude, and Timestamp** per frame  
✅ High-speed **video trimming** using FFmpeg  
✅ API-powered backend built with **FastAPI**  
✅ Public tunnel support using **Cloudflared**  
✅ Docker-compatible deployment  
✅ Ideal for **incident forensics, asset monitoring**, and **pothole detection**

---

## 🗂️ Project Structure
FastTrimmer/
├── format.py # Step-1: Video → CSV
├── app.py # Step-2: FastAPI backend
├── requirements.txt # Python dependencies
├── Dockerfile # Containerize the app
├── L2.mp4 # Your input video (place here)
└── output.csv # Auto-generated metadata file

---

## ⚙️ Installation & Setup

### 🧾 Prerequisites

- Python 3.8+
- FFmpeg installed and in PATH
- Node.js (for cloudflared tunnel)
- Docker (optional)

---

## 🎥 Step 1: Format the Video

Convert your video into structured `.csv` metadata using OCR and GPS overlays.

📍 **Ensure your `.mp4` video is in the same directory as `format.py`.**

```bash
python format.py
🚀 Step 2: Run the FastAPI Server
Install Python dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Start the server locally:

bash
Copy
Edit
uvicorn app:app --host 0.0.0.0 --port 8000
Your API is now live at:
👉 http://localhost:8000

🌐 Step 3: Make it Public (Optional but Useful)
Use Cloudflare to expose your local FastAPI server:

Install Cloudflared:

bash
Copy
Edit
npm install -g cloudflared
Tunnel your API:

bash
Copy
Edit
cloudflared tunnel --url http://localhost:8000
🌍 You’ll get a public HTTPS link like:
https://fasttrimmer-nhai.trycloudflare.com

🐳 Optional: Docker Support
Build the Docker image:

bash
Copy
Edit
docker build -t fasttrimmer .
Run the container:

bash
Copy
Edit
docker run -p 8000:8000 fasttrimmer
🧪 API Usage
POST /trim
Returns a trimmed .mp4 video clip based on given coordinates.

✅ Request Format:
json
Copy
Edit
{
  "start_lat": 28.6129,
  "start_lon": 77.2295,
  "end_lat": 28.6200,
  "end_lon": 77.2340
}
🔁 Response:
json
Copy
Edit
{
  "video_url": "https://yourserver.com/output_trimmed.mp4",
}
📁 The output video contains only the relevant geospatial segment from your full recording.

📈 Use Cases for NHAI
🚧 Road Quality Audits: Detect cracks, potholes, and surface damage

📍 Geo-tagged Event Extraction: Focus on high-incident zones

🧾 Compliance & Review: Pull video evidence for route inspections

🚨 Accident/Incident Forensics: Quickly review critical GPS zones

📊 Smart Infrastructure Monitoring

🛠️ Tech Stack
Layer	Tech Used
Backend	Python, FastAPI
Video Engine	FFmpeg
OCR Engine	Tesseract + OpenCV
API Tunnel	Cloudflared
Deployment	Docker, Uvicorn
Data Format	CSV

🗃️ Sample CSV Output
Timestamp	Latitude	Longitude	
2025-07-10 08:45	28.6130	77.2300
2025-07-10 08:46	28.6136	77.2306	

🔭 Future Scope
AI detection of road distress (potholes, lane fading, debris)

Integration with live CCTV or drone feeds

Real-time alert system on map dashboards

NLP summarization of OCR content (e.g., “speed limit”, “diversion ahead”)

API integrations with NHAI or state transport dashboards
