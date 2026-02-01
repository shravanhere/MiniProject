import cv2

def load_image(image_path):
    
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image not found or invalid image format")

    return image


def capture_from_camera(camera_id=0):
    
    cap = cv2.VideoCapture(camera_id)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture image from camera")

    return frame
