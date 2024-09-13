import os
import requests
from requests.auth import HTTPBasicAuth
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from twillio_service import TwilioService
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
import pandas as pd
from db import DB
from assistant import assistant
import time
from fastapi.staticfiles import StaticFiles
app = FastAPI()

app.mount("/voice_data", StaticFiles(directory="voice_data"), name="voice_data")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
):
    try:
        if file.content_type == 'text/csv':
            df = pd.read_csv(file.file)
         
        elif file.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
            df = pd.read_excel(file.file)
          
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel files are allowed.")
        
        DB.plan_call(df)
        
        return DB.take_plans()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/getplan")
async def get_plans():
    return DB.take_plans()

@app.post("/login")
async def login(request: Request):
    data = await request.json() 
    username = data.get("username")
    password = data.get("password")
    
    if DB.login(username, password):
        return {"message": "Login successful"}
    else:
        return {"message": "Login failed"}
    
@app.post("/call")
async def call(request: Request):
    data = await request.json()
    to_phone = data.get("phone_number")
    monthly_pay = data.get("monthly_pay")
    startmp3 = assistant.generate_speech('Madina', f"Assalomu alaykum, men Biznesi rivojlantirish banki xodimi Madina. Sizga  {monthly_pay} so`mlik to`lovni amalga oshirish uchun qo`ng`iroq qilmoqchiman. To'lov nega kech qolganini sababini ayta olasizmi?")    
   
    files = os.listdir('records')
    for file in files:
        os.remove(os.path.join('records', file))

   
    with open('voice_data/text.txt', 'w') as f:
        f.write('')

    try:
        call_sid = TwilioService.make_call(to_phone)
        return {"message": "Call made successfully", "call_sid": call_sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to make a call: {str(e)}")


@app.post("/twiml")
async def generate_twiml():
    response = VoiceResponse()
    
    response.play('https://628e-188-113-194-170.ngrok-free.app/voice_data/start.mp3')
   

    response.record(
        max_length=60,  # Maximum length of the recording in seconds
        speech_timeout="auto",  # Automatically stop recording after a pause in speech
        action="https://628e-188-113-194-170.ngrok-free.app/handle_recording",  # Полный URL для обработки записи
        play_beep=True
    )

    
    return Response(content=str(response), media_type="application/xml")




@app.post("/handle_recording")
async def handle_recording(request: Request):
    try:
        # Получение данных формы
        form_data = await request.form()
       
        # Получение RecordingUrl из данных формы
        recording_url = form_data.get('RecordingUrl')
        if not recording_url:
            raise HTTPException(status_code=400, detail="Recording URL not found")

        # Учетные данные Twilio
        account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN')

        # Ожидание перед запросом (опционально)
        time.sleep(2)

        # Запрос файла записи с Twilio
        response = requests.get(recording_url, auth=HTTPBasicAuth(account_sid, auth_token))
        
        if response.status_code == 200:
            # Сохранение записи
            file_name = os.path.join('records', f'{os.path.basename(recording_url)}.mp3')
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            # Вызов ассистента для обработки записи
            answer = assistant.workflow(file_name)
            print(answer)
            if answer["id"] == '5':

                assistant.after_call(
                form_data.get('To')
                ) 
       
            voice_response = VoiceResponse()

            # Воспроизведение ответа
            voice_response.play(f'https://628e-188-113-194-170.ngrok-free.app/{answer["voice"]}')

            if answer["id"] != '5':
                # Если id не равно 5, продолжаем запись
                voice_response.record(
                    max_length=60,  # Максимальная длина записи в секундах
                    speech_timeout="auto",  # Остановка записи после паузы
                    action="https://628e-188-113-194-170.ngrok-free.app/handle_recording",  # URL для обработки записи
                    play_beep=True
                )
          
            return Response(content=str(voice_response), media_type="application/xml")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to download recording, status code: {response.status_code}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/getcallinfo")
async def get_cwall_info():
   return DB.take_after_calls()

    


# To run your application
# uvicorn main:app --reload --port 8080
