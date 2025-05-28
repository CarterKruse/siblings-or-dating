import os
import pandas as pd
from deepface import DeepFace
from tqdm import tqdm

def analyze_race(folder_path):
    data = []

    for file_name in tqdm(os.listdir(folder_path)):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, file_name)
            try:
                result = DeepFace.analyze(img_path=file_path, actions=['race'], enforce_detection=False)
                dominant_race = result[0]['dominant_race']
                data.append({"image": file_name, "race": dominant_race})
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
                data.append({"image": file_name, "race": "error"})

    return pd.DataFrame(data)

# Analyze "static/female"
female_folder = "static/female"
female_df = analyze_race(female_folder)
female_df.to_csv("female_race.csv", index=False)

# Analyze "static/male"
male_folder = "static/male"
male_df = analyze_race(male_folder)
male_df.to_csv("male_race.csv", index=False)

print("Race detection complete. CSV files saved.")