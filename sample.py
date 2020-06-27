#!/usr/bin/python
import nswacv1

nswacv1.post(
	api=["cyberattackalarms",
		"malwarealarms",
		"targetedattackalarms"],
	csv=False,
	date="2020-06-23",
	time="08:00:00",
	range=180)
exit(0)
