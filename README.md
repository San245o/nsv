#NSV Dashboard - NHAI national hackathon
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


python format.py
🚀 Step 2: Run the FastAPI Server
Install Python dependencies:
```bash
pip install -r requirements.txt
```
Start the server locally:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
Your API is now live at:
```bash
👉 http://localhost:8000
```

🌐 Step 3: Make it Public (Optional but Useful)
Use Cloudflare to expose your local FastAPI server:

Install Cloudflared:
```bash
npm install -g cloudflared
```
Tunnel your API:
```
cloudflared tunnel --url http://localhost:8000
```
🌍 You’ll get a public HTTPS link like:
```
https://fasttrimmer-nhai.trycloudflare.com
```

🐳 Optional: Docker Support
Build the Docker image:

docker build -t fasttrimmer .
Run the container:

docker run -p 8000:8000 fasttrimmer
🧪 API Usage
```
POST /trim
Returns a trimmed .mp4 video clip based on given coordinates.

✅ Request Format:

{
  "start_lat": 28.6129,
  "start_lon": 77.2295,
  "end_lat": 28.6200,
  "end_lon": 77.2340
}
🔁 Response:

{
  "video_url": "https://yourserver.com/output_trimmed.mp4",
}
```
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
```
🗃️ Sample CSV Output
Timestamp	          Latitude	Longitude	
2025-07-10 08:45	   28.6130	77.2300
2025-07-10 08:46	   28.6136	77.2306
```

🔭 Future Scope
AI detection of road distress (potholes, lane fading, debris)

Integration with live CCTV or drone feeds

Real-time alert system on map dashboards

NLP summarization of OCR content (e.g., “speed limit”, “diversion ahead”)

API integrations with NHAI or state transport dashboards
# 🌐 Frontend - Lightweight Web Dashboard for Smart Highway Monitoring

**🏁 Submission for NHAI Hackathon 2025 — Frontend Module**  
**🔗 Interfaces with FastTrimmer Backend**

---

### 🧠 Overview

The FastTrimmer Frontend is a lightweight, responsive dashboard built using pure HTML, CSS, and JavaScript. It provides an intuitive UI for viewing geo-tagged video insights extracted by the backend.

-   **`index.html`**: The main entry point featuring an interactive Leaflet.js map to visualize road segments, play geo-tagged videos, and view detailed segment data.
-   **`dashboard.html`**: A comprehensive analytics hub with interactive charts and tables to visualize road health, predict deterioration, and analyze infrastructure correlations.
-   **`report.html`**: A dynamic reporting page that generates filterable summaries, KPIs, and charts for creating detailed PDF reports.

### 🚀 Key Features

✅ **No frameworks** — built with HTML, CSS, & JS only for maximum speed and compatibility.  
✅ **Responsive Layout** using Flexbox and Media Queries for a seamless experience on desktop and mobile.  
✅ **Interactive Mapping** via Leaflet.js to visualize road segments and infrastructure.  
✅ **Integrated Video Playback** to view survey videos directly on the map.  
✅ **Advanced Analytics** with Plotly.js and Tabulator.js for 3D visualizations, statistical tables, and predictive modeling.  
✅ **Dynamic PDF Reporting** using jsPDF and html2canvas to export insights.  
✅ **Direct API Integration** with the backend using the native Fetch API.

### 🛠️ Tech Stack

| Layer         | Tech Used                               |
|---------------|-----------------------------------------|
| **UI/Frontend** | HTML, CSS, JavaScript (ES6+)            |
| **Mapping**     | Leaflet.js                              |
| **Charts**      | Plotly.js                               |
| **Tables**      | Tabulator.js                            |
| **Video**       | HTML5 `<video>` tag, Video.js           |
| **PDF Export**  | jsPDF + html2canvas                     |
| **API Interface**| Fetch API (AJAX)   
