import os
import cv2
import requests
from deepface import DeepFace

# Constants
URL = "https://thispersondoesnotexist.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MALE_DIR = "static/male"
FEMALE_DIR = "static/female"
TARGET_COUNT = 100

# Create directories if not exist
os.makedirs(MALE_DIR, exist_ok=True)
os.makedirs(FEMALE_DIR, exist_ok=True)

def get_age_range(age):
    if age < 20:
        return "<20"
    elif age >= 20 and age <= 28:
        return "in-range"
    else:
        return ">28"

def save_image(content, filename):
    with open(filename, "wb") as f:
        f.write(content)

def download_image():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            save_image(response.content, "person.jpg")
            return "person.jpg"
        else:
            print("Failed to download image.")
    except Exception as e:
        print("Error downloading image:", e)
    return None

def analyze_image(image_path):
    try:
        # Analyze the face using DeepFace
        result = DeepFace.analyze(img_path=image_path, actions=['age', 'gender'], enforce_detection=True)
        
        # If multiple faces detected, use the first one
        if isinstance(result, list):
            result = result[0]

        age = result['age']
        age_range = get_age_range(age)

        gender_dict = result['gender']
        if isinstance(gender_dict, dict):
            gender = max(gender_dict, key=gender_dict.get).lower()
        else:
            gender = gender_dict.lower()

        print(f"Age: {age}, Age Range: {age_range}, Gender: {gender}")
        return age_range, gender
    except Exception as e:
        print("Error analyzing image:", e)
        return None, None

# Main loop
male_count = len(os.listdir(MALE_DIR))
female_count = len(os.listdir(FEMALE_DIR))

while male_count < TARGET_COUNT or female_count < TARGET_COUNT:
    image_path = download_image()
    if not image_path:
        continue

    age_range, gender = analyze_image(image_path)

    if age_range == "in-range":
        if gender == "man" and male_count < TARGET_COUNT:
            save_path = os.path.join(MALE_DIR, f"image{male_count + 1}.jpg")
            os.rename("person.jpg", save_path)
            male_count += 1
            print(f"Saved to {save_path}")
        elif gender == "woman" and female_count < TARGET_COUNT:
            save_path = os.path.join(FEMALE_DIR, f"image{female_count + 1}.jpg")
            os.rename("person.jpg", save_path)
            female_count += 1
            print(f"Saved to {save_path}")
        else:
            os.remove("person.jpg")  # Clean up
    else:
        os.remove("person.jpg")  # Clean up

print("✅ Done! 10 images in each folder.")
