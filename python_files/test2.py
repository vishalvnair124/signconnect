import os
import json

# Path to your directory containing the .csv files
dir_path = r"D:\signcsv"

gloss_dict = {}
for fname in os.listdir(dir_path):
    if fname.lower().endswith('.csv'):
        word = fname[:-4]  # Remove the ".csv"
        gloss = word.upper()
        gloss_dict[word.lower()] = gloss

# Write the dictionary to sign_dict.json
with open("sign_dict.json", "w", encoding="utf-8") as f:
    json.dump(gloss_dict, f, ensure_ascii=False, indent=2)

print(f"Added {len(gloss_dict)} words to sign_dict.json")
