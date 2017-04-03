# -*- coding: utf-8 -*-
import requests
import json
import time

token = 'xoxp-TOKEN' # 슬랙 RTM(Real Time Messaging) API 토큰
hook_url = 'https://' # 슬랙 Incoming Webhook URL
bot_name = '' # 슬랙 메시지에 쓰일 봇 이름
channel_id = "#channel_id" # 채널 ID

api_files_list = 'https://slack.com/api/files.list'

second_day = 60 * 60 * 24
ts_to = time.time() - 60 * second_day

data = {'token': token, 'ts_to': ts_to, 'types': 'images', 'count': 1000, 'page': 1}
response = requests.post(api_files_list, data = data)

num_total = response.json()['paging']['total']
num_pages = response.json()['paging']['pages']

print "files: {}\npages: {}".format(num_total, num_pages)

list_starred = []
list_private = []
list_delete = []

delete_size = 0

if len(response.json()['files']) == 0:
    exit(0)
for p in range(1, num_pages+1):
    print "Current page: {}".format(p)
    data = {'token': token, 'ts_to': ts_to, 'types': 'images', 'count': 1000, 'page': p}
    response = requests.post(api_files_list, data = data)

    for f in response.json()['files']:
        try:
            f['num_stars']
            list_starred.append(f['id'])

        except:
            if f['is_public'] == False:
                list_private.append(f['id'])
            else:
                list_delete.append(f['id'])
                delete_size += f['size']
print "Starred files count: {}".format(len(list_starred))
print "Private files count: {}".format(len(list_private))
print "Deleting files count: {}".format(len(list_delete))

print "Starred files: {}".format(list_starred)
print "Total size to be cleaned: {}".format(delete_size)

def call_delete(delete_list):
    global token
    api_files_delete = 'https://slack.com/api/files.delete'

    list_success = []
    list_fail = []

    for f in delete_list:
        data = {'token': token, 'file': f}
        response = requests.post(api_files_delete, data = data)

        if response.json()['ok'] == True:
            list_success.append(f)
            print "Deletion succeed: {}".format(f)
        else:
            list_fail.append(f)
            print "Deletion failed: {}".format(f)

    print "Succeed files count: {}".format(len(list_success))
    print "Failed files count: {}".format(len(list_fail))

    print "Failed files: {}".format(list_fail)


def call_report(num_delete, delete_size):
    json_channel = channel_id
    json_fallback = "슬랙 청소 결과"
    json_title = "슬랙 청소 결과"
    json_text = "슬랙에 올라온지 60일이 지난 *사진 파일* 들을 일괄 삭제 완료하였습니다\n*별표(star)* 되어있거나, *비공개 채널* 혹은 *DM* 에서 공유된 사진들은 삭제 대상에서 *제외* 되었습니다"
    json_value1 = num_delete
    json_value2 = delete_size

    requests.post(hook_url, json.dumps({
    "channel": json_channel,
    "username": bot_name,
    "attachments": [
        {
            "fallback": json_fallback,
            "title": json_title,
            "text": json_text,
            "mrkdwn_in": ["text"],
            "fields": [
                {
                    "title": "삭제된 사진 개수",
                    "value": json_value1,
                    "short": "true"
                },
                {
                    "title": "비워진 용량",
                    "value": json_value2,
                    "short": "true"
                }
            ],
            "color": "#1DAFED"
        }
    ]
    }))

# byte로 표기된 파일 크기를 사람이 읽을 수 있는 단위로 바꿈
suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def human_readable(nbytes):
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s%s' % (f, suffixes[i])

# 실행
call_delete(list_delete)
call_report(len(list_delete), human_readable(delete_size))
