import cv2
import numpy as np

def resize_image(image, target_size=(640, 640)):
    return cv2.resize(image, target_size)


def normalize_image(image):
    """
    Convert pixel values from [0,255] → [0,1]
    """
    return image.astype(np.float32) / 255.0


def remove_noise(image):
    """
    Apply Gaussian Blur to reduce noise
    """
    return cv2.GaussianBlur(image, (5, 5), 0)


def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def preprocess_image(image, grayscale=False):
    """
    Complete preprocessing pipeline
    """
    image = resize_image(image)
    image = remove_noise(image)

    if grayscale:
        image = convert_to_grayscale(image)

    image = normalize_image(image)
    return image
