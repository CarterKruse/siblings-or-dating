import os
import cv2
import face_recognition
from PIL import Image

def crop_and_resize_face(image, size=(1024, 1024), padding_ratio=0.4):
    h, w, _ = image.shape
    face_locations = face_recognition.face_locations(image)
    
    if not face_locations:
        return None  # No face found

    largest_face = max(face_locations, key=lambda rect: (rect[2] - rect[0]) * (rect[1] - rect[3]))
    top, right, bottom, left = largest_face

    face_height = bottom - top
    face_width = right - left
    pad_h = int(padding_ratio * face_height)
    pad_w = int(padding_ratio * face_width)

    # Extend box and clamp to image bounds
    top = max(0, top - pad_h)
    bottom = min(h, bottom + pad_h)
    left = max(0, left - pad_w)
    right = min(w, right + pad_w)

    cropped = image[top:bottom, left:right]
    pil_image = Image.fromarray(cropped)
    resized_image = pil_image.resize(size, Image.LANCZOS)

    return resized_image

def process_folder(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    supported_exts = (".jpg", ".jpeg", ".png")
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_exts):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                image = face_recognition.load_image_file(input_path)
                result = crop_and_resize_face(image)
                if result:
                    result.save(output_path)
                    print(f"✅ Saved: {output_path}")
                else:
                    print(f"❌ No face found: {filename}")
            except Exception as e:
                print(f"⚠️ Error processing {filename}: {e}")

# Example usage
process_folder("original", "new")
