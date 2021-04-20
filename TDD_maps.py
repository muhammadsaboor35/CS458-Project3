import mpu
import math
import requests
from flask import Flask,request,render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

#Initialzing Flask app, config, and Google Maps
app = Flask(__name__)
app.config['GOOGLEMAPS_KEY'] = "Google Maps API key"
GoogleMaps(app)

@app.route('/')
def main_page():
	return render_template('main.html')
	
def parse_auto(request):
	#parse request to find out whether to use GPS or not
	if request.form['lat_input'] == '' and request.form['long_input'] == '':
		auto = True
	else:
		auto = False
	return auto
	
def parse_request(request):
	#parse string into floats
	try:
		lat=float(request.form['lat_input'])
	except:
		lat = None
	try:
		long=float(request.form['long_input'])
	except:
		long = None
	return lat, long
	
@app.route('/showCity')
def showCity():
	return render_template('ShowCityMap.html')

@app.route('/showCity', methods=['POST'])
def showCity_post():
	#parsing request added in refactoring 
	lat, long = parse_request(request)
		
	city = None
	if lat is None or long is None:
		city = "Invalid Coordinates"
	else:
		city = getCity(lat, long)
		if city is None:
			city = "No City Found!"
	return render_template('ShowCityMap.html', lat=lat, lng=long, city=city)
	
def getCity(lat,long):
	#perform Google Maps API request
	URL = 'https://maps.googleapis.com/maps/api/geocode/json'
	PARAMS = {'latlng':str(lat) + ',' + str(long),'key':app.config['GOOGLEMAPS_KEY']}
	r = requests.get(url = URL, params = PARAMS)
	results = r.json()['results']
	
	#Important attributes to find in the response
	order = ['locality', 'administrative_area_level_2','administrative_area_level_1']
	if len(results) > 0:
		addr_components = results[0]['address_components']
		if len(addr_components) > 0:
			for x in addr_components:
				types = x['types']
				for t in types:
					if t in order :
						return x['long_name']
			return None
		else:
			return None
	else:
		return None

@app.route('/nearestCity')
def showNearestCityDistance():
	return render_template('ShowNearestCityDistanceMap.html', auto=False)
	
@app.route('/nearestCity', methods=['POST'])
def showNearestCityDistance_post():
	#parsing request added in refactoring 
	auto = parse_auto(request)
	lat, long = parse_request(request)
	
	distance = None
	lat2 = None
	long2 = None
	city = None
	if lat is not None and long is not None:
		distance,lat2,long2,city = getDistanceOfNearestCity(lat,long)
	#Rounding off the distance
	if distance is not None:
		distance = str(round(distance, 3)) + " km"
	if distance is None:
		distance = "Invalid Coordinates"
		city = "Invalid Coordinates"
	return render_template('ShowNearestCityDistanceMap.html', lat1=lat, lng1=long, lat2=lat2, lng2=long2, city=city, distance=distance, auto=auto)

def getDistanceOfNearestCity(lat,long):					
	#getCity called during refactoring
	city_name = getCity(lat,long)
					
	if(long >= 0):
		long = "+" + str(long)
	else:
		long = str(long)
		
	#Perform GeoDB Cities API request
	url = "https://wft-geo-db.p.rapidapi.com/v1/geo/locations/" + str(lat) + str(long) + "/nearbyCities"
	headers = {
    'x-rapidapi-key': "Rapid API",
    'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
    }
	response = requests.request("GET", url, headers=headers)
	results = response.json()['data']
	
	if len(results) > 0:
		city = None
		for x in results:
			if city_name == x['city']:
				city = x['city']
				lat2 = x['latitude']
				long2 = x['longitude']
				break
		if city is None:
			city = results[0]['city']
			lat2 = results[0]['latitude']
			long2 = results[0]['longitude']
			
		#Calculate distance using haversine distance formula
		distance = mpu.haversine_distance((float(lat),float(long)),(float(lat2),float(long2)))
		return distance, lat2, long2, city
	else:
		return None, None, None, None

@app.route('/earthDistance')
def showEarthCenterDistance():
	return render_template('ShowEarthCenterDistanceMap.html', auto=False)
	
@app.route('/earthDistance', methods=['POST'])
def showEarthCenterDistance_post():
	#parsing request added in refactoring 
	auto = parse_auto(request)
	lat, long = parse_request(request)
	
	distance = None
	if lat is not None and long is not None:
		distance = getDistanceToEarth(lat,long)
		
	#rounding off the distance
	if distance is not None:
		distance = str(round(distance, 3)) + " km"
	if distance is None:
		distance = "Invalid Coordinates"
	return render_template('ShowEarthCenterDistanceMap.html', lat=lat, lng=long, distance=distance, auto=auto)
	
def getRadius(lat):
	#calculate geocentric radius
	cos_theta = math.cos(lat)
	sin_theta = math.sin(lat)
	a = 6378.1370 #equatorial radius
	b = 6356.7523 #polar radius
	num = (a*a*cos_theta)**2 + (b*b*sin_theta)**2
	den = (a*cos_theta)**2 + (b*sin_theta)**2
	radius = math.sqrt(num/den)
	return radius
	
def getDistanceToEarth(lat,long):
	#perform Google Maps Elevation API request
	URL = 'https://maps.googleapis.com/maps/api/elevation/json'
	PARAMS = {'locations':str(lat) + ',' + str(long),'key':app.config['GOOGLEMAPS_KEY']}
	r = requests.get(url = URL, params = PARAMS)
	results = r.json()['results']
	if len(results) > 0:
		elevation = results[0]['elevation']
	else:
		elevation = None
		
	#get geo centric radius
	radius = getRadius(lat)
	
	#convert to Kilometers
	if elevation is not None:
		return (elevation/1000) + radius
	return radius
	
if __name__ == "__main__":
	app.run(debug=True)
