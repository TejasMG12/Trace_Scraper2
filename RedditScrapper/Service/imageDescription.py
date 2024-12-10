# import google.generativeai as genai
# # from IPython.display import Markdown
# # from google.colab import drive
# # import google.colab.usersecrets

# # drive.mount('/content/drive')
# # %cd drive/MyDrive/SIH
# import os
# from IPython.display import Image


# def detectDrugFromImage(name):
#     GOOGLE_API_KEY2 = 'AIzaSyDOLcGweO0hOBHUZth3F0RRAys3x6etc2o'

#     genai.configure(api_key=GOOGLE_API_KEY2)
#     # Upload the file and print a confirmation.
#     sample_file = genai.upload_file(path=name,
#                                     display_name="Jetpack drawing")

#     # Choose a Gemini API model.
#     model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
#     prompt_text = """
#     This is an image found on social media channel potentially sells drugs, identify if this is a harmful drug?

#     Output as JSON: 
#     {
#     "Description":<string>,
#     "DrugIdentified": True/False, 
#     "PossibleDrugName": <list[string]>,
#     "ConfidenceLevel": "<High/Medium/Low>"
#     }
#     """
#     from google.generativeai.types import HarmCategory, HarmBlockThreshold

#     # Prompt the model with text and the pr eviously uploaded image.
#     response = model.generate_content([sample_file, prompt_text], safety_settings={
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#     })
#     if (response.text):
#         return response.text
#     else:
#         return """{
#     "Description": "Sensitive information",
#     "DrugIdentified": False, 
#     "PossibleDrugName": [],
#     "ConfidenceLevel": "Medium"
#     }"""



import google.generativeai as genai
# import json
from IPython.display import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
from Secrets import GOOGLE_API_KEY
def detectDrugFromImage(name):
    # Ensure API key is securely managed
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Upload the file and confirm success
        name = "Media/" + name 
        sample_file = genai.upload_file(path=name, display_name="Social Media Image")
        logging.info(f"Image {name} uploaded successfully.")

        # Choose the Generative Model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        prompt_text = """
        This is an image found on social media channel potentially selling drugs, identify if this is a harmful drug?

        Output as strictly as JSON nothing else!: 
        {
        "Description":<string>,
        "DrugIdentified": True/False, 
        "PossibleDrugName": <list[string]>,
        "ConfidenceLevel": "<High/Medium/Low>"
        }
        """
        
        # Generate content with safety settings for sensitive content
        response = model.generate_content(
            [sample_file, prompt_text], 
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        # Parse and return the response text
        if response and response.text:
            
            return response.text.split('```')[1].strip('json').strip('\n')

        # Fallback response
        # logging.warning("No response text. Returning default.")
        return """{
            "Description": "Sensitive information",
            "DrugIdentified": False,
            "PossibleDrugName": [],
            "ConfidenceLevel": "Medium"
        }"""
    
    except Exception as e:
        logging.error(f"Error in detectDrugFromImage: {e}")
        return """{
            "Description": "Error encountered during processing",
            "DrugIdentified": False,
            "PossibleDrugName": [],
            "ConfidenceLevel": "Low"
        }"""
# print(detectDrugFromImage('./Service/channelmessage7.jpg'))