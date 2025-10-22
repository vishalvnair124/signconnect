import spacy
import time
# Load English language model
nlp = spacy.load("en_core_web_sm")

# Words to remove in gloss (articles, auxiliary verbs, etc.)
REMOVE_WORDS = {"is", "am", "are", "was", "were", "the", "a", "an", "to"}

def text_to_gloss(text):
    doc = nlp(text.lower())
    gloss_words = []
    
    for token in doc:
        # Skip unwanted words
        if token.text in REMOVE_WORDS:
            continue
        # Lemmatize verbs/nouns (going → go, cars → car)
        gloss_words.append(token.lemma_.upper())
    
    # Optional: move time words to start
    time_words = [w for w in gloss_words if w in ["TODAY", "TOMORROW", "YESTERDAY"]]
    other_words = [w for w in gloss_words if w not in time_words]
    return " ".join(time_words + other_words)

# Test

star_time = time.process_time()
print(text_to_gloss("I am going to the market tomorrow"))
end_time = time.process_time()

print("time taken:", end_time - star_time)
