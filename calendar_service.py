import datetime
import json
import os
import openai
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'lingyangshinei@gmail.com'

def get_calendar_service():
    service_account_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

def check_availability(service, calendar_id, start_time, end_time):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return len(events) == 0

def add_event(service, calendar_id, start_time, end_time, summary, user_id, original_message):
    event = {
        'summary': f'{summary} - {user_id}',
        'description': f'元のメッセージ: {original_message}\nLINEユーザーID: {user_id}',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Tokyo'}
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()

# 🔁 将来的にGPTなどで拡張するなら、この関数を差し替える
def parse_datetime_naturally(text):
    try:
        dt = parser.parse(text, fuzzy=True)
        japan_tz = pytz.timezone('Asia/Tokyo')  # ← タイムゾーンを取得
        dt = dt.replace(minute=0, second=0, microsecond=0)
        dt = japan_tz.localize(dt)  # ← タイムゾーン付きに変換！
        return dt
    except Exception:
        return None

def reserve_if_available(date_string, user_id):
    start = parse_datetime_naturally(date_string)
    if not start:
        return '日付の形式が正しくありません。「6月5日14時」や「6/5 14時」などの形式で入力してください。'

    # タイムゾーン設定
    japan_tz = pytz.timezone('Asia/Tokyo')
    now = datetime.now(japan_tz)
    start = start.astimezone(japan_tz)

    # 過去日時かどうか判定
    if start < now:
        return '過去の日時は予約できません。'

    end = start + timedelta(hours=1)
    service = get_calendar_service()

    if check_availability(service, CALENDAR_ID, start, end):
        add_event(service, CALENDAR_ID, start, end, 'ドローン点検予約', user_id, date_string)
        return f'{start.month}月{start.day}日{start.hour}時に予約を入れました！'
    else:
        return f'{start.month}月{start.day}日{start.hour}時は予約が入っています。他の時間をご指定ください。'







