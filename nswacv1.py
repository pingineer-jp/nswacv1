import os
import sys
import json
import time
from requests import Session
import datetime
import urllib.parse
from logging import getLogger, StreamHandler, DEBUG

class Disp():
	verbose = False
	csv = False
	def print(self,text):
		print("%s: %s"%(MYNAME, text))

	def stderr(self,text):
		print("%s: Error[%s]"%(MYNAME,text), file=sys.stderr)
		sys.exit(1)
	
	def showUsage(self):
		print('Usage: python %s [--verbose] [--csv] [--date <YYYY-MM-DD>] [--time <HH:MM:SS>] [--range <0-180>] [--help]'%(MYNAME))
		sys.exit(0)

	def cmdErr(self, text):
		print(text, file=sys.stderr)
		sys.exit(1)

	def debug(self,text):
		logger.debug("%s: %s", MYNAME, text)

	def resDebug(self,text):
		logger.debug("Web-API: %s", text)

	def vCredential(self,config):
		if self.verbose == True:
			print("-------------- 認証情報 --------------")
			print("証明書: %s"%(config["pem"]))
			print("account: %s"%(config["account"]))
			print("password: %s"%("*"*len(config["password"])))

	def vParam(self,api,startDateTime,range):
		if self.verbose == True:
			print("---------- クエリパラメータ ----------")
			print("api: %s"%(api))
			print("startdatetime: %s"%(startDateTime))
			print("time: %d"%(range))
			print("--------------------------------------")

	def vRes(self, text):
		if self.verbose == True:
			print("> %s"%(text))

	def vReq(self, text):
		if self.verbose == True:
			print("< %s"%(text))

	def printResult(self, resJson):
		if not self.csv:
			print(resJson)
		else:
			resDict =json.loads(resJson)
			self.recursiveDictShaping(resDict)

	def recursiveDictShaping(self,resDict):
		# 再帰処理で結果のリストに到達するまで進める
		for key in resDict:
			if isinstance(resDict[key],dict):
				disp.vRes("%s: "%(key))
				self.recursiveDictShaping(resDict[key])
			else:
				for apiResult in ["cyberAttackAlarmList", "malwareAlarmList", "targetedAttackAlarmList"]:
					if key == apiResult:
						# 結果が収まったkeyに到達したので処理を変える
						self.resultList(resDict[key])
						return
				if self.verbose:
					self.vRes("%s: %s"%(key, resDict[key]))

	def resultList(self,resList):
		keyList=[]
		valueList=[]
		# まずヘッダーとしてkeyの一覧だけ取得して出力
		for res in resList:
			for key in res:
				keyList.append(key)
			break
		print(",".join(keyList))
		# 再度ループを回してvalueだけ出力
		if keyList is not None:
			for res in resList:
				for key in res:
					valueList.append(res[key])
				valueList = [str(i) for i in valueList]
				print(",".join(valueList))

class Config():
	def __init__(self):
		# コンフィグデータの読み込み
		self.readConfig()
		# 必要なコンフィグデータがあるか確認
		self.checkConfig()
		# 必要なコンフィグデータだけ抽出して整形
		self.shapingConfig()


	def readConfig(self):
		# configファイルの読み込み
		self.config = {}
		with open(CONFIG_FILE) as f:
			s = f.read().rstrip()
			# パラメータごとに辞書型で格納
			self.config2dict(s.split("\n"))


	def config2dict(self,configLine):
		# パラメータごとに辞書型で格納
		for tmp in configLine:
			try:
				key, value = tmp.split("=")
				self.config[key] = value
			except:
				disp.debug("Warning(Invalid config paramerter.)")


	def checkConfig(self):
		# 必要なコンフィグデータがあるか確認
		for key in ["pem","account","password"]:
			if not key in self.config:
				dip.stderr("No valid %s)"%(key))


	def shapingConfig(self):
		# クライアント証明書のパス
		self.pem = CONFIG_DIR + self.config["pem"]

		# クレデンシャルの整形
		self.authJson = json.dumps(
			{"auth":
				{"account" :self.config["account"],
				 "password":self.config["password"]
				}
			})
		# verboseの時はクレデンシャル等を表示
		disp.vCredential(self.config)
		# 整形済みの値を取得してもう不要なので削除
		del self.config
		# クレデンシャルの表示
		#disp.debug("Credential = %s"%(self.authJson))
		

