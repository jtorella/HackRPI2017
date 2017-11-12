from urllib.request import Request, urlopen, URLError
import json
import re
import pickle
import string
import tkinter
import matplotlib.pyplot as plt
import os.path
import numpy as np
import texttable as tt

income_code = "B19013_001E" #household income in the past year
median_code = "B01002_001E"

f=open("keys.txt",'r')
TAkey = (f.read())
f.close()
googleMaps='AIzaSyC-2jdvjnt7toifJSd1E_pmsJc4IGawPcI'
request = True
grequest = True

def get_key():
    file = "uscensuskey.txt"
    key=open(file, 'r')
    return key.read()

def parse_keys(data):
    data = data.decode('utf-8')
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
    data = data.decode('utf-8')

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
    data = data.decode('utf-8')
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

    return county_income


def parseLatLon(googleJSON):
    data = json.loads(googleJSON.decode('utf-8'))
    latLonPair = (data['results'][0]['geometry']['location'])
    lat = str(latLonPair['lat'])
    lon = str(latLonPair['lng'])
    return lat,lon


def generateInfo(dataTuples):
    sz = len(dataTuples)
    i=0
    while i<sz:
        if os.path.isfile(dataTuples[i][1].replace(' ','_') + '_' + dataTuples[i][0].replace(' ','_')):
            print(dataTuples[i][1] + " is already a file!!")
            i+=1
            continue

        request = True
        grequest = True
        mapRequest = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="+dataTuples[i][0].replace(' ','+')+"+"+\
            dataTuples[i][1].replace(' ','+')+"&key=" + googleMaps
        area=dataTuples[i][1].replace(' ','_') + "_" + dataTuples[i][0].replace(' ', '_')
        #FOR GOOGLE maps
        if(grequest is True):
            try:
                gresponse = urlopen(mapRequest)
                counties = gresponse.read()
        	#print (state)
            except URLError as e:
                print ('Error trying to do api request:', e)
            pickle.dump(counties,open(area+"GrawInfo.p","wb"))
        else:
            counties = pickle.load(open(area+"GrawInfo.p","rb"))

        lat,lon=parseLatLon(counties)

        testrequestLine = "http://api.tripadvisor.com/api/partner/2.0/map/"+lat+","+lon+"/restaurants?&distance=50&key="+TAkey # grabs everything in boston
        print(testrequestLine)
        if(request is True):
            try:
                response = urlopen(testrequestLine)
                state = response.read()
        	#print (state)
            except URLError as e:
                print ('Error trying to do api request:', e)

            info = json.loads(state.decode('utf-8'))
            pickle.dump(state,open(area+"rawInfo.p","wb"))
            pickle.dump(info,open(area+"info.p","wb"))
        else:
            raw = pickle.load(open(area+"rawInfo.p","rb"))
            info = pickle.load(open(area+"info.p","rb"))

        keys=["name","num_reviews","percent_recommended","rating","latitude","longitude","price_level","cuisine"]
        results={"name":[],"num_reviews":[],"percent_recommended":[],"rating":[],"latitude":[],"longitude":[],"price_level":[],"cuisine":[],"medianIncomeForArea":[]}

        for x in (info['data']):
            for y in keys:
                results[y].append(x[y])
            results["medianIncomeForArea"]=dataTuples[i][2]


        pickle.dump(results,open(dataTuples[i][1].replace(' ','_') + "_" + dataTuples[i][0].replace(' ', '_'),'wb'))
        i+=1

