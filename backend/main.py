from fastapi import FastAPI
import sqlite3
import pandas as pd
from pydantic import BaseModel
import ollama
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import os

app = FastAPI()

# Load data once
def get_db_connection():
    return sqlite3.connect('subway_store.db')

df = pd.read_sql_query("SELECT * FROM subway", get_db_connection())

if not os.path.exists("./models/bart_large_mnli_model"):
    model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")
    model.save_pretrained("./models/bart_large_mnli_model")
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
    tokenizer.save_pretrained("./models/bart_large_mnli_model")

# Load NLP model
model = AutoModelForSequenceClassification.from_pretrained("./models/bart_large_mnli_model")
tokenizer = AutoTokenizer.from_pretrained("./models/bart_large_mnli_model")

classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)
categories = ["General chat", "Asking question about outlet"]

def get_category(question):
    result = classifier(question, candidate_labels=categories)
    return result['labels'][0]  # Highest score label

def execute_sql_query(query):
    try:
        with sqlite3.connect('subway_store.db') as conn:  # Open and close connection properly
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except Exception as e:
        return f"Error executing query: {e}"

def handle_question(question, category):
    if category == "General chat":
        return ollama.chat(model="llama3.2:1b", messages=[{'role': 'user', 'content': question}])['message']['content']

    if category == "Asking question about outlet":
        prompt = f"""Here is a details of a SQL table and the columns explanation.

        Table name:
        subway

        Columns name and explanation:
        outlet_name: the Subway outlet name. For example, Subway Menara UOA Bangsar.,
        address: the address of a Subway outlet. For example, Jalan Bangsar Utama 1, Unit 1-2-G, Menara UOA Bangsar, Kuala Lumpur, 59000.,
        opening_hours: the time of a Subway outlet operating. For example, Monday - Sunday, 8:00 AM - 8:00 PM.
        waze_link: A link to a platform Waze for navigation to the Subway outlet
        gmaps_link: A link to a platform Google Maps for navigation to the Subway outlet

        As a professional SQL Developer, create a SQL query that answer the user's question. There is no other SQLtable exists other than subway.

        Question: {question}

        Return SQL statement only in plain text.
        """

        query = ollama.chat(model="llama3.2:1b", messages=[{'role': 'user', 'content': prompt}])['message']['content']
        print(query)

        result =  execute_sql_query(query.replace("```sql", "").replace("```", "").strip())
        print(result)
        #prompt = f""" Write an answer about Subway outlets in a simplest way based on the:
        #Question: {question}

		#Result: {result}

		#Do not go out of topic.
		#"""
        #return  ollama.chat(model="llama3.2:1b", messages=[{'role': 'user', 'content': prompt}])['message']['content']
        return result[0] if len(result) == 1 else result

@app.get("/")
def read_root():
    return {"message": "Hello, Adam!"}

@app.get("/outlets")
def get_data():
    return {"data": df.to_dict(orient='records')}

class Chat(BaseModel):
    text: str  

@app.post("/chat")
async def ask_llm(chat: Chat):
    category = get_category(chat.text)
    answer = handle_question(chat.text, category)
    return {"message": chat.text, "response": answer}  
