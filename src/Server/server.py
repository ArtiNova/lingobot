from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import os
from loginReqRes import LoginRequest
from pymongo import MongoClient
import json
from Previous import PreviousRequest
from forConversation import conversationRequest
from UpdateChatRequest import UpdateChatRequest, UpdateCurrentRequest
from UpdateContext import UpdateContext
from updateTitle import UpdateTitle
from AudioRequestResponse import AudioRequest
from gtts import gTTS
from fastapi.responses import FileResponse
from token_passing import AllReq

with open('./config.json') as f:
    data = json.load(f)
    MONGO_URI, LANGUAGES = data['MONGO_URI'], data['LANGUAGES']

client = MongoClient(MONGO_URI)
db = client["LingoBot"]
user_collection = db.get_collection("Users")
chat_collection = db.get_collection("Chats")


token_cache = {}
import secrets

def generate_random_token(length=32):
    token = secrets.token_hex(length // 2)
    while user_collection.find_one({"token" : token}) is not None:
        token = secrets.token_hex(length // 2)
    return token

# if not os.path.exists('./translation_model'):
#     translation_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
#     translation_model.save_pretrained('./translation_model/')
# if not os.path.exists('./tokenizer'):
#     tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
#     tokenizer.save_pretrained('./tokenizer/')
    
# translation_model = MBartForConditionalGeneration.from_pretrained("./translation_model/")
# tokenizer = MBart50TokenizerFast.from_pretrained("./tokenizer/")

app = FastAPI()
#app.add_middleware(TrustedHostMiddleware, allowed_hosts = ["chat2fluency.duckdns.org"])

origins = [
    "https://chat2fluency.duckdns.org",
    "https://chat2fluency.duckdns.org/chat",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
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
    

def authorize(request):
    if token_cache.get(request.token) == True:
        return True
    res = user_collection.find_one({'token' : request.token}) is not None
    token_cache[request.token] = res
    return res

@app.post('/api/login')
async def login(request : LoginRequest):
    username, password = request.username, request.password
    res = user_collection.find_one({"username" : username, "password" : password})
    return {"status" : res is not None, "token" : res['token'] if res is not None else None}

@app.post("/api/signup")
async def signup(request : LoginRequest):
    username, password = request.username, request.password
    if (user_collection.find_one({"username" : username, "password" : password}) is None):
        token = generate_random_token(32)
        user_collection.insert_one({"username" : username, "password" : password, "token" : token})
        return {"status" : True, 'token' : token}
    return False

@app.post("/api/loadPrevious")
async def loadPrevious(request : PreviousRequest):
    username, title = request.username, request.title
    if (authorize(request)):
        res = chat_collection.find_one({"username" : username, "title" : title})
        return {
            "messages" : res["messages"],
            "context" : res["context"]
        }
    else:
        return Response(status_code=401)

@app.post('/api/getPrevious')
async def getPrevious(request : conversationRequest):
    if (authorize(request)): 
        res = chat_collection.find({"username" : request.username})
        titles = []
        for doc in res:
            titles.append(doc['title'])
        return titles
    return Response(status_code=401)

@app.post('/api/newChat')
async def updateChat(request : UpdateChatRequest):
    if (authorize(request)):
        username, title = request.username, request.title
        chat_collection.insert_one({"username" : username, "title" : title, "messages" : list(), "context" :  [{'role': 'system', 'content': ''}]})
        return True
    else:
        return Response(status_code=401)

@app.post('/api/updateMessages')
async def updateMessages(request: UpdateCurrentRequest):
    if (authorize(request)):
        username, title, messages = request.username, request.title, request.messages
        chat_collection.update_one({"username" : username, "title" : title}, { "$set" : {
            "username" : username,
            "title" : title,
            "messages" : messages
        }})
        return True
    return Response(status_code=401)

@app.post('/api/deleteConv')
async def deleteConv(request: UpdateChatRequest):
    if (authorize(request)):
        username, title = request.username, request.title
        chat_collection.delete_one({"username" : username, "title" : title})
        return True
    return Response(status_code=401)

@app.post('/api/renameTitle')
async def renameTitle(request : UpdateTitle):
    if (authorize(request)):
        username, oldtitle, newtitle = request.username, request.oldTitle, request.newTitle
        chat_collection.update_one({"username" : username, "title" : oldtitle}, {"$set" : {
        "title" : newtitle 
        }})
        return True
    return Response(status_code=401)

@app.post('/api/updateContext')
async def updateContext(request : UpdateContext):
    if (authorize(request)):
        username, title, context = request.username, request.title, request.context
        chat_collection.update_one({"username" : username, "title" : title}, {
            "$set" : {
                "context" : context
            }
        })
        return True
    return Response(status_code=401)

@app.post('/api/audio')
async def createAudio(request : AudioRequest):
    tts = gTTS(text=request.message, lang=request.lang.split('-')[0], slow=False)
    tts.save('output.mp3')
    return True

@app.get('/api/languages')
async def send_available_languages():
    underscore_to_hiphen = {}
    for i in LANGUAGES:
        underscore_to_hiphen[i] = LANGUAGES[i].replace('_', '-')
    return {
        "languages" : list(LANGUAGES.keys()),
        "lang-to-code" : underscore_to_hiphen
    }

@app.get('/api/playSound')
async def playSound():
    return FileResponse("output.mp3")

@app.post('/api/deleteAudio')
async def remove():
    os.remove("output.mp3")
    return True



if __name__ == '__main__':
    app.run()
