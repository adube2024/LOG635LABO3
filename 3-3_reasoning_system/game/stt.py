import speech_recognition as sr


def listen():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    
        # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = r.recognize_google(audio, language='fr-FR')
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["success"] = False
        response["error"] = "Unable to recognize speech"

    return response


def hear_response():
    heard = listen()
    if not heard["success"]:
        return None
    
    response = heard["transcription"].strip()
    words = response.split()

    characters = ("mutarde","white", "scarlett", "plum", "green", "orchid", "black", "violet", "peacock")
    for i in range(len(words)):
        if words[i].lower() in characters:
            words[i] = words[i].capitalize()

        elif words[i].isdigit():
            words[i] = words[i] + "h"
        
    response = " ".join(words)
    
    return response