import speech_recognition as sr
# Initialize recognizer class
r = sr.Recognizer()

# Function to recognize speech using microphone
def recognize_speech():
    with sr.Microphone() as source:
        while True:
            audio = r.listen(source)

            try:
                text = r.recognize_google(audio)
                print("You said: ", text)
                if "quit" in text.lower():
                    print("Quitting...")
                    return 'quit', text # Exit the loop if "quit" is spoken
                elif "update" in text.lower():
                    print("Updating...")
                    return 'update', text
                elif "delete" in text.lower():
                    print("Deleting..")
                    return 'delete', text
                elif "create" or "creating" in text.lower():
                    print("creating...")
                    return 'create',text
                else:
                    return None,text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))




