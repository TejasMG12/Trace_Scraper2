

import google.generativeai as genai
import os
# import json
from IPython.display import Image
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging

from Secrets import GOOGLE_API_KEY
logging.basicConfig(level=logging.INFO)


def detectDrugFromText(post):
    try:
        genai.configure(api_key=GOOGLE_API_KEY)

        # Choose the Generative Model
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        prompt_text = f"""
        This is a reddit post and few comments on it which potentially advertises selling drugs, identify the following post for potential indicators of illicit drug trafficking:
        {post}
        lookout for emoji's like 🍄💊🍀 used to imply drugs,
        give Output strictly as JSON no other thing: for example 
        {{
            "userName":<user who posted>,
            "postText" : "I sell cocaine, heroin, c_a_n_n_a_b_i_s, shrooms",
            "postUrl" : "<url>",
  "drug_related_terms": [
    "cocaine",
    "heroin",
    "methamphetamine",
    "cannabis",
    "LSD",
    "MDMA",
    "PCP",
    "ketamine"
  ],
  "drug_trafficking_indicators": [
    "cryptocurrency transactions",
    "dark web marketplaces",
    "encrypted communication",
    "use of specific lingo or slang",
    "references to specific drug routes or locations"
  ],
  "potential_drug_trafficking_detected": "true"/"false",
  "confidence_level": high/medium/low,
  "links":[<links found in text>],
  "usernames":[<usernames of suspicius commentors>]
 }},
        """
        response = model.generate_content([prompt_text],
                                          safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        })

        # Print the response
        return response.text.split('```')[1].strip().strip('json').strip('"').strip("\n")

    except Exception as e:
        # logging.error(f"Error in detectDrugFromImage: {e}")
        print(e)
        return f"""{{
            "userName": [],
            "potential_drug_trafficking_detected": "false",
            "PossibleDrugName": [],
            "ConfidenceLevel": "Low"
        }}"""


# print(detectDrugFromText(["Sender1 : Доброго времени суток!сдесь Вы можете приобрести качественный товар по приятной цене.качество товара тщательно проверяется нами перед тем как попасть на витрину.зайдя к нам в шоп,вы не останетесь равнодушными!💯👍💪🔞",
#                            """Turin_robot: 🍁🍄❄️ 💊 Ciao a tutti i nostri clienti, benvenuti 🍁🍄❄️💊

# # Sono C.O.C.A.I.N.A❄️❄️ ...☘️

# # 🍀 , M.A.R.I.H.U.A.N.A 🍁.....
# # CARTE CLONATE 💳 E SOLDI FALSI 💶 PATENTE DI GUIDA 🪪 E CARTA D'IDENTITÀ DISPONIBILI ANCHE
# # P.I.L.L.O.L.E💊💊 ...... F.U.N.G.O 🍄🍄.

# # Il corriere è pronto a scendere in campo 🏍️

# # 💳🪪💶💶Telegram

# # https://t.me/Club420_graspharma

# # Telegramma 🍃🍃❄️💊
# # https://t.me/Club420_graspharma

# # Contattaci ☎️☎️🚚

# # Telegramma @Jorginho_420
# # Telegramma @Jorginho_420"""]))
