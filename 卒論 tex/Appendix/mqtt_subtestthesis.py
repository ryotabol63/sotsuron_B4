# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import datetime
import random
import json
import csv

#for MQTT broker
MQTT_HOST = '127.0.0.1'
MQTT_PORT = 1883
KEEP_ALIVE = 60
TOPIC = 'TWELITE'


"""
接続を試みたときに実行
def on_connect(client, userdata, flags, respons_code):

* client
Clientクラスのインスタンス

* userdata
任意のタイプのデータで新たなClientクラスののインスタンスを作成するときに>設定することができる

* flags
応答フラグが含まれる辞書
クリーンセッションを0に設定しているユーザに有効。
セッションがまだ存在しているかどうかを判定する。
クリーンセッションが0のときは以前に接続したユーザに再接続する。

0 : セッションが存在していない
1 : セッションが存在している

* respons_code
レスポンスコードは接続が成功しているかどうかを示す。
0: 接続成功
1: 接続失敗 - incorrect protocol version
2: 接続失敗 - invalid client identifier
3: 接続失敗 - server unavailable
4: 接続失敗 - bad username or password
5: 接続失敗 - not authorised
"""
mqttlog_name = 'mqtt' + str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')) + '(' + str(random.randint(100, 999)) + ')' + '.csv'

header =['時間', '論理ID', 'タグID', '中継器ID', '送信番号', '電波強度', '電源電圧']

#ヘッダを定義し書き込む
with open(mqttlog_name,'a',encoding='shift_jis',newline='') as fw:
    csvout = csv.writer(fw)
    csvout.writerow(header)

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(client.topic)      #サブスクライブTOPICを指定

"""
def on_message(client, userdata, message):
topicを受信したときに実行する
"""
def on_message(client, userdata, message):
    nakami = message.payload
    message_json = nakami.decode('utf-8')                #受信データはバイト列なのでそれを文字列に変換する
    print (message_json)
    print (type(message_json))
    #print(message.topic + ' ' + str(message.payload))
    #message_json=str(message.payload)
    #message_json=my_removeprefix(message_json, "b'")
    #message_json=my_removesuffix(message_json, "'")
    #print(message_json.decode('utf-8'))
    with open(mqttlog_name, 'a', encoding='shift-jis',newline='') as f:
        wdata = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]) + ',' + message_json
        f.write(wdata + '\n')                        #すでにコンマ区切りされたデータなので単にwriteするだけ+改行


#受信データはプレフィックス，サフィックスデータを含むので除く

def my_removeprefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s

def my_removesuffix(s, suffix):
    return s[:-len(suffix)] if s.endswith(suffix) else s


if __name__ == '__main__':

    while 1:
        try:

            client = mqtt.Client(protocol=mqtt.MQTTv311)
            client.topic = TOPIC

            client.on_connect = on_connect
            client.on_message = on_message

            client.connect(MQTT_HOST, port=MQTT_PORT, keepalive=KEEP_ALIVE)

            # ループ（接続を維持する）
            client.loop_forever()       
        except KeyboardInterrupt:
            print('end')
            break                        