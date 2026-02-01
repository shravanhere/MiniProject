from flask import Flask, jsonify
from flask_cors import CORS
import os
import cv2

from preprocessing.image_input import load_image
from preprocessing.image_preprocess import preprocess_image
from preprocessing.video_preprocess import preprocess_video

# 1️⃣ Create Flask app FIRST
app = Flask(__name__)

# 2️⃣ Enable CORS AFTER app is created
CORS(app)

IMAGE_DIR = "data/images"
VIDEO_DIR = "data/videos"
OUT_IMG_DIR = "output/images"
OUT_VID_DIR = "output/videos"

@app.route("/process-all", methods=["POST"])
def process_all():
    processed_files = []

    # Process images
    for img in os.listdir(IMAGE_DIR):
        img_path = os.path.join(IMAGE_DIR, img)
        image = load_image(img_path)
        processed = preprocess_image(image)

        save_path = os.path.join(OUT_IMG_DIR, img)
        cv2.imwrite(save_path, (processed * 255).astype("uint8"))
        processed_files.append(save_path)

    # Process videos
    for vid in os.listdir(VIDEO_DIR):
        vid_path = os.path.join(VIDEO_DIR, vid)
        out_path = os.path.join(OUT_VID_DIR, vid)
        preprocess_video(vid_path, out_path)
        processed_files.append(out_path)

    return jsonify({
        "status": "Success",
        "processed_files": processed_files
    })

if __name__ == "__main__":
    app.run(debug=True)
