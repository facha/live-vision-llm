import cv2
import base64
import time
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8080/v1/chat/completions"

def capture_and_encode_frame(camera):
    ret, frame = camera.read()
    if not ret:
        logger.warning("Failed to capture frame")
        return None
    _, buffer = cv2.imencode('.jpg', frame)
    encoded = base64.b64encode(buffer).decode('utf-8')
    return encoded

def send_image_to_api(encoded_image):
    payload = {
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        message_text = data["choices"][0]["message"]["content"]
        logger.info(message_text.strip())
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format: {e}")

def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        logger.error("Could not open webcam")
        return

    try:
        while True:
            encoded_image = capture_and_encode_frame(camera)
            if encoded_image:
                send_image_to_api(encoded_image)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        camera.release()
        logger.info("Camera released.")

if __name__ == "__main__":
    main()

