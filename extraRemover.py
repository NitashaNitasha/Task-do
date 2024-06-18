import genai

GENAI_API_KEY = 'AIzaSyAwgNVpn_iz6tMhxXb-hl1OUj7aqRvI1fc'

def remove_redundant_words(sentence):
    try:
        genai.
        model = genai.GenerativeModel(model_name="gemini-1.0-pro")

        # Start a chat session
        convo = model.start_chat(history=[])

        # Send the sentence to Gemini for processing
        convo.send_message(sentence)

        # Retrieve the filtered response
        cleaned_sentence = convo.remove_redundant(convo.last.text)

        return cleaned_sentence

    except Exception as e:
        print(f"Error interacting with Gemini: {e}")
        return None

# Example usage:
input_sentence = "This is a test sentence with redundant words like like and and"
cleaned_sentence = remove_redundant_words(input_sentence)

if cleaned_sentence:
    print("Original Sentence:", input_sentence)
    print("Cleaned Sentence:", cleaned_sentence)
else:
    print("Failed to process sentence.")
