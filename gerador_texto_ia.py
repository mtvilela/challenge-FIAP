import os
import google.generativeai as genai
from dotenv import load_dotenv


def RIA():
    load_dotenv()
    CHAVE_API_KEY = os.getenv("KEY")
    
    genai.configure(api_key=CHAVE_API_KEY)

    MODELO_ESCOLHIDO = "gemini-1.5-flash"

    prompt_sistema = ""

    llm = genai.GenerativeModel(
        model_name=MODELO_ESCOLHIDO,
        system_instruction=prompt_sistema

    )
    pergunta = ""
    resposta = llm.generate_content(pergunta)
    resposta = resposta.txt
    
    return resposta
