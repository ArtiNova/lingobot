from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gpt4all
import os
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from ReqResBody import Response, Request
from loginReqRes import LoginRequest
from pymongo import MongoClient
import json
from Previous import PreviousRequest
from forConversation import conversationRequest
from UpdateChatRequest import UpdateChatRequest, UpdateCurrentRequest
from UpdateContext import UpdateContext
from updateTitle import UpdateTitle

MONGO_URI = json.load(open('./config.json'))["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["LingoBot"]
user_collection = db.get_collection("Users")
chat_collection = db.get_collection("Chats")

# if not os.path.exists('./translation_model'):
#     translation_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
#     translation_model.save_pretrained('./translation_model/')
# if not os.path.exists('./tokenizer'):
#     tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
#     tokenizer.save_pretrained('./tokenizer/')
    
# translation_model = MBartForConditionalGeneration.from_pretrained("./translation_model/")
# tokenizer = MBart50TokenizerFast.from_pretrained("./tokenizer/")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# model = gpt4all.GPT4All(model_name = "ggml-model-gpt4all-falcon-q4_0", model_path = '.')


# template = """This is a conversation between human and AI. 
# I just want the immediate answer from the AI not an entire conversation. 

# Here's the context
# {context}

# Human:{input}
# AI:
# """

# def translate(txt, src, to):
#     tokenizer.src_lang = src
#     encoded_en = tokenizer(txt, return_tensors="pt")
#     generated_tokens = translation_model.generate(**encoded_en, forced_bos_token_id=tokenizer.lang_code_to_id[to])
#     return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

# @app.post('/api/inference')
# async def inference(request : Request):
#     try:
#         print(request)
#         input_req = request.input
#         context = request.context
#         english_input = translate(input_req, "hi_IN", "en_XX")
#         res = model.generate(template.format(context = context, input = english_input), max_tokens=1024)
#         print(res)
#         if (res.startswith('AI:')):
#             res : str = res.replace('AI:', '', 1)
#         return Response(result = translate(res, "en_XX", "hi_IN"))
#     except:
#         return Response(result="Internal Server Error 500") 
    
@app.post('/api/login')
async def login(request : LoginRequest):
    username, password = request.username, request.password
    return user_collection.find_one({"username" : username, "password" : password}) is not None

@app.post("/api/signup")
async def signup(request : LoginRequest):
    username, password = request.username, request.password
    if (user_collection.find_one({"username" : username, "password" : password}) is None):
        user_collection.insert_one({"username" : username, "password" : password})
        return True
    return False

@app.post("/api/loadPrevious")
async def loadPrevious(request : PreviousRequest):
    username, title = request.username, request.title
    res = chat_collection.find_one({"username" : username, "title" : title})
    return {
        "messages" : res["messages"],
        "context" : res["context"]
    }

@app.post('/api/getPrevious')
async def getPrevious(request : conversationRequest):
    res = chat_collection.find({"username" : request.username})
    titles = []
    for doc in res:
        titles.append(doc['title'])
    return titles

@app.post('/api/newChat')
async def updateChat(request : UpdateChatRequest):
    username, title = request.username, request.title
    chat_collection.insert_one({"username" : username, "title" : title, "messages" : list(), "context" : ''})
    return True

@app.post('/api/updateMessages')
async def updateMessages(request: UpdateCurrentRequest):
    username, title, messages = request.username, request.title, request.messages
    chat_collection.update_one({"username" : username, "title" : title}, { "$set" : {
        "username" : username,
        "title" : title,
        "messages" : messages
    }})
    return True

@app.post('/api/deleteConv')
async def deleteConv(request: UpdateChatRequest):
    username, title = request.username, request.title
    chat_collection.delete_one({"username" : username, "title" : title})
    return True

@app.post('/api/renameTitle')
async def renameTitle(request : UpdateTitle):
    username, oldtitle, newtitle = request.username, request.oldTitle, request.newTitle
    chat_collection.update_one({"username" : username, "title" : oldtitle}, {"$set" : {
       "title" : newtitle 
    }})
    return True

@app.post('/api/updateContext')
async def updateContext(request : UpdateContext):
    username, title, context = request.username, request.title, request.context
    chat_collection.update_one({"username" : username, "title" : title}, {
        "$set" : {
            "context" : context
        }
    })


if __name__ == '__main__':
    app.run()
