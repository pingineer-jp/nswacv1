NII-SOCS Web-API ver1用のpythonクライアント
ver0.9


1. 動作環境の準備
動かすには本スクリプトとは別にWeb-APIのアカウントとPEM形式のクライアント証明書が必要。
実行前にホームディレクトリ( ~/ )直下に.nii-socsディレクトリを作成して、その中にクライアント証明書とconfigファイルを保存してください。
安全のためにconfigファイルとクライアント証明書は読み取り専用にした方が良いです。


1-1. ディレクトリ構成
以下の構成になります。
~/.nii-socs/
         ├ config
         └-クライアント証明書


1-2. configファイルのフォーマット
configファイル内には使用するクライアント証明書のファイル名とクレデンシャルを記述。
configファイルの記述形式は以下のようになります。

pem=クライアント証明書のファイル名
account=Web-APIのアカウント
password=Web-APIのパスワード



2. 実行
2-1. 動作環境
python3.7.3で動作確認


2-2. 実行方法
以下のpythonスクリプトを実行すると各Web-APIから情報を取得します。
・サイバー攻撃警報一覧
cyberattackalarms.py

・マルウェア警報一覧
malwarealarms.py

・標的型サイバー攻撃警報一覧
targetedattackalarms.py


2-3. 実行時オプションの説明
-v, --verbose
	詳細表示
	省略可能

-d, --date
	Web-APIのstartdattimeに設定する日付を設定
	2020-06-27 のようなYYYY-MM-DD形式で指定
	省略可能
	省略時は実行日で補完、rangeの値と矛盾する場合はrangeが優先される

-t, --time
	Web-APIのstartdattimeに設定する時刻を設定
	23:00:00 のようなHH:MM:DD形式で指定
	省略可能
	省略時はdateが実行日の場合は(実行時刻-range)もしくは(実行時刻-31分)の大きい方で補完
	dateが実行日以外の場合は00:00:00で補完

-r, --range
	Web-APIのtimeに設定する時間を設定
	0から180までの数値で指定
	省略可能
	省略時は180で補完


3. pythonから呼び出す場合
3-1. nswacv1.pyをインポート
import nswacv1


3-2. post関数を呼び出し
呼び出し例
nswacv1.post(
	api=["cyberattackalarms",
		"malwarealarms",
		"targetedattackalarms"],
	date="2020-06-23",
	time="08:00:00",
	range=180)

3-3. post関数の引数
api
	アクセスしたいWeb-APIをリスト形式で設定
	サイバー攻撃警報一覧はcyberattackalarms、マルウェア警報一覧はmalwarealarms、標的型サイバー攻撃警報一覧はtargetedattackalarmsを指定
	省略可能
	省略時は3種類のWeb-API全てを指定

date
	Web-APIのstartdattimeに設定する日付を設定
	2020-06-27 のようなYYYY-MM-DD形式で指定
	省略可能
	省略時は実行日で補完、rangeの値と矛盾する場合はrangeが優先される

time
	Web-APIのstartdattimeに設定する時刻を設定
	23:00:00 のようなHH:MM:DD形式で指定
	省略可能
	省略時はdateが実行日の場合は(実行時刻-range)もしくは(実行時刻-31分)の大きい方で補完
	dateが実行日以外の場合は00:00:00で補完

range
	Web-APIのtimeに設定する時間を設定
	0から180までの数値で指定
	省略可能
	省略時は180で補完
