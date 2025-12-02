import google.generativeai as genai

def get_ai_response(user_input):
    """
    This function gets a response from the Google Gemini AI model.
    """
    try:
        # PASTE YOUR SECRET API KEY HERE
        genai.configure(api_key="PASTE_YOURGENAI_API_KEY") 

        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        prompt = f"""
        You are Luna, a warm, empathetic, and knowledgeable menstrual health companion named Luna Sensai.
        Your personality is like a caring and supportive friend. You use emojis 🌸💖✨😊.
        You are talking to a user who needs support with their health, feelings, and well-being.
        Keep your answers concise and supportive.
        User's message: "{user_input}"
        Luna's response:
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "I'm having a little trouble connecting to my full knowledge right now, but I'm still here to listen. 💖"