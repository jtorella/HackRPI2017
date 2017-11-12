from urllib2 import Request, urlopen, URLError
import json
import re

income_code = "B19013_001E" #household income in the past year
median_code = "B01002_001E"

def get_key():
	file = "uscensuskey.txt"
	key=open(file, 'r')
	return key.read()

def parse_keys(data):
	data = data.replace('[', '')
	data = data.replace(']', '')
	data = data.replace('"', '')
	data = data.replace(',\n', '\n')

	data_list = data.split('\n')	
	code_map = {}

	for i in range(len(data_list)-1):
		line = data_list[i+1].strip(' ')
		loc, code = line.split(',')
		loc = loc.lower()
		code_map[loc] = code

	#allows user to specify all states for query
	code_map['*'] = '*' 

	return code_map

def parse_counties(data):
	data = data.replace('[', '')
	data = data.replace(']', '')
	data = data.replace('"', '')
	data = data.replace(',\n', '\n')

	data_list = data.split('\n')
	code_map = {}
	for i in range(len(data_list)-1):
		line = data_list[i+1].split(',')
		county = line[0].lower()
		code = line[3].lower()
		code_map[county] = code

	code_map['*'] = '*'	

	return code_map


def request_handler(url):
	request = Request(url)

	data = ""
	try:
		response = urlopen(request)
		data = response.read()

	except URLError as e:
		print("Something went wrong!")
		print("Got Error Code: ", e)

	return data

def ready_data(data):
	data = data.replace('[', '')
	data = data.replace(']', '')
	data = data.replace('"', '')
	data = data.replace(',\n', '\n')

	data_list = data.split('\n')
	county_income = []

	for i in range(len(data_list)-1):
		line = data_list[i+1].split(',')
		income = line[0]
		county = line[1]
		state = line[2].strip()

		county_income.append((state, county, income))

	print(county_income)
	return county_income


if __name__ == "__main__":

	print("Please enter a state:")
	state = raw_input().lower()
	

	key = get_key()

	#get state codes
	state_data = request_handler('https://api.census.gov/data/2016/acs/acs1?get=NAME&for=state:*&key='+key)
	state_codes = parse_keys(state_data)
	

	if state not in state_codes:
		print("Error! Unrecognized state: " + state)
		exit(0)

	county_codes = {}
	county_data = request_handler('https://api.census.gov/data/2016/acs/acs1?get=NAME&for=county:*&in=state:' + state_codes[state] + '&key=' + key)
	county_codes = parse_counties(county_data)

	county = ""
	if state != '*':
		print("\nHere are the counties in " + state + ":")
		counties_list = []
		for x in county_codes:
			if x == '*':
				continue;
			counties_list.append(x)

		counties_list.sort()
		for x in counties_list:
			print(x)
		

		print("\nPlease enter a county:")
		county = raw_input().lower()

	if county != "" and county != '*':
		county += ' county'

	if county != "":
		request = Request('https://api.census.gov/data/2016/acs/acs1?get=' + income_code + ',NAME&for=county:' + county_codes[county] + '&in=state:' + state_codes[state] + '&key='+key)
	else:
		request = Request('https://api.census.gov/data/2016/acs/acs1?get=' + income_code + ',NAME&for=state:' + state_codes[state] + '&key='+key)

	data = ""
	try:
		response = urlopen(request)
		data = response.read()

	except URLError as e:
		print("Something went wrong!")
		print("Got Error Code: ", e)


	county_incomes = ready_data(data) 

	

