#!/usr/bin/python
import time
import re
import requests
from bs4 import BeautifulSoup as bs
import smtplib
from email.mime.text import MIMEText

styles = {
	'toyota' : {
		'camry' : {
			'2013': {'LE': '200444384', 'SE': '200444386',  'XLE': '200444385', 'default_style': '200444384'},
			'2012': {'LE': '101403728', 'SE': '101403729',  'XLE': '101403734', 'default_style': '101403728'},
			'2011': {'LE': '101275054', 'SE': '101275056',  'XLE': '101275058', 'default_style': '101275054'},
			'2010': {'LE': '101147478', 'SE': '101147480',  'XLE': '101147482', 'default_style': '101147478'},
			'2009': {'LE': '100975557', 'SE': '100975559',  'XLE': '100975561', 'default_style': '100975557'},
			'2008': {'CE':'100900019','LE':'100900021','SE':'100900023','XLE':'100900043','default_style':'100900021'},
 			'2007': {'CE':'100699450','LE':'100699452','SE':'100699455','XLE':'100699453','default_style':'100699452'},
 			'2006': {'LE':'100566040','SE':'100566043','Standard':'100566037','XLE':'100566041','default_style':'100566040'}
		},
		'corolla' : {
			'2013': {'L':'200431095','LE':'200431097','S':'200431098','default_style':'200431097'},
			'2012': {'L':'101419637','LE':'101419638','S':'101419640','default_style':'101419638'},
			'2011': {'Base':'101372440','LE':'101372441','S':'101372443','default_style':'101372441'},
			'2010': {'Base':'101140838','LE':'101140839','S':'101140841','XLE':'101140842','XRS':'101140844','default_style':'101140839'},
			'2009': {'Base':'100980400','LE':'100980401','S':'100980404','XLE':'100980405','XRS':'100980407','default_style':'100980401'},
			'2008': {'CE':'100884946','LE':'100884950','S':'100884948','default_style':'100884950'},
			'2007': {'CE':'100773492','LE':'100773496','S':'100773494','default_style':'100773496'},
			'2006': {'CE':'100578063','LE':'100578067','S':'100578065','default_style':'100578067'}
		}
	}
}

def get_ksl_id(link) :
	return link[link.rfind('/')+1:link.find('?')]

def get_ksl_spec (car_specs, spec_name) :
	for spec in car_specs:
		if spec.select('td')[0].text.find(spec_name) >= 0 :
			return str(spec.select('td')[1].text).strip()
	print 'spec not found ', spec_name
	return ""

def get_ksl_price (car) :
	price = str(car.select('.price')[0].text).strip()
	return price[:-2]

def get_ksl_title (car) :
	return str(car.select('.title')[0].text).strip()


def get_ksl_info (car_id) :
	print 'requesting ksl car', car_id
	car_request = bs(requests.get('http://www.ksl.com/auto/listing/' + car_id).text)
	car_specs = car_request.select('#specificationsTable tr')

	return {
		'url': 'http://www.ksl.com/auto/listing/' + car_id,
		'ksl_id': car_id,
		'year': get_ksl_spec(car_specs, 'Year'),
		'mileage' : get_ksl_spec(car_specs, 'Mileage'),
		'color' : get_ksl_spec(car_specs, 'Exterior Color').lower(),
		'vin' : get_ksl_spec(car_specs, 'VIN'),
		'make' : get_ksl_spec(car_specs, 'Make').lower(),
		'model' : get_ksl_spec(car_specs, 'Model').lower(),
		'title_type' : get_ksl_spec(car_specs, 'Title Type'),
		'price' : get_ksl_price(car_request),
		'title' : get_ksl_title(car_request)
	}

def get_velocity_id(car_url) :
	return car_url[len('/web/used/') : len(car_url)-1]

def get_velocity_spec(car_specs, spec_name) :
	for spec in car_specs:
		spec_label = spec.select('strong')
		# print str(spec_label[0].text).strip()
		if len(spec_label) > 0:
			cur_spec_name = (spec_label[0].text).lower()
			cur_spec_name = cur_spec_name[:cur_spec_name.find(':')]
			if cur_spec_name == spec_name.lower():
				for child in spec.children:
					child.extract()
				return str(spec.text).strip()
	return ''

def get_velocity_title(car_request) :
	print car_request.select('#vehicle_title')
	return str(car_request.select('#vehicle_title')[0].text).strip()