class UrlQueryParameter():
	date = None
	time = None
	def checkParam(self,param):
		# POSTするapiをセット
		self.setApi(param)
		# 時間をセット
		self.setRange(param)
		# 日付と時刻のパラメータをチェック
		for type in ["date","time"]:
			self.checkDate(type, param)
		# 日付と時刻をセット
		self.setDateTime()

	def setApi(self,param):
		self.api = []
		# Web-APIのリスト
		apiList =["cyberattackalarms", "malwarealarms", "targetedattackalarms"]
		# apiが引数として与えられなかった場合は3種類のapi全てをセット
		if not "api" in param or param is None:
			self.api = apiList
			return
		# 引数として渡されたapiをチェック
		flag=False
		for api in apiList:
			for tmp in param["api"]:
				if tmp == api:
					self.api.append(api)
					flag=True
		if not flag:
			disp.stderr("Invalid api(%s)"%(param["api"]))


	def setRange(self,param):
		# 時間が引数として与えられなかった場合は180をセット
		if not "range" in param or param is None:
			self.range = 180
			return
		# 時間が有効範囲内か確認
		if param["range"] >= 0 and param["range"] <= 180:
			self.range = param["range"]
		else:
			disp.stderr("Invalid range(%s)"%(param["range"]))


	def checkDate(self,type,param):
		if not type in param:
			return
		if param[type] is None or param[type] == "":
			return
		# 日付と時刻のフォーマットが合っているか確認
		if not self.checkDateFormat(type,param[type]):
			disp.stderr("Invalid %s(%s)"%(type,param[type]))
		else:
			exec('self.%s = param["%s"]'%(type,type))


	def checkDateFormat(self,type,dateTime):
		# 日付と時刻のフォーマットが合っているか確認
		try:
			if type == "date":
				# 日付のフォーマットチェック
				date=datetime.datetime.strptime(dateTime,"%Y-%m-%d")
				self.date = dateTime
				return True
			elif type == "time":
				# 時刻のフォーマットチェック
				date=datetime.datetime.strptime(dateTime,"%H:%M:%S")
				self.time = dateTime
				return True
			return False
		except ValueError:
			return False


	def setDateTime(self):
		if self.date is not None and self.time is not None:
			# 日付と時刻と両方セットされていた場合
			self.startDateTime = "%sT%s"%(self.date, self.time)
		elif self.date is None and self.time is not None:
			# 時刻だけセットされていた場合
			self.createDate()
		elif self.date is not None and self.time is None:
			# 日付だけセットされていた場合
			self.createTime()
		else:
			# 日付も時刻もセットされていなかった場合
			self.createDateTime()


	def createDate(self):
		# 日付が与えられていないので矛盾がないように作成してセット
		now = datetime.datetime.now()
		rangeSeconds = self.range * 60
		if rangeSeconds >= WAIT:
			td = datetime.timedelta(seconds=rangeSeconds)
		else:
			td = datetime.timedelta(seconds=WAIT)
		diffDate = now - td
		date=datetime.datetime.strptime(diffDate.strftime("%Y-%m-%d") + " " + self.time, "%Y-%m-%d %H:%M:%S")
		if diffDate <= date:
			td = datetime.timedelta(days=1)
			date = date - td
		self.startDateTime = date.strftime("%Y-%m-%dT%H:%M:%S")


	def createTime(self):
		# 時刻が与えられていないので矛盾がないように作成
		now = datetime.datetime.now()
		today=now.replace(hour=0,minute=0,second=0,microsecond=0)
		date=datetime.datetime.strptime(self.date, "%Y-%m-%d")
		if today == date:
			rangeSeconds = self.range * 60
			if rangeSeconds >= WAIT:
				td = datetime.timedelta(seconds=rangeSeconds)
			else:
				td = datetime.timedelta(seconds=WAIT)
			date = now - td
		self.startDateTime = date.strftime("%Y-%m-%dT%H:%M:%S")


	def createDateTime(self):
		now = datetime.datetime.now()
		rangeSeconds = self.range * 60
		if rangeSeconds >= WAIT:
			td = datetime.timedelta(seconds=rangeSeconds)
		else:
			td = datetime.timedelta(seconds=WAIT)
		date = now - td
		self.startDateTime = date.strftime("%Y-%m-%dT%H:%M:%S")


