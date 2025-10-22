import spacy
import json
import time

nlp = spacy.load("en_core_web_sm", disable=["lemmatizer", "parser", "ner"])

with open("sign_dict.json", "r", encoding="utf-8") as f:
    GLOSS_DICT = {k.lower(): v for k, v in json.load(f).items()}

def text_to_gloss(text):
    # Process the text with spaCy
    doc = nlp(text)
    # Initialize a list to hold gloss words
    gloss_words = []
    # Iterate through each token in the processed document
    for token in doc:
        # Convert token to lowercase for dictionary lookup
        key = token.text.lower()
        # Check if the token is in the gloss dictionary
        if key in GLOSS_DICT:
            # If the word is in the dictionary, use its gloss
            gloss_words.append(GLOSS_DICT[key])
        else:
            # If not in dictionary, use the original token
            # gloss_words.append(token.text.upper())
            continue
    # Remove unwanted words
    return " ".join(gloss_words)

star_time = time.process_time()
print(text_to_gloss("I am going to the market tomorrow"))
end_time = time.process_time()
print("time taken:", end_time - star_time)