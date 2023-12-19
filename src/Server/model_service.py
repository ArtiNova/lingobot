from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import gpt4all
from ReqResBody import Request
import os
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from nameTitleRequest import nameTitleRequest
from correctGrammar import correctGrammarRequest
from nltk.translate.gleu_score import sentence_gleu
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import string
from sentence_transformers import SentenceTransformer, util
from token_passing import AllReq
import json
import pymongo
import pickle
from translate import Translator

with open('./languages.pkl', 'rb') as f:
    lang_code_mapping = pickle.load(f)

user_collection = pymongo.MongoClient(json.load(open('./config.json'))['MONGO_URI'])['LingoBot'].get_collection("Users")

correction_model = AutoModelForSeq2SeqLM.from_pretrained("./v5/model")
correction_tokenizer = AutoTokenizer.from_pretrained("./v5/tokenizer")

# if not os.path.exists('./similarity/'):
#     semantic_sim_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
#     semantic_sim_model.save('./similarity/')
# else:
#     semantic_sim_model = SentenceTransformer('./similarity/')

if not os.path.exists('./translation_model'):
    translation_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    translation_model.save_pretrained('./translation_model/')
if not os.path.exists('./tokenizer'):
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    tokenizer.save_pretrained('./tokenizer/')

translation_model = MBartForConditionalGeneration.from_pretrained("./translation_model/")
tokenizer = MBart50TokenizerFast.from_pretrained("./tokenizer/")

token_cache = {}

app = FastAPI()

def authorize(request):
    if token_cache.get(request.token) == True:
        return True
    res = user_collection.find_one({'token' : request.token}) is not None
    token_cache[request.token] = res
    return res

origins = [
    "https://chat2fluency.duckdns.org",
    "https://chat2fluency.duckdns.org/chat",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = gpt4all.GPT4All(model_name = "ggml-model-gpt4all-falcon-q4_0", model_path = '.')

template_chat = """This is a chat between human and AI. 
I just want the immediate answer from the AI not an entire conversation. 
Assume that you are the AI.

Here are the previous conversations
{context}

Human: {input}
AI:
"""

template_title = """
Analyze this conversation and name the conversation with a creative single word title.
{question}
"""

def preprocess_result(text):
    return ''.join(list(filter(lambda x: x not in string.punctuation and x != '।', text))).strip()

def translate(txt, src, to):
    tokenizer.src_lang = src
    encoded_en = tokenizer(txt, return_tensors="pt")
    generated_tokens = translation_model.generate(**encoded_en, forced_bos_token_id=tokenizer.lang_code_to_id[to])
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

def correct(text):
    to_check = preprocess_result(text)
    if not any(map(lambda x: (ord(x) >= 65 and ord(x) <= 122), to_check)):
        if '।' not in text:
            text += '।'
        inputs = correction_tokenizer(text, return_tensors="pt")
        max_length = 200  
        generated = correction_model.generate(inputs["input_ids"], max_length=max_length, num_return_sequences=1)
        corrected_text = correction_tokenizer.decode(generated[0], skip_special_tokens=True)
        corrected_text_2 = translate(translate(text, "hi_IN", "en_XX"), "en_XX", "hi_IN")
        if preprocess_result(text) == preprocess_result(corrected_text_2):
            return ''
        # score = util.pytorch_cos_sim(semantic_sim_model.encode(corrected_text, convert_to_tensor=True), semantic_sim_model.encode(corrected_text_2, convert_to_tensor=True))[0][0].item()
        if preprocess_result(corrected_text) == preprocess_result(corrected_text_2):
            return corrected_text
        return corrected_text_2
    return ''

@app.post('/api/nameTitle')
async def nameTitle(request : nameTitleRequest):
    print("Renaming!!")
    context = ""
    for i in request.question[1:]:
        context += (i['role'] + ' : ' + i['content'] + '\n')
    with model.chat_session():
        response = model.generate(f"This is a chat between human and AI assistant can you analyze the chat and give a single word topic. Just reply the topic. Here's the conversation : {context}")
    return response.strip()

@app.post('/api/inference')
async def inference(request : Request):
    if authorize(request):
        print(request)
        input_req = request.input
        context = request.context
        if request.lang not in lang_code_mapping.values():
            english_input = Translator(from_lang=request.lang.split('-')[0], to_lang='en').translate(input_req)
        else:
            english_input = translate(input_req, request.lang.replace('-', '_'), "en_XX")
        with model.chat_session():
            model.current_chat_session = context
            model_output = model.generate(english_input, max_tokens=1024)
            context = model.current_chat_session
        if request.lang not in lang_code_mapping.values():
            result = (Translator(to_lang=request.lang.split('-')[0], from_lang='en').translate(model_output) + '\n' + ('-' * 10) + '\n' + 'FYI : ' + model_output).strip()
        else:
            result = (translate(model_output, "en_XX", request.lang.replace('-', '_')) + '\n' + ('-' * 10) + '\n' + 'FYI : ' + model_output).strip()
        return {
            "result" : result, 
            "context" : context
        }
    return Response(status_code=401) 

@app.post('/api/correctGrammar')
async def correct_grammar(request : correctGrammarRequest):
    if authorize(request):
        text = request.text
        if request.lang == 'Hindi':
            return correct(text)
        return ''
    return Response(status_code=401)
    

if __name__ == '__main__':
    app.run()
