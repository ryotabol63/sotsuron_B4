#!/usr/bin/env python
# coding: UTF-8

#################################################################
# Copyright (C) 2017 Mono Wireless Inc. All Rights Reserved.    #
# Released under MW-SLA-*J,*E (MONO WIRELESS SOFTWARE LICENSE   #
# AGREEMENT).                                                   #
#################################################################

# ライブラリのインポート
import sys
import csv
import os
import serial
import paramiko
import time
import datetime
from optparse import *

from time import sleep
#mqtt用のライブラリのインポート(paho-mqttパッケージが必要)
import paho.mqtt.client as mqtt

# WONO WIRELESSのシリアル電文パーサなどのAPIのインポート(TWELITE製造元・モノワイヤレス社のパルスクリプト参照)
sys.path.append('./MNLib/')
from apppal import AppPAL

# ここより下はグローバル変数の宣言
# コマンドラインオプションで使用する変数
options = None
args = None

# 各種フラグ
bEnableLog = False
bEnableErrMsg = False

# プログラムバージョン
Ver = "1.1.0"

# mqtt 接続----------------------------------------------------------
sys.stderr.write("*** 開始 ***\n")
host = '999.999.99.9'             #ブローカーのipアドレス（ipv4）を入れる
port = 1883                       #mqttではこのポートを使う
topic = 'TWELITE'                 #サブスクライバプログラムと同一のtopicにすることで送受信に成功する

client = mqtt.Client(protocol=mqtt.MQTTv311)

#mqttブローカーに接続，keepalive設定は設定秒数なにもこちらからの発信がなかったとしたらping確認をして，その応答がなければ通信が切断されたとみなして良いという設定
client.connect(host, port=port, keepalive=60) 
#上記のkeepalive設定により送られるping確認に応答する設定
client.loop_start()

header =['時間', '論理ID', 'タグID', '中継器ID', '送信番号', '電波強度', '電源電圧']
#送信データはこのように並ぶ（辞書データ）


# ------------------------------------------------------------------


#CSVを開く（送信側でのログ）

shortlog_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')) + '.csv'

print(shortlog_name)

#データを取得するメイン部分。newline=''は改行をなくすためのオプション

def writeX(note):
    with open(shortlog_name,'a',encoding='shift_jis',newline='') as f:
        csvout = csv.writer(f)
        csvout.writerow(note)

#ここから先はパルスクリプト（TWELITE製造元のプログラム）を改変

def ParseArgs():
    global options, args

    parser = OptionParser()
    parser.add_option('-t', '--target', type='string', help='target for connection', dest='target', default=None)
    parser.add_option('-b', '--baud', dest='baud', type='int', help='baud rate for serial connection.', metavar='BAUD', default=115200)
    parser.add_option('-s', '--serialmode', dest='format', type='string', help='serial data format type. (Ascii or Binary)',  default='Ascii')
    parser.add_option('-l', '--log', dest='log', action='store_true', help='output log.', default=False)
    parser.add_option('-e', '--errormessage', dest='err', action='store_true', help='output error message.', default=False)
    (options, args) = parser.parse_args()


if __name__ == '__main__':
    print("*** MONOWIRELESS App_PAL_Viewer " + Ver + " ***")

    writeX(header)

    ParseArgs()

    bEnableLog = options.log
    bEnableErrMsg = options.err
    try:
        PAL = AppPAL(port=options.target, baud=options.baud, tout=0.05, sformat=options.format, err=bEnableErrMsg)
    except:
        print("Cannot open \"AppPAL\" class...")
        exit(1)

    while True:
        try:
            # データがあるかどうかの確認
            if PAL.ReadSensorData():
                # あったら辞書を取得する
                Data = PAL.GetDataDict()
                if Data['RouterSID'] == '80000000':
                    RSID = 'No Relay'
                else:
                    RSID = Data['RouterSID']
                print(Data)
                print(Data['ArriveTime'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], end = ",")
                print(Data['LogicalID'], end = ",")
                print(Data['EndDeviceSID'], end = ",")
                print(RSID, end = ",")
                print(Data['SequenceNumber'], end = ",")
                print(Data['LQI'], end = ",")
                print(Data['Power'], end = "\n")

                # なにか処理を記述する場合はこの下に書く

                #辞書型で取られたシリアルポート（MONOSTICK）からのデータから必要なものを抜粋する
                datas_TAG = [str(Data['ArriveTime'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]),\
                Data['LogicalID'],Data['EndDeviceSID'],RSID,Data['SequenceNumber'],Data['LQI'],Data['Power']]
                
                #本稿で説明している方法では時間はブローカー，サブスクライバ側のものを使用するので
                #上記のデータからさらに取得時間のデータを除く
                send_datas_TAG = [\
                        #str(Data['ArriveTime'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]),\
                Data['LogicalID'],Data['EndDeviceSID'],RSID,Data['SequenceNumber'],Data['LQI'],Data['Power']]

                writeX(datas_TAG)                   #送信側ログには時間データも必要なのでdatas_TAGを書き込む
    
                #パブリッシュ用データはsend_datas_TAG，こちらもカンマ区切りテキストにしてパブリッシュ
                client.publish(topic, ",".join(map(str, send_datas_TAG)))

                
                # ここまでに処理を書く

                # ログを出力するオプションが有効だったらログを出力する。
                if bEnableLog == True:
                    PAL.OutputCSV()	# CSVでログをとる
            # Ctrl+C でこのスクリプトを抜ける
        except KeyboardInterrupt:
            break
    del PAL


    print("*** Exit App_PAL Viewer ***")
client.disconnect()             #接続を終了する