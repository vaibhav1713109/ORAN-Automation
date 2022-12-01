import json, httplib2

def notification(msg):
    url = 'https://chat.googleapis.com/v1/spaces/AAAA4XkxAB4/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=c8TU0zdl2uPLU4-HXMqYxsQAsrKdbHTZIgbeZk_SjxQ%3D'

    message = {'text' : msg}

    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

    http_obj = httplib2.Http()

    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=json.dumps(message),
    )
    return
    


