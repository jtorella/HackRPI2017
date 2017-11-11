# HackRPI2017
Hackathon Project for HackRPI 2017

<<<<<<< HEAD
key="957e54c54c466948f418a4fb06de33bb044fe859"

state = ""
request2 = Request('http://api.census.gov/data/2016/acs/acs1?get=NAME,B01001_001E&for=state:*&key='+key)

try:
	response = urlopen(request2)
	state = response.read()
	print (state)
except URLError, e:
    print 'No kittez. Got an error code:', e
=======
https://www.census.gov/data/developers/guidance/api-user-guide.Query_Examples.html
>>>>>>> origin/master
