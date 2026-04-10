# Google Text to Speech API
from gtts import gTTS
import os

# Library to play an mp3 using python
from playsound import playsound


# The text that you want to convert to audio
dummy_text = "Ou suis-je ? Qui est là ? Qu'est-ce qu'il y a ?"

# Language in which you want to convert
LANGUANGE = 'fr'



def talk(text):
    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=text, lang=LANGUANGE, slow=False)

    # Saving the converted audio in a mp3 file
    myobj.save("speech.mp3")

    # Playing the converted file
    playsound('speech.mp3', True)

    os.remove("speech.mp3")