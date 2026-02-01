import cv2
import os
from preprocessing.video_input import get_video_stream
from preprocessing.image_preprocess import preprocess_image

def preprocess_video(video_path, output_path):
    cap = get_video_stream(video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 640))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed = preprocess_image(frame)
        processed = (processed * 255).astype("uint8")
        out.write(processed)

    cap.release()
    out.release()
