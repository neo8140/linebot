import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Googleカレンダーの読み書き権限スコープ
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Step 1: 認証処理
def get_calendar_service():
    creds = None
    # トークンファイルがあれば読み込む
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # トークンがなければ認証フローを開始
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # トークンを保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# Step 2: 予定を確認
def check_availability(service, calendar_id, start_time, end_time):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return len(events) == 0  # Trueなら空いている

# Step 3: 予定を追加
def add_event(service, calendar_id, start_time, end_time, summary):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Tokyo'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Tokyo'}
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()

# --- 実行部分（例） ---
if __name__ == '__main__':
    service = get_calendar_service()
    calendar_id = 'primary'  # 自分のGoogleカレンダー

    # 予約希望日時（例：2025-06-05 14:00〜15:00）
    start = datetime.datetime(2025, 6, 5, 14, 0)
    end = datetime.datetime(2025, 6, 5, 15, 0)

    if check_availability(service, calendar_id, start, end):
        print('空いています、予約を入れます。')
        add_event(service, calendar_id, start, end, 'ドローン点検予約（LINE）')
    else:
        print('その時間は埋まっています。')
def reserve_if_available(date_string):
    import re
    import datetime

    match = re.search(r'(\d{1,2})月(\d{1,2})日(\d{1,2})時', date_string)
    if not match:
        return '日付の形式が正しくありません。「6月5日14時」のように入力してください。'

    month, day, hour = map(int, match.groups())
    year = datetime.datetime.now().year
    try:
        start = datetime.datetime(year, month, day, hour, 0)
    except ValueError:
        return '指定された日付が不正です。'

    if start < datetime.datetime.now():
        return f'{month}月{day}日{hour}時はすでに過ぎています。未来の日時を指定してください。'

    end = start + datetime.timedelta(hours=1)
    service = get_calendar_service()
    calendar_id = 'primary'

    if check_availability(service, calendar_id, start, end):
        add_event(service, calendar_id, start, end, 'ドローン点検予約（LINE）')
        return f'{month}月{day}日{hour}時は空いているので予約を入れました！'
    else:
        return f'{month}月{day}日{hour}時は埋まっています。他の時間をご指定ください。'

