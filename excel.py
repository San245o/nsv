import pandas as pd
import json
import time
import orjson

# --- Configuration ---
file_path = r"resources\Comparison Delhi Vadodara Pkg 9 (Road Signage).xlsx"
output_js_path = "segments.js"
start = time.time()

# Mapping of lanes to column index numbers
column_mapping = {
    "L1": {
        "start_lat": 5,   "start_lon": 6,   "end_lat": 7,   "end_lon": 8,
        "roughness": 39,  "rutting": 48,    "cracking": 57, "ravelling": 66
    },
    "L2": {
        "start_lat": 9,   "start_lon":10,   "end_lat":11,   "end_lon":12,
        "roughness": 40,  "rutting": 49,    "cracking": 57, "ravelling": 67
    },
    "L3": {
        "start_lat":13,   "start_lon":14,   "end_lat":15,   "end_lon":16,
        "roughness": 41,  "rutting": 50,    "cracking": 58, "ravelling": 68
    },
    "L4": {
        "start_lat":17,   "start_lon":18,   "end_lat":19,   "end_lon":20,
        "roughness": 42,  "rutting": 51,    "cracking": 59, "ravelling": 69
    },
    "R1": {
        "start_lat":21,   "start_lon":22,   "end_lat":23,   "end_lon":24,
        "roughness": 43,  "rutting": 52,    "cracking": 60, "ravelling": 70
    },
    "R2": {
        "start_lat":25,   "start_lon":26,   "end_lat":27,   "end_lon":28,
        "roughness": 44,  "rutting": 53,    "cracking": 61, "ravelling": 71
    },
    "R3": {
        "start_lat":29,   "start_lon":30,   "end_lat":31,   "end_lon":32,
        "roughness": 45,  "rutting": 54,    "cracking": 62, "ravelling": 72
    },
    "R4": {
        "start_lat":33,   "start_lon":34,   "end_lat":35,   "end_lon":36,
        "roughness": 46,  "rutting": 55,    "cracking": 63, "ravelling": 73
    },
}

# --- Data Processing ---
df = pd.read_excel(file_path, header=2)

all_segments = []

for lane, idxs in column_mapping.items():
    # Extract relevant columns including chainage (1,2) and structure (4)
    lane_df = df.iloc[:, [
        1, 2,  # start_chainage, end_chainage
        4,     # Structure Details (Column E)
        idxs["start_lat"], idxs["start_lon"],
        idxs["end_lat"], idxs["end_lon"],
        idxs["roughness"], idxs["rutting"],
        idxs["cracking"], idxs["ravelling"]
    ]].copy()

    lane_df.columns = [
        "start_chainage", "end_chainage",
        "structure",
        "start_lat", "start_lon",
        "end_lat", "end_lon",
        "roughness", "rutting",
        "cracking", "ravelling"
    ]

    lane_df["lane"] = lane
    
    # If structure is null, it's a normal road
    lane_df["structure"] = lane_df["structure"].fillna("Normal Road")

    if lane in {"R1", "R2", "R3", "R4"}:
        lane_df[["start_chainage", "end_chainage"]] = lane_df[["end_chainage", "start_chainage"]]
    
    numeric_cols = [
        "start_chainage", "end_chainage",
        "start_lat", "start_lon", "end_lat", "end_lon",
        "roughness", "rutting", "cracking", "ravelling"
    ]
    lane_df[numeric_cols] = lane_df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    lane_df.dropna(subset=["start_lat", "start_lon", "end_lat", "end_lon"], inplace=True)

    lane_df["start"] = lane_df[["start_lat", "start_lon"]].values.tolist()
    lane_df["end"] = lane_df[["end_lat", "end_lon"]].values.tolist()

    final_cols = [
        "lane", "start", "end",
        "start_chainage", "end_chainage",
        "structure", "roughness", "rutting", "cracking", "ravelling"
    ]

    all_segments.extend(lane_df[final_cols].to_dict("records"))

# --- Write to JS file ---
with open(output_js_path, "wb") as f:
    f.write(b"const segments = ")
    f.write(orjson.dumps(all_segments))
    f.write(b";")

end = time.time()
print(f"✅ {output_js_path} generated successfully in {end-start:.2f} seconds.")
