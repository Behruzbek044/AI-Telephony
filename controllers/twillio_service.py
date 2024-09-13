from twilio.rest import Client
import os


account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

class TwilioService:
    @staticmethod
    def make_call(to_phone: str):
    
        try:
            call = client.calls.create(
                to=to_phone,
                from_='+17194198225',
                url='https://628e-188-113-194-170.ngrok-free.app/twiml' ,
                
            )
            return call.sid
        except Exception as e:
            raise Exception(f"Failed to make a call: {str(e)}")
        
    @staticmethod
    def get_call_info_with_recordings(phone_number):
        base_url = f'https://{account_sid}:{auth_token}@api.twilio.com'
        
        # Получаем список вызовов для определенного номера телефона
        calls = client.calls.list(to=phone_number)  # Используйте `from_` для исходящих вызовов
        recordings = client.recordings.list()

        # Создаем словарь для быстрого поиска записи по SID вызова
        recording_urls = {recording.call_sid: f'{base_url}{recording.uri.replace(".json", ".mp3")}' for recording in recordings}

        call_info_list = []
        for call in calls:
            call_info = {
                'phone_number': call.to,
                'duration': call.duration,
                'date_created': call.date_created,
                'download_url': recording_urls.get(call.sid)
            }
            call_info_list.append(call_info)

        return call_info_list

