import datetime
import json
import os
import openai
import pytz
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
from datetime import datetime, timedelta
from pytz import timezone

# 環境変数からAPIキーを読み込み
openai.api_key = os.environ["OPENAI_API_KEY"]

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


def parse_datetime_naturally(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "以下の日本語の日時表現を ISO8601形式 (例: 2025-06-07T15:00:00+09:00) に変換してください。タイムゾーンは常に Asia/Tokyo です。"
                },
                {"role": "user", "content": text}
            ]
        )
        result_text = response["choices"][0]["message"]["content"].strip()

        # ASCIIで再構成して不正文字を除去（これが前回のエラー対策）
        result_text_ascii = result_text.encode("ascii", errors="ignore").decode()

        dt = parser.isoparse(result_text_ascii)
        return dt.astimezone(pytz.timezone("Asia/Tokyo"))
    except Exception as e:
        # ここでエラーをログに出す＋呼び出し元に詳細を返す
        error_message = f"[GPT日付解析エラー] {e}"
        print(error_message)
        return error_message  # ← Noneではなく、文字列としてエラーを返す


def reserve_if_available(date_string, user_id):
    start = parse_datetime_naturally(date_string)

    if isinstance(start, str):  # エラーメッセージが返ってきたとき
        return f"日付の認識に失敗しました：{start}"

    # タイムゾーン設定
    japan_tz = pytz.timezone('Asia/Tokyo')
    now = datetime.now(japan_tz)
    start = start.astimezone(japan_tz)

    if start < now:
        return '過去の日時は予約できません。'

    end = start + timedelta(hours=1)
    service = get_calendar_service()

    if check_availability(service, CALENDAR_ID, start, end):
        add_event(service, CALENDAR_ID, start, end, 'ドローン点検予約', user_id, date_string)
        return f'{start.month}月{start.day}日{start.hour}時に予約を入れました！'
    else:
        return f'{start.month}月{start.day}日{start.hour}時は予約が入っています。他の時間をご指定ください。'