def get_velocity_price(car_request) :
	return str(car_request.select('.price_line_1')[0].text).strip()

def get_velocity_year(title) :
	for word in title.split() :
		if word < '2015' and word > '2000':
			return word
	return ''

def get_velocity_make(title) :
	for word in title.lower().split() :
		if styles.has_key(word) :
			return word
	return ''

def get_velocity_model(make, title) :
	for word in title.lower().split() :
		if len(make) > 0 and styles[make] and styles[make].has_key(word) :
			return word
	return ''


def get_velocity_info(car_id) :
	print 'requesting velocity car', car_id
	car_request = bs(requests.get('http://www.velocitycars.com/web/used/' + car_id).text)
	car_specs = car_request.select('#vitalsLeft > ul > li') + car_request.select('#vitalsRight > ul > li')

	car_title = get_velocity_title(car_request)
	make = get_velocity_make(car_title)

	return {
		'url': 'http://www.velocitycars.com/web/used/' + car_id,
		'velocity_id': car_id,
		'year': get_velocity_year(car_title),
		'mileage' : get_velocity_spec(car_specs, 'Mileage'),
		'color' : get_velocity_spec(car_specs, 'Exterior'),
		'vin' : get_velocity_spec(car_specs, 'VIN #'),
		'make' : make,
		'model' : get_velocity_model(make, car_title),
		'title_type' : 'clean',
		'price' : get_velocity_price(car_request),
		'title' : car_title
	}



def get_edmunds_style(car) :
	if styles[car['make']] and styles[car['make']][car['model']] and styles[car['make']][car['model']][car['year']] :
		car_styles = styles[car['make']][car['model']][car['year']]
		words = car['title'].split()
		for key in car_styles :
			for word in words :
				if word == key :
					print 'found style for ', car['make'], car['model'], car['year'], car_styles[key]
					return car_styles[key]
		return car_styles['default_style']
	else :
		print 'no style found for car ', car['make'], car['model'], car['year']
		return 'no style'

def get_edmunds_tmv(car) :
	print 'requesting tmv', car['make'], car['model'], car['year']
	tmv_url = 'http://www.edmunds.com/' + car['make'] + '/' + car['model'] + '/' + car['year'] + '/tmv-appraise-results.html'
	payload = {
		'style': get_edmunds_style(car),
		'category': 'sedan',
		'zip': '84606',
		'color': 'GENERIC_Black',
		'mileage': car['mileage'],
		'condition': 'clean'}
	s = requests.session()
	response = s.post(tmv_url, data=payload)
	content = bs(response.text)
	tmv = str(content.select('.tmv-price-details')[1].text).strip() # this should be the 1st on edmunds?
	return tmv

def price_to_int(price) :
	p = re.compile(r'[^\d]')
	return int(''.join(p.split(price)))

def get_tmv_price_diff(car) :
	if len(car['tmv']) == 0 or len(car['price']) == 0:
		return 0
	return price_to_int(car['tmv']) - price_to_int(car['price'])

def interested_in_car(car) :
	return car['year'] >= '2008' and car['title_type'].lower().find('rebuilt') < 0 and car['title_type'].lower().find('reconstructed') < 0

save_file = open('cars.txt', 'a+')

ksl_url = 'http://www.ksl.com/auto/search/index?o_facetClicked=true&o_facetValue=8000%2C14000&o_facetKey=priceFrom%2C+priceTo&resetPage=true&keyword=&make%5B%5D=Toyota&model%5B%5D=Camry&model%5B%5D=Corolla&yearFrom=2008&yearTo=2014&priceFrom=8000&priceTo=14000&mileageFrom=1&mileageTo=60000&zip=84095&miles=50'
# ksl_url = 'http://www.ksl.com/auto/search/index?o_facetClicked=true&o_facetValue=8000%2C14000&o_facetKey=priceFrom%2C+priceTo&resetPage=true&keyword=&make%5B%5D=Toyota&model%5B%5D=Camry&yearFrom=2008&yearTo=2014&priceFrom=8000&priceTo=14000&mileageFrom=1&mileageTo=60000&zip=84095&miles=50'
velocity_camry_url = 'http://www.velocitycars.com/web/inventory/All_years/Toyota/Camry/All_body_types/All_vehicles/'

