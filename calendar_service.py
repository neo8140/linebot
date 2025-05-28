import datetime
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

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
        'summary': f'{summary} - {user_id}',  # イベント名にユーザーID
        'description': f'元のメッセージ: {original_message}\nLINEユーザーID: {user_id}',  # 説明に詳細
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Tokyo'}
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()


def reserve_if_available(date_string, user_id):
    import re
    match = re.search(r'(\d{1,2})月(\d{1,2})日(\d{1,2})時', date_string)
    if not match:
        return '日付の形式が正しくありません。「6月5日14時」のように入力してください。'

    month, day, hour = map(int, match.groups())
    year = datetime.datetime.now().year
    try:
        start = datetime.datetime(year, month, day, hour)
    except ValueError:
        return '指定された日付が不正です。'

    if start < datetime.datetime.now():
        return '過去の日時は予約できません。'

    end = start + datetime.timedelta(hours=1)
    service = get_calendar_service()

    if check_availability(service, CALENDAR_ID, start, end):
        add_event(service, CALENDAR_ID, start, end, 'ドローン点検予約', user_id, date_string)
        return f'{month}月{day}日{hour}時に予約を入れました！'
    else:
        return f'{month}月{day}日{hour}時は埋まっています。他の時間をご指定ください。'





