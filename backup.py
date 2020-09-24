from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import time
import traceback
from config import *

def trying(func, *args):
    while True:
        try:
            return func(*args)
        except Exception as e:
            file = open('errors2.txt', 'a')
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            file.write(str(t) + '\n')
            file.write(str(e) + '\n')
            file.write(traceback_str + '\n')
            file.close()
            time.sleep(2)
            continue
    #raise Exception('5 times fail')


def delete(folder_id):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token2.pickle'):
        with open('token2.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token2.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)

    def list_items(folder_id):
        params = {
            'q': "'{}' in parents".format(folder_id),
            'pageSize': 1000,
            'fields': "nextPageToken, files(id, name, mimeType)",
        }
        results = service.files().list(**params).execute()
        items = results.get('files', [])
        next_p_token = results.get('nextPageToken', None)
        ans = []
        if not items:
            return ans
        else:
            for i in items:
                ans += [i['id']]
        while next_p_token:
            for i in items:
                ans += [i['id']]
        return ans

    for i in list_items(folder_id):
        trying(service.files().delete(fileId=i).execute)
    return

def drive(fold_name, arch_name):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token2.pickle'):
        with open('token2.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token2.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)

    def main(folder_id, target_id):
        params = {
            'q': "'{}' in parents".format(folder_id),
            'pageSize': 1000,
            'fields': "nextPageToken, files(id, name, mimeType)",
        }
        results = trying(service.files().list(**params).execute)
        items = trying(results.get, 'files', [])
        next_p_token = trying(results.get, 'nextPageToken', None)

        if not items:
            ans = 0
            return
        else:
            ans = len(items)
            for i in items:
                if i['mimeType'] == 'application/vnd.google-apps.folder':
                    file_metadata = {
                        'name': i['name'],
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [target_id]
                    }
                    file = trying(service.files().create(body=file_metadata,
                                                  fields='id').execute)
                    main(i['id'], trying(file.get, 'id'))
                else:
                    request_body = {
                        "parents": [target_id]
                    }
                    trying(service.files().copy(fileId=i['id'], body=request_body).execute)
        while next_p_token:
            results = trying(service.files().list(pageToken=next_p_token, **params).execute)
            items = trying(results.get, 'files', [])
            next_p_token = trying(results.get, 'nextPageToken', None)
            ans += len(items)
            for i in items:
                if i['mimeType'] == 'application/vnd.google-apps.folder':
                    file_metadata = {
                        'name': i['name'],
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [target_id]
                    }
                    file = trying(service.files().create(body=file_metadata,
                                                  fields='id').execute)
                    main(i['id'], trying(file.get, 'id'))
                else:
                    request_body = {
                        "parents": [target_id]
                    }
                    trying(service.files().copy(fileId=i['id'], body=request_body).execute)
        return

    params = {
        'q': "'{}' in parents".format(arch_name),
        'pageSize': 1000,
        'fields': "nextPageToken, files(id, name, mimeType, createdTime)",
    }
    results = trying(service.files().list(**params).execute)
    items = trying(results.get, 'files', [])
    def f(x):
        return x['createdTime']
    items.sort(key=f)
    if len(items) >= 10:
        delete(items[0]['id'])
        trying(service.files().delete(fileId=items[0]['id']).execute)
        results = trying(service.files().list(**params).execute)
        items = trying(results.get, 'files', [])
        items.sort(key=f)
    while len(items) >= 10:
        delete(items[0]['id'])
        trying(service.files().delete(fileId=items[0]['id']).execute)
        results = trying(service.files().list(**params).execute)
        items = trying(results.get, 'files', [])
        items.sort(key=f)
    t = datetime.now()
    file_metadata = {
        'name': str(t),
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [arch_name]
    }
    file = trying(service.files().create(body=file_metadata,
                                  fields='id').execute)
    main(fold_name, trying(file.get, 'id'))

while True:
    t = datetime.now()
    if True:
        try:
            drive(arch_eng)
            #drive(arch_rus)
            time.sleep(3600)
        except Exception as e:
            file = open('errors2.txt', 'a')
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            file.write(str(t) + '\n')
            file.write(str(e) + '\n')
            file.write(traceback_str + '\n')
            file.close()
            time.sleep(2)
            continue
    time.sleep(2500)