vins = {}
ksl_ids = {}
velocity_ids = {}
cars = []
new_cars = []

#read file & load vins & ids
cars_str = save_file.readline()
if cars_str.find('[') > -1 :
	cars = eval(cars_str)

start_time = time.strftime("%y/%m/%d %H:%M")

for car in cars :
	if car.has_key('vin') :
		vins[car['vin']] = True
	if car.has_key('ksl_id') :
		ksl_ids[car['ksl_id']] = True
	if car.has_key('velocity_id') :
		velocity_ids[car['velocity_id']] = True


#find all ksl cars
print 'requesting ksl list'
r = requests.get(ksl_url)
content = bs(r.text)

for car in content.select('.srp-listing-body') :
	car_id = get_ksl_id(car.select('.srp-listing-title a')[0]['href'])

	if not ksl_ids.has_key(car_id):
		car_info = get_ksl_info(car_id)
		ksl_ids[car_id] = True

		if (not vins.has_key(car_info['vin'])) and car_info['year'] >= '2008' :
			car_info['tmv'] = get_edmunds_tmv(car_info)
			car_info['tmv_price_diff'] = get_tmv_price_diff(car_info)
			car_info['save_time'] = start_time
			cars.append(car_info)
			new_cars.append(car_info)
			vins[car_info['vin']] = True
			print 'new car', car_info

#find all velocity cars
print 'requesting velcoity cars list'
r = requests.get(velocity_camry_url)
content = bs(r.text)

for car in content.select('.inventory_v2_row') :
	car_url = 'http://velocitycars.com/' + car.select('a.color_pri')[0]['href']
	car_id = get_velocity_id(car.select('a.color_pri')[0]['href'])

	if not velocity_ids.has_key(car_id) :
		car_info = get_velocity_info(car_id)
		if (not vins.has_key(car_info['vin'])) and car_info['year'] >= '2008' :
			car_info['tmv'] = get_edmunds_tmv(car_info)
			car_info['tmv_price_diff'] = get_tmv_price_diff(car_info)
			car_info['save_time'] = start_time
			cars.append(car_info)
			new_cars.append(car_info)
			vins[car_info['vin']] = True
			print 'new car', car_info
save_file.close()
save_file = open('cars.txt', 'w+')

save_file.write(str(cars))

save_file.close()


# NOTE: If you want to send an email, uncomment this last part and add in your email.
# Warning: many Internet Service Providers block sending emails from localhost. You may need to set this up to use a non-localhost email account.

# to_email = ''
# if len(new_cars) > 0:
# 	s = smtplib.SMTP('localhost')
# 	msg_text = '<style>td,th{text-align:left;}</style><h2>New Cars</h2><table><tr><th>Price</th><th>TMV</th><th>TMV-Price</th><th>Year</th><th>Mileage</th><th>Model</th><th>Title</th><th>Color</th></tr>'
# 	for car in new_cars :
# 		msg_text += '<tr><td><a href="' + car['url'] + '">' + str(car['price']) + '</a></td><td>' + car['tmv'] + '</td><td>' + str(car['tmv_price_diff']) + '</td><td>' + car['year'] + '</td><td>' + car['mileage'] + '</td><td>' + car['model'] + '</td><td>' + car['title_type'] + '</td><td>' + car['color'] + '</td></tr>'
# 	msg_text += '</table>'

# 	msg_text += '<h2>All Cars</h2><table><tr><th>Price</th><th>TMV</th><th>TMV-Price</th><th>Year</th><th>Mileage</th><th>Model</th><th>Title</th><th>Color</th></tr>'
# 	for car in cars :
# 		print car
# 		msg_text += '<tr><td><a href="' + car['url'] + '">' + str(car['price']) + '</a></td><td>' + car['tmv']+ '</td><td>' + str(car['tmv_price_diff']) + '</td><td>' + car['year'] + '</td><td>' + car['mileage'] + '</td><td>' + car['model'] + '</td><td>' + car['title_type'] + '</td><td>' + car['color'] + '</td></tr>'
# 	msg_text += '</table>'


# 	msg = MIMEText(msg_text, 'html')
# 	msg['Subject'] = 'New Car Listing From Script'
# 	msg['From'] = 'cars'
# 	msg['To'] = to_email
# 	print('sending email')
# 	s.sendmail('me@localhost', [to_email], msg.as_string())