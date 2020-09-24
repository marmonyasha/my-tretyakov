from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time
import traceback
from config import *

def drive():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)

    peop_nums = [0, 0, 0, 0, 0, 0, 3, 0]

    def main(folder_id, pers):
        params = {
            'q': "'{}' in parents".format(folder_id),
            'pageSize': 1000,
            'fields': "nextPageToken, files(id, name, mimeType, owners)",
        }
        results = service.files().list(**params).execute()
        items = results.get('files', [])
        next_p_token = results.get('nextPageToken', None)

        if not items:
            ans = 0
            return ans
        else:
            ans = 0
            for i in items:
                if i['mimeType'] == 'application/vnd.google-apps.folder':
                    ans += main(i['id'], pers)
                else:
                    ans += 1
                    if pers and i['owners'][0]['emailAddress'] in people:
                        peop_nums[people[i['owners'][0]['emailAddress']]] += 1
        while next_p_token:
            results = service.files().list(pageToken=next_p_token, **params).execute()
            items = results.get('files', [])
            next_p_token = results.get('nextPageToken', None)
            for i in items:
                if i['mimeType'] == 'application/vnd.google-apps.folder':
                    ans += main(i['id'], pers)
                else:
                    ans += 1
                    if pers and i['owners'][0]['emailAddress'] in people:
                        peop_nums[people[i['owners'][0]['emailAddress']]] += 1
        return ans

    f = open('out.txt', 'w')
    f.write(str(main(fid_rus, 0)) + '\n')
    f.write(str(main(fid_inpr, 0)) + '\n')
    f.write(str(main(fid_done, 1) +
                main(fid_no_r, 1)) + '\n')

    for p in peop_nums:
        f.write(str(p) + '\n')
    f.close()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
service = build('sheets', 'v4', credentials=creds)

def min():
    # check folders
    drive()
    f = open('out.txt', 'r')
    g8, g9, g10, i14, i15, i16, i17, i18, i19, i20, i21 = f.read().split()
    f.close()
    # rewrite nums of files
    range_ = 'G8:G10'
    value_input_option = 'USER_ENTERED'
    value_range_body = {
        "range": "G8:G10",
        "majorDimension": "COLUMNS",
        "values": [
            [g8, g9, g10]
        ]
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_,
        valueInputOption=value_input_option, body=value_range_body).execute()
    range_ = 'I14:I21'
    value_input_option = 'USER_ENTERED'
    value_range_body = {
        "range": "I14:I21",
        "majorDimension": "COLUMNS",
        "values": [
            [i14, i15, i16, i17, i18, i19, i20, i21]
        ]
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_,
        valueInputOption=value_input_option, body=value_range_body).execute()

def day():
    # sorting1
    batch_update_spreadsheet_request_body = {
        "requests": [
            {
                "sortRange": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "sortSpecs": [
                        {
                            "dimensionIndex": 2,
                            "sortOrder": "ASCENDING"
                        },
                        {
                            "dimensionIndex": 3,
                            "sortOrder": "ASCENDING"
                        }
                    ]
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                       body=batch_update_spreadsheet_request_body).execute()
    # find done
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range="C1:C", majorDimension="COLUMNS").execute()
    cols = result.get('values', [])
    try:
        fd = str(cols[0].index('выполнен') + 1)
    except:
        return()
    moving = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range="A" + fd + ":D").execute()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range="выполненные!C1:C", majorDimension="COLUMNS").execute()
    cols = result.get('values', [])
    # put in empty space
    new = str(len(cols[0]) + 1)
    range_ = 'выполненные!A' + new + ':D'
    value_input_option = 'USER_ENTERED'
    value_range_body = {
        "range": 'выполненные!A' + new + ':D',
        "majorDimension": "ROWS",
        "values": moving.get('values', [])
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_,
        valueInputOption=value_input_option, body=value_range_body).execute()
    # clear
    range_ = "A" + fd + ":D"
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_).execute()

    # sorting2
    batch_update_spreadsheet_request_body = {
        "requests": [
            {
                "sortRange": {
                    "range": {
                        "sheetId": 575760989,
                        "startRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "sortSpecs": [
                        {
                            "dimensionIndex": 3,
                            "sortOrder": "ASCENDING"
                        }
                    ]
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                       body=batch_update_spreadsheet_request_body).execute()

from datetime import datetime
while True:
    t = datetime.now()
    try:
        min()
    except Exception as e:
        file = open('errors.txt', 'a')
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        file.write(str(t) + '\n')
        file.write(str(e) + '\n')
        file.write(traceback_str + '\n')
        file.close()
        time.sleep(2)
        continue
    if (t.hour == 4 and 0 <= t.minute <= 5):
        try:
            day()
        except Exception as e:
            file = open('errors.txt', 'a')
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            file.write(str(t) + '\n')
            file.write(str(e) + '\n')
            file.write(traceback_str + '\n')
            file.close()
            time.sleep(2)
            continue
        time.sleep(300)
    time.sleep(300)