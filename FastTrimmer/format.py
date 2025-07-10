import cv2
import pytesseract
import re
import csv

def extract_lat_lon(text):
    # Normalize OCR noise
    text = text.replace('La’r', 'Lat').replace('Laf', 'Lat').replace('LC1f', 'Lat')
    text = text.replace('Lon', 'Lon').replace('Ion', 'Lon').replace('L0n', 'Lon')

    # Regex tolerant to optional colons and spacing
    lon_match = re.search(r'Lon[:\s]*([\d]+\.\d+)', text, re.IGNORECASE)
    lat_match = re.search(r'Lat[:\s]*([\d]+\.\d+)', text, re.IGNORECASE)

    lon = float(lon_match.group(1)) if lon_match else None
    lat = float(lat_match.group(1)) if lat_match else None
    return lon, lat

def ocr_on_video_frames(video_path, max_frames=4, output_csv="output.csv"):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file.")
        return

    frame_count = 0
    results = []

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            print("End of video or cannot read the frame.")
            break

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

        # --- Fix: Preprocessing to improve OCR for faint/dark digits ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.adaptiveThreshold(gray, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)

        # OCR
        text = pytesseract.image_to_string(enhanced, lang='eng')
        lon, lat = extract_lat_lon(text)

        print(f"\n--- Frame {frame_count + 1} ---")
        print(f"Timestamp: {timestamp:.2f}s")
        print(f"Lon: {lon}, Lat: {lat}")
        print(text.strip())

        results.append({
            "frame_no": frame_count + 1,
            "timestamp_sec": round(timestamp, 2),
            "lon": lon,
            "lat": lat
        })

        frame_count += 1

    cap.release()

    with open(output_csv, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["frame_no", "timestamp_sec", "lon", "lat"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Data saved to {output_csv}")

# Example usage
video_path = "L2.mp4"
ocr_on_video_frames(video_path)
