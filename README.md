# HackRPI2017
Hackathon Project for HackRPI 2017

key="?"

state = ""
request2 = Request('http://api.census.gov/data/2016/acs/acs1?get=NAME,B01001_001E&for=state:*&key='+key)

try:
	response = urlopen(request2)
	state = response.read()
	print (state)
except URLError, e:
    print 'Error getting url, probably a key issue', e
