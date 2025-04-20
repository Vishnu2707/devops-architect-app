def clean_output(text):
    stop_phrases = [
        "Let me know when you're ready",
        "I'm here to help",
        "What do you say?",
        "Please respond",
    ]
    for phrase in stop_phrases:
        if phrase in text:
            return text.split(phrase)[0].strip()
    return text.strip()

