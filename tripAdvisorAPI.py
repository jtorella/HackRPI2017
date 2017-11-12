from urllib.request import Request, urlopen, URLError
import json
import pickle
import string

#this is just messing around to understand how the trip advisor api works.

def parseLatLon(googleJSON):
    data = json.loads(googleJSON)
    latLonPair = (data['results'][0]['geometry']['location'])
    lat = str(latLonPair['lat'])
    lon = str(latLonPair['lng'])
    return lat,lon


f=open("keys.txt",'r')
key = (f.read())
f.close()
print ("yuuhh")
googleMaps='AIzaSyAOg6tjxblKqni2RL2r5rDrVPAnU0vnvME'
request = True
grequest = True
#
def generateInfo(dataTuples):
    sz = len(dataTuples)
    i=0
    while i<sz:
        mapRequest = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="+dataTuples[i][0].replace(' ','+')+"+"+\
            dataTuples[i][1]+"&key="+googleMaps
        area=dataTuples[i][1].replace(' ','_')
        #FOR GOOGLE maps
        if(grequest is True):
            try:
                gresponse = urlopen(mapRequest)
                counties = gresponse.read()
        	#print (state)
            except URLError as e:
                print ('Error trying to do api request:', e)
            pickle.dump(counties,open(area+"GrawBostRests.p","wb"))
        else:
            counties = pickle.load(open(area+"GrawBostRests.p","rb"))

        lat,lon=parseLatLon(counties)

        testrequestLine = "http://api.tripadvisor.com/api/partner/2.0/map/"+lat+","+lon+"/restaurants?&distance=50&key="+key # grabs everything in boston

        if(request is True):
            try:
                response = urlopen(testrequestLine)
                state = response.read()
        	#print (state)
            except URLError as e:
                print ('Error trying to do api request:', e)

            info = json.loads(state)
            pickle.dump(state,open(area+"rawBostRests.p","wb"))
            pickle.dump(info,open(area+"bostonRests.p","wb"))
        else:
            raw = pickle.load(open(area+"rawBostRests.p","rb"))
            info = pickle.load(open(area+"bostonRests.p","rb"))
            counties = pickle.load(open(area+"GrawBostRests.p","rb"))
        #for x in info:
            #for y in info['data']:
            #    print("\nbeginning")
            #    print(y)
            #    print("end\n")
        #print (info)
        #Data and Paging available in map
        keys=["name","num_reviews","percent_recommended","rating","latitude","longitude","price_level","cuisine"]
        results={}
        for x in (info['data']):
            for y in keys:
                results[y]=x[y]
        info["medianIncomeForArea"]=dataTuples[i][2]
        pickle.dump(results,open(dataTuples[i][1].replace(' ','_'),'wb'))
        i+=1
    #print(counties)
    #raw = str(raw)
    #print(raw.split("\\n"))
    #print (data['data'])