def generatePlots(dataTuples):
    keys=["name","num_reviews","percent_recommended","rating","latitude","longitude","price_level","cuisine","medianIncomeForArea"]

    x = []
    y = []
    tot=0
    pricelvl=False
    prct=True
    dataTuples=sorted(dataTuples,key=lambda x: int(x[2]))
    xlbls=[]
    clrs=np.arange(0,1.0,1.0/len(dataTuples))
    clrs_actual = []
    actClrs=[]
    j=0
    for tup in dataTuples:
        income = int(tup[2])
        county = tup[1]
        state = tup[0]
        pickle_data = pickle.load(open(county.replace(' ','_')+ '_' + state.replace(' ', '_'), "rb"))
        count = 0
        if(pricelvl == True):
            for levels in pickle_data['price_level']:

                if levels is None:
                    continue
                count+=1
                money_count = levels.count('$')
                if money_count == 5:
                    money_count = 2.5
                elif money_count == 3:
                    if '-' in levels:
                        money_count = 1.5

                y.append(money_count)
        elif(prct):
            for pcnt_rcmd in pickle_data["percent_recommended"]:
                if pcnt_rcmd is None:
                    continue
                count+=1
                y.append(int(pcnt_rcmd))
        i=0
        while i < count:
            x.append((income))
            xlbls.append(county + " "+str(income))
            clrs_actual.append(clrs[j])
            i+=1
        tot+=count
        j+=1

    plt.xticks(x,xlbls,rotation=90)
    plt.ylabel("% recommendation")
    plt.scatter(x,y,c=clrs_actual) #add clrs maybe
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.tight_layout()
    fig.savefig("testing.pdf")
    plt.show()



def generateHist(dataTuples):
    keys=["name","num_reviews","percent_recommended","rating","latitude","longitude","price_level","cuisine","medianIncomeForArea"]

    x = []
    y = []
    tot=0
    dataTuples=sorted(dataTuples,key=lambda x: int(x[2]))
    numCounties=len(dataTuples)
    ylbls=[]
    j=0
    for tup in dataTuples:
        income = int(tup[2])
        county = tup[1]
        state = tup[0]
        pickle_data = pickle.load(open(county.replace(' ','_')+ '_' + state.replace(' ', '_'), "rb"))
        count=0
        for rat in pickle_data["rating"]:
            if rat is None:
                continue
            count+=1
            x.append(int(round(float(rat))))
            y.append(income)
            ylbls.append(county + " "+str(income))

        tot+=count
        j+=1

    bins = [5+5,numCounties+5]
    plt.yticks(y,ylbls)
    #plt.ylabel("% recommendation")
    plt.hist2d(x,y,bins=bins) #add clrs maybe
    plt.colorbar()
    plt.margins(0.05)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.tight_layout()
    fig.savefig("testingHist.pdf")

    plt.show()

def generateTableHist(dataTuples):
    keys=["name","num_reviews","percent_recommended","rating","latitude","longitude","price_level","cuisine","medianIncomeForArea"]

    table = {}
    tot=0
    dataTuples=sorted(dataTuples,key=lambda x: int(x[2]))
    incomes=[]
    numCounties=len(dataTuples)

    j=0
    for tup in dataTuples:
        prcntRatings={1:0,2:0,3:0,4:0,5:0}
        county = tup[1]
        state = tup[0]
        pickle_data = pickle.load(open(county.replace(' ','_')+ '_' + state.replace(' ', '_'), "rb"))
        count=0
        for rat in pickle_data["rating"]:
            if rat is None:
                continue
            count+=1
            rating = (int(round(float(rat))))
            prcntRatings[rating]+=1
        for index in prcntRatings.keys():
            prcntRatings[index] = prcntRatings[index]/count
        table[county.replace(' ','_')]=prcntRatings
        incomes.append(float(tup[2]))
    tab = tt.Texttable()
    headings = ["County","Median Income:", "1 star %", "2 star %" , "3 star %", "4 star %", "5 star %"]
    tab.header(headings)
    i = 0
    for x in table.keys():
        row=[]
        row.append(x)
        row.append(incomes[i])
        for y in table[x].keys():
            row.append(100*table[x][y])
        tab.add_row(row)
        i+=1
    print(tab.draw())


if __name__ == "__main__":

    print("Please enter a state:")
    state = input().lower()


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
    	county = input().lower()

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
    generateInfo(county_incomes)
    generatePlots(county_incomes)
    generateHist(county_incomes)
    generateTableHist(county_incomes)
