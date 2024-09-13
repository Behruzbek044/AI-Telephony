
from transformers import pipeline
import requests
import openai
from fastapi import Request
from requests.auth import HTTPBasicAuth
from db import DB
from twillio_service import TwilioService

openai.api_key = 'YOUR_OPENAI_API_KEY'
# Модели для определения языка и преобразования речи в текст
detec_pipe = pipeline("audio-classification", model="fitlemon/whisper-small-uz-en-ru-lang-id")
pipe_uz = pipeline("automatic-speech-recognition", model="oyqiz/uzbek_stt")
pipe_ru = pipeline("automatic-speech-recognition", model="artyomboyko/whisper-base-fine_tuned-ru")



class assistant:

    
    @staticmethod
    def workflow(audio_file_path: str) -> str:
        
        lang = assistant.detectLang(audio_file_path)
        print(lang)
        text = assistant.stt(audio_file_path, lang)
        print(text)
        with open('voice_data/text.txt', 'a') as file:
            file.write(text + '\n')

        with open('voice_data/text.txt', 'r') as file:
            history = file.readlines()
            answer = assistant.gpt_answer(history)
          
        return {
            "id": answer,
            'voice':f'voice_data/{lang}/{answer}.mp3'
        }

        

    @staticmethod
    def detectLang(audio) -> str:
        result = detec_pipe(audio)
        result = max(result, key=lambda x: x['score'])['label']
        if result in ['uz','ru']:
            return result
        else:
            return 'uz'
    
    @staticmethod
    def stt(audio, lang) -> str:
        if lang == 'uz':
            
            token = "YOUR_MUXLISA_token"  
            payload = {
                "token": token
            }
            
            url = "https://api.muxlisa.uz/v1/api/services/stt/"
            
            files = [
            ('audio', (audio, open(audio, 'rb'), 'audio/mpeg'))
        ]
            headers = {}
            
            # Make the API request
            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            return  response.json()['message']['result']['text']
        
        else:
            result = pipe_ru(audio)

        return result['text']
   
    
    @staticmethod
    def generate_speech(voice, text):
        payload = {
            "token": 'YOUR_MUXLISA_token',
            "email": 'ismatilaevmuzaffar6@gmail.com',
            "voice": voice,
            "text": text,
            "format": 'mp3',
            "speed": 0.8,
            "pitch": 3,
            "emotion": 'good',
            "pause_sentence": 400,
            "pause_paragraph": 500,
            "bitrate": 48000
        }
        
        response = requests.post('https://speechgen.io/index.php?r=api/text', json=payload)
        response_data = response.json()
        
        if response_data.get('status') == 1:
            audio_url = response_data.get('file')
            
            # Загрузка файла
            audio_response = requests.get(audio_url)
            with open('voice_data/start.mp3', 'wb') as f:
                f.write(audio_response.content)
            
            return {
                'status': 'success',
                'message': 'Audio file generated successfully'
            }
        else:
            raise Exception(f"Error from API: {response_data.get('error')}")
        
    @staticmethod
    def gpt_answer(history: list) -> str:
        # Преобразование истории в формат, который понимает GPT
        formatted_history = [{'role': 'user', 'content': h.strip()} for h in history if h.strip()]
        
        # Проверка количества элементов в formatted_history
        if len(formatted_history) == 2:
            return "5"
        
        # Если условие не выполнено, продолжаем отправку запроса к GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """ 
                    Вы сотрудник банка, который спрашивает, когда клиент вернет долг. 
                    Вы должны спрашивать причину задержки платежа и спросить, когда клиент сможет вернуть долг. 
                    Выбирайте нужный вопрос из списка вопросов и возвращайте только ID вопроса. 
                    Учитывайте предыдущие вопросы и ответы клиента. Если всё понятно, завершите диалог, отправив ID 5. 
                    Если клиент говорит на узбекском, понимайте и отправляйте ID нужного вопроса на русском языке.
                    ТОлько номер id вопроса и все.
                    Слова id не нужно
                    Список вопросов:
                    id:2. На каком числе вы сможете вернуть долг?
                    id:3. Вы можете сказать точную дату, когда вы вернете долг?
                    id:4. У вас есть долг по кредиту, когда вы его вернете?
                    id:5. Больше нечего спрашивать.
                    id:6. Я сотрудник банка и хотел бы узнать, когда вы вернете долг.
                    """
                }
            ] + formatted_history
        )
        
        # Получение ответа от GPT и возвращение ID вопроса
        return response['choices'][0]['message']['content'].strip()

    

    @staticmethod
    def after_call(phone_number: str):
       
        twillio_info = TwilioService.get_call_info_with_recordings(phone_number)[0]
        phone_number = phone_number[1:]
        DB.delete_plan(phone_number)

        with open('voice_data/text.txt', 'r') as file:
            history = file.readlines()
            twillio_info['reason'] = history[0]
            twillio_info['date'] = history[1]

        DB.after_call(twillio_info)





        




