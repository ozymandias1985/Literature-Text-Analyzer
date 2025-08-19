import openai
import os
from dotenv import load_dotenv
from textblob import TextBlob
from PyPDF2 import PdfReader 


#Conf
#Load API key securely from .env

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("   Error: API key missing. Please make sure your .env file is correctly set up.")
    print("   It should be in the same directory as this script and contain:")
    print("   OPENAI_API_KEY='your_actual_openai_api_key_here'")
    exit(1) # Exit if API key is not found

# Initialize the OpenAI client with the API key

client = openai.OpenAI(api_key=api_key)


#Hardcoded MLA citation for "Narrative of the Life of Frederick Douglass"
MLA_CITATION = (
    "Douglass, Frederick. *Narrative of the Life of Frederick Douglass, an American Slave.* "
    "Anti-Slavery Office, 1845."
)

# function for  pdf handling file path
def load_pdf_text(file_path):
    """
    Loads text content from a specified PDF file.
    """
    if not os.path.exists(file_path):
        print(f"  Error: PDF file not found at: {file_path}")
        print("   Please ensure the path is correct and the file exists.")
        exit(1) # Exit if the PDF is not found
    
    print(f"Attempting to load text from: {file_path}")
    try:
        reader = PdfReader(file_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            # Extract text and add a new_line to separate content from different pages
            page_text = page.extract_text()
            if page_text: # Only add if text was actually extracted
                text += page_text + "\n" 
        print("✅ PDF text loaded successfully.")
        return text
    except Exception as e:
        print(f"\n Error reading PDF file: {e}")
        print("   Please ensure the PDF is not corrupted and is readable.")
        exit(1)

#user inp
def get_user_quote():
    """
    Prompts the user to enter a quote and returns the input.
    """
    print("\n--- Quote Input ---")
    print("📜 Please enter a quote from 'Narrative of the Life of Frederick Douglass':")
    quote = input(">>> ").strip() 
    if not quote:
        print("⚠️ No quote entered. Please try again.")
        return get_user_quote() # Recursively ask again if input is empty
    return quote

#OpenAI Integration 
def explain_quote_with_gpt(quote):
    """
    Uses OpenAI's GPT-4.0 Mini - o - model to explain the given quote.
    Includes error handling for API calls.
    Updated to use OpenAI library v1.0.0+ syntax.
    """
    print("\n--- OpenAI Explanation ---")
    print("🔍 Generating explanation via OpenAI (this might take a moment)...")
    try:
        # Use the new client.chat.completions.create method
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful literature assistant, specializing in 19th-century American literature. Explain quotes clearly and concisely."},
                {"role": "user", "content": f"Explain this quote from Frederick Douglass's 'Narrative' in simple terms, focusing on its meaning and significance: \"{quote}\""}
            ],
            temperature=0.7, # Controls randomness; lower for more focused answers
            max_tokens=300 # Limit response length
        )
        # Access the content from the new response object structure
        explanation = response.choices[0].message.content.strip()
        print("✅ Explanation received from OpenAI.")
        return explanation
    except openai.APIStatusError as e: # Catch API-specific errors
        print(f"\n OpenAI API Error (Status Code: {e.status_code}): {e.response}")
        if e.status_code == 401:
            print("   This is likely an Authentication Error: Your API key is invalid or expired.")
            print("   Please double-check your OPENAI_API_KEY in the .env file.")
        return "Could not generate explanation due to an API error."
    except openai.APITimeoutError:
        print("\n OpenAI API Timeout Error: The request took too long to respond.")
        return "Could not generate explanation due to a timeout."
    except Exception as e:
        print(f"\n An unexpected error occurred during OpenAI call: {e}")
        return "Could not generate explanation due to an unexpected error."

#NLP Diagnostics ratings
def analyze_quote_nlp(quote):
    """
    Performs sentiment analysis on the quote using TextBlob to determine its tone.
    """
    print("\n--- NLP Diagnostics ---")
    print(" Running NLP diagnostics with TextBlob...")
    blob = TextBlob(quote)
    sentiment = blob.sentiment

    print("\n  Sentiment Analysis Results:")
    # Polarity ranges from -1 (negative) to +1 (positive)
    print(f"- Polarity (Tone): {sentiment.polarity:.2f} (closer to -1 is negative, +1 is positive, 0 is neutral)")
    # Subjectivity ranges from 0 (objective) to +1 (subjective)
    print(f"- Subjectivity: {sentiment.subjectivity:.2f} (closer to 0 is factual, closer to 1 is opinionated)")

    # Provide a more human-readable interpretation of polarity
    if sentiment.polarity > 0.3:
        print("  Interpretation: The quote generally conveys a positive tone.")
    elif sentiment.polarity < -0.3:
        print("  Interpretation: The quote generally conveys a negative tone.")
    else:
        print("  Interpretation: The quote generally conveys a neutral or mixed tone.")

#Main function
def main():
    # Def the path to your PDF file
    
    file_path = "/run/media/darklord/GVH USB/Python Code/Douglass_Narrative.pdf"
    
    #Load PDF text
    pdf_text = load_pdf_text(file_path)

    #Get user quote
    user_quote = get_user_quote()

    #Check if the quote is in the PDF (case-insensitive check)
    # The warning "Quote not found in the PDF" is fine if the quote isn't an exact match.It just means the script couldn't verify it against the PDF content.
    if user_quote.lower() in pdf_text.lower():
        print("\n✅ Quote found in the loaded PDF text (case-insensitive match).")
    else:
        print("\n⚠️ Warning: The exact quote was not found in the PDF.")
        print("   This might be due to typos, variations, or the quote not being in the document.")

    #Get explanation from OpenAI
    explanation = explain_quote_with_gpt(user_quote)
    print("\n--- OpenAI Explanation Result ---")
    print(explanation)

    #Perform NLP diagnostics
    analyze_quote_nlp(user_quote)

    #Output MLA citation
    print("\n--- MLA Citation ---")
    print("📝 For 'Narrative of the Life of Frederick Douglass, an American Slave':")
    print(MLA_CITATION)
    print("\n--- Program Finished ---")

if __name__ == "__main__":
    main()
