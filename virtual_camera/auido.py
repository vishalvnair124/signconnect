import pyttsx3

# Essay text
essay_text = """
Good morning. I am a student. I am young, alive, and happy. I have a father, mother, brother, and sister. My family is good. My grandfather and grandmother are old, but they are healthy.

I live in a house in the city. The house has a bedroom, bathroom, kitchen, and library. I use a chair, table, bed, and lamp. I like books, paper, and pen. I have a laptop and computer. Technology is important for me.

I go to school and university. My teacher is kind. My friend is nice. We study science and art. We use clock, calendar, and book every day.

I like morning, afternoon, evening, and night. Summer, winter, spring, and monsoon are seasons. Friday, Saturday, Sunday, Monday, Tuesday, Wednesday, and Thursday are days.

I like sport. I play with a ball. I like bus, train, car, bicycle, and boat for transportation. The ground, road, and park are good places.

I see bird, dog, cat, horse, cow, and fish. They are animals. They live on land and in water. They are beautiful.

Life is good. I am alive, I am healthy, I am happy. Thank you.
"""

# Initialize TTS engine
engine = pyttsx3.init()

# Save to file
output_file = "essay_audio.mp3"
engine.save_to_file(essay_text, output_file)

# Run the speech engine
engine.runAndWait()

print(f"Audio file saved as {output_file}")
