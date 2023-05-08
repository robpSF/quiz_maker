import openai
import re
import streamlit as sl
import pandas as pd
import io
from io import BytesIO

openai.organization = sl.secrets["organization"]
openai.api_key =  sl.secrets["key"]
password =  sl.secrets["password"]

if password != sl.text_input("Enter password"): exit(600)

temp = sl.sidebar.slider("Craziness of ideas",0.0,1.0,0.5)
#model = sl.sidebar.radio("model to use",("text-davinci-003","gpt-3.5-turbo-0301"))
model = "text-davinci-003"

default_prompt="from the following {data} create a multiple choice quiz.   Format your answer in a table with the following column headings - Question_text, 1,2,3,4, Answer - where 1,2,3,4 are plausible answers and Answer is the number of the column heading with the correct answer. Randomise the correct answer column so the player can't easily guess. There should be 7 rows, each row is a different question {data}="

originating_text = sl.text_area("Table command", value=default_prompt)
scenario = sl.text_area("Content")
quiz_code = sl.text_input("quiz code")


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'})
    worksheet.set_column('A:A', None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def davinci(text):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=text,
      temperature=temp,
      max_tokens=1000,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    return response

def turbo(text):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0301",
      messages= [{"role": "user", "content": text}],
      temperature=temp,
      max_tokens=1000,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    return response


go = sl.button("do it!")

if go:
    sl.sidebar.text("Submitting to the AI Gods....")

    sl.write(originating_text+scenario)

    if model == "text-davinci-003":
        response = davinci(originating_text+scenario)
        sl.write(response)
        AI_scenario = response["choices"][0]["text"]
        sl.write(AI_scenario)
    elif model == "gpt-3.5-turbo-0301":
        response = turbo(originating_text+scenario)
        sl.write(response)
        #AI_scenario = response["choices"][0]["text"]
        #sl.write(AI_scenario)

    #df = pd.read_csv(io.StringIO(AI_scenario))

    csv_bytes = AI_scenario.encode('utf-8')
    csv_bytes_io = BytesIO(csv_bytes)

    df = pd.read_csv(csv_bytes_io)

    # insert a new column at the start of the dataframe
    df.insert(0, "Question_coding", quiz_code)
    sl.write(df)

    df_xlsx = to_excel(df)
    sl.download_button(label='📥 Download Answers Result',
                       data=df_xlsx,
                       file_name=quiz_code+'_Answers.xlsx')

