import pandas as pd
from langchain_groq.chat_models import ChatGroq
from pandasai import SmartDataframe

data = pd.read_csv("data\Sample_Data.csv")
data.head()

llm = ChatGroq(
    model_name="mixtral-8x7b-32768", 
    api_key = "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")

df = SmartDataframe(data, config={"llm": llm})
tarea = False
while not tarea:
    test = 'Which are the top 5 cities by humidity?'
    inp = input("Give me a query: ")
    if not(inp == "q"):
        print(df.chat(inp))
    else:
        tarea = True