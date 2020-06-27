#!/bin/sh
mkdir ~/.nii-socs
cat - << EOS  > ~/.nii-socs/config
pem=PEM形式のクライアント証明書
account=Web-APIのアカウント名
password=Web-APIのパスワード
EOS

chmod 700 ~/.nii-socs
chmod 400 ~/.nii-socs/config
