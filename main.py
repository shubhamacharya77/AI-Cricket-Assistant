
import os
import httpx #for async request 
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
load_dotenv()

app=FastAPI()

API_KEY = os.getenv("HUGGINGFACE_API_KEY")
@app.get("/")
def healthCheck():
    return{
        "message":"server is running !"
    }



@app.post("/AI_assistant")

#Checks for prompt injection
async def chatbot(request:str):
  blocked_words = [
    "ignore previous",
    "forget rules",
    "system prompt",
    "jailbreak",
    "backend",
    "hack",
    "system setting"
]
  try:
    if  any(word in request.lower() for word in blocked_words):
        return {"answer": "Potential prompt injection detected."}
    async with httpx.AsyncClient(timeout=60.0) as client:
     response=await client.post(
        url= "https://router.huggingface.co/v1/chat/completions",
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "MiniMaxAI/MiniMax-M2.7:novita",
            "messages": [
                { 
                   #role based prompt
                    "role": "system",
                    "content": """"You are a cricket-only AI assistant.

                        MANDATORY POLICY:
                        - Allowed topic: Cricket only.
                        - Block all other topics.

                        If the user asks anything not related to cricket, respond with exactly:
                        I can only help with cricket-related questions.

                        Do not explain.
                        Do not apologize.
                        Do not answer the blocked question.

                        For cricket questions:
                        - Give clear answers
                        - Give coaching tips
                        - Be professional
                        - Keep responses concise """
                },
            {
            "role": "user",
            "content": request
            }
                    ],
    "temperature": 0.2,
    "stream": False
    })
    return {"answer" : response.json()["choices"][0]["message"]["content"]}
  except Exception as e:
     return {
        "error :" :repr(e)
     }



#local LLM use

# class UserInput(BaseModel):
#     userQuery:str
#     temperature:float
#     max_tokens:int
#     frequency_penalty:float


# @app.post("/AI_assistant")
# async def AIassistant(request:UserInput):
#     async with httpx.AsyncClient() as client:
#     # response from local llms 
#         response=await client.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model":"phi3:mini",
#                 "prompt":request.userQuery,
#                 "stream":False,
#                 "options":{
#                 "temperature":request.temperature,
#                 "max_tokens":request.max_tokens,
#                 "frequency_penalty":request.frequency_penalty
#                 }
#             }
#         )
#     return {
#         "response": response.json()["response"]
#     }

    