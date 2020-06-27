#!/bin/sh

# サイバー攻撃警報一覧の取得
python cyberattackalarms.py -v -d 2020-06-23 -t 09:00:00 -r 180
sleep(1)

# マルウェア警報一覧の取得
python malwarealarms.py -v -d 2020-06-23 -t 09:00:00 -r 180
sleep(1)

# 標的型サイバー攻撃警報一覧の取得
python targetedattackalarms.py -v -d 2020-06-23 -t 09:00:00 -r 180