class NiiSocsWebApiV1Client():
	BASE_URL = 'https://portal.soc.nii.ac.jp/ada/api/v1/'
	def postQuery(self,pem,authJson,url):
		# Web-APIへPOST
		session = Session()
		# クライアント証明書の指定
		session.cert = pem
		# Web-APIへPOST
		res = session.post(url, authJson,
					headers={'Content-Type': 'application/json'})
		self.response(res)

	def response(self,res):
		disp.resDebug("Response status code = %s"%(res.status_code))
		resList = {200:"情報取得に成功しました",
								206:"情報取得に成功しました(応答上限超過のため破棄された情報があります",
								400:"入力パラメータが不正です",
								401:"パスワード認証に失敗しました",
								403:"APIの利用が許可されていません",
								500:"サーバでの処理に失敗しました",
								503:"リソースビジーによりタイムアウトしました"}
		if res.status_code == 200:
			disp.vRes(resList[res.status_code])
		else:
			disp.stderr("Web-API Error(%s)"%(resList[res.status_code]))
		disp.printResult(res.text)

	def createUrl(self,api,startDateTime,range):
		disp.vParam(api,startDateTime,range)
		url = "%s%s?startdatetime=%s&time=%d"%(self.BASE_URL,api,urllib.parse.quote(startDateTime),range)
		disp.vReq(url)
		disp.debug("URL(%s)"%(url))
		return url


logger = getLogger(__name__)
handler = StreamHandler()
#handler.setLevel(DEBUG)
#logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

PATH = os.environ['HOME']
ENTITY_NAME = "nswacv1"
MYNAME = os.path.splitext(os.path.basename(__file__))[0]

CONFIG_DIR_NAME = ".nii-socs"
CONFIG_FILE_NAME = "config"

CONFIG_DIR = "%s/%s/"%(PATH, CONFIG_DIR_NAME)
CONFIG_FILE = CONFIG_DIR + CONFIG_FILE_NAME

WAIT = 1860

# 表示用のクラス
disp = Disp()

API_LIST = ["cyberattackalarms", "malwarealarms", "targetedattackalarms"]


def post(**param):
	# コンフィグから必要な設定の読み込み
	config = Config()

	# Web-APIへPOSTするパラメータの準備
	uqp = UrlQueryParameter()
	uqp.checkParam(param)

	# Web-API用のクラス
	nswac = NiiSocsWebApiV1Client()
	# 指定されたWeb-API全てに実行
	for api in uqp.api[:]:
		# URLクエリを生成
		url = nswac.createUrl(api,uqp.startDateTime,uqp.range)
		# Web-APIへPOST
		nswac.postQuery(config.pem,config.authJson,url)
		# 複数のapiを叩く時は念のためにsleepを1秒挟んでおく
		if len(uqp.api) >1:
			time.sleep(1)
			uqp.api.remove(api)
	sys.exit(0)

def getOptions():
	argList = sys.argv
	# ファイル自身を指す最初の引数を除去
	argList.pop(0)
	# - で始まるoption
	options = [option for option in argList if option.startswith('-')]

	param = {"date":"","time":"","range":180, "verbose": False, "csv":False}

	if '-h' in options or '--help' in options:
		disp.showUsage()
	if '-v' in options or '--verbose' in options:
		param.update({"verbose":True})
	if '-c' in options or '--csv' in options:
		param.update({"csv":True})
	if '-d' in options or '--date' in options:
		date_position = argList.index('-d') \
	if '-d' in options else argList.index('--date')
		date = argList[date_position + 1]
		param.update({"date":date})
	if '-t' in options or '--time' in options:
		time_position = argList.index('-t') \
	if '-t' in options else argList.index('--time')
		time = argList[time_position + 1]
		param.update({"time":time})
	if '-r' in options or '--range' in options:
		range_position = argList.index('-r') \
	if '-r' in options else argList.index('--range')
		range = argList[range_position + 1]
		param.update({"range":int(range)})
	return param

if __name__ == '__main__':
	apiList = []
	# コマンドとして実行された時のファイル名をPOSTするapiとして設定
	for tmp in API_LIST:
		if MYNAME == tmp:
			 apiList.append(tmp)
	# 実体を直接コマンドとして実行された時は全てのAPIをPOSTする対象として設定
	if MYNAME == ENTITY_NAME:
		#apiList = ["cyberattackalarms", "malwarealarms", "targetedattackalarms"]
 		apiList = API_LIST

	# コマンドとして実行された時のオプション取得
	options = getOptions()
	disp.verbose = options["verbose"]
	disp.csv = options["csv"]
	disp.debug("Command option = %s"%(options))

	# シンボリックリンク名が変わってWeb-APIを選択できない時は実体ファイルを使うよう促して終了
	if len(apiList) == 0:
		disp.cmdErr("Invalid file name. Use %s"%(ENTITY_NAME))

	# コマンドとして実行された時のPOST処理の呼び出し
	post(api=apiList,date=options["date"],time=options["time"],range=options["range"])
	sys.exit(0)
