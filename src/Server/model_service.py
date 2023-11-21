from fastapi import FastAPI
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

correction_model = AutoModelForSeq2SeqLM.from_pretrained("./v5/model")
correction_tokenizer = AutoTokenizer.from_pretrained("./v5/tokenizer")

if not os.path.exists('./similarity/'):
    semantic_sim_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    semantic_sim_model.save('./similarity/')
else:
    semantic_sim_model = SentenceTransformer('./similarity/')

if not os.path.exists('./translation_model'):
    translation_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    translation_model.save_pretrained('./translation_model/')
if not os.path.exists('./tokenizer'):
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    tokenizer.save_pretrained('./tokenizer/')

translation_model = MBartForConditionalGeneration.from_pretrained("./translation_model/")
tokenizer = MBart50TokenizerFast.from_pretrained("./tokenizer/")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
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

template_chat = """This is a conversation between human and AI. 
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
    return ''.join(list(filter(lambda x: x not in string.punctuation, text))).strip()

def translate(txt, src, to):
    tokenizer.src_lang = src
    encoded_en = tokenizer(txt, return_tensors="pt")
    generated_tokens = translation_model.generate(**encoded_en, forced_bos_token_id=tokenizer.lang_code_to_id[to])
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

def correct(text):
    if not any(map(lambda x: (ord(x) >= 65 and ord(x) <= 122) or ord(x) == 32, text)):
        inputs = correction_tokenizer(text, return_tensors="pt")
        max_length = 200  
        generated = correction_model.generate(inputs["input_ids"], max_length=max_length, num_return_sequences=1)
        corrected_text = correction_tokenizer.decode(generated[0], skip_special_tokens=True)
        corrected_text_2 = translate(translate(text, "hi_IN", "en_XX"), "en_XX", "hi_IN")
        if preprocess_result(text) == preprocess_result(corrected_text_2):
            return ''
        score = util.pytorch_cos_sim(semantic_sim_model.encode(corrected_text, convert_to_tensor=True), semantic_sim_model.encode(corrected_text_2, convert_to_tensor=True))[0][0].item()
        if score >= 0.9:
            return corrected_text_2
        return ''
    return ''

@app.post('/api/nameTitle')
async def nameTitle(request : nameTitleRequest):
    print("Renaming!!")
    question = request.question
    return model.generate(template_title.format(question = question))

@app.post('/api/inference')
async def inference(request : Request):
    print(request)
    input_req = request.input
    context = request.context
    english_input = translate(input_req, "hi_IN", "en_XX")
    res = model.generate(template_chat.format(context = context, input = english_input), max_tokens=1024)
    print(res)
    context += ("Human: " + english_input + '\n' + "AI: " + res + '\n')
    return {
        "result" : translate(res, "en_XX", "hi_IN") + '\n' + ('-' * 10) + '\n' + 'FYI : ' + res,
        "context" : context
    }

@app.post('/api/correctGrammar')
async def correct_grammar(request : correctGrammarRequest):
    text = request.text
    return correct(text)
    

if __name__ == '__main__':
    app.run()
