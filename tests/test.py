from selenium import webdriver
import time
import os
import coloredlogs, logging
import sys

fmt = '%(message)s'
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',logger=logger,fmt=fmt)

supported_os = ['Android', 'Windows']
supported_browser = ['Chrome']

supp_os = "Supported OS:"
for x in supported_os:
	supp_os = supp_os + " " + x
supp_browser = "Supported Browser:"
for x in supported_browser:
	supp_browser = supp_browser + " " + x

if len(sys.argv) != 3:
	logger.error("Invalid Arguments")
	logger.info("Command Format: python3 " + sys.argv[0] + " OS " + " Browser ")
	logger.info(supp_os)
	logger.info(supp_browser)
	sys.exit(-1)

def setUp(os, browser):
	if os not in supported_os or browser not in supported_browser:
		logger.error('Invalid OS or Browser')
		logger.info(supp_os)
		logger.info(supp_browser)
		sys.exit(-1)
	if os == supported_os[0] and browser == supported_browser[0]:
		options = webdriver.ChromeOptions()
		options.add_argument('ignore-certificate-errors')
		options.add_experimental_option('androidPackage', 'com.android.chrome')
		driver = webdriver.Chrome('./chromedriver_83.exe', options=options)
		return driver
	elif os == supported_os[1] and browser == supported_browser[0]:
		options = webdriver.ChromeOptions()
		options.add_argument('ignore-certificate-errors')
		driver = webdriver.Chrome('./chromedriver_90.exe', options=options)
		return driver

def test_showCity(driver):
	test_cases = [(39.8652539,32.7466006,"Çankaya"),(39.92652515450522,32.57341579682371,"Sincan"),(44.96908362329413,-93.25232934157854,"Minneapolis"),(32.99753361039027,73.25452405957748,"Jhelum"),(33.73721444143737,72.84212921472779,"Taxila"),(25.103809346243924,62.212696505284896,"No City Found!"),(-68.44758170052704, 91.11978227092429,"No City Found!"),('23.43av',12.323,"Invalid Coordinates"),('abcd',"efgh","Invalid Coordinates"),('abcd',"","Invalid Coordinates")]
	logger.info("Test A part: show City")
	results = [False for i in range(len(test_cases))]
	start_time = time.time()
	for i,x in enumerate(test_cases):
		inputs = (str(x[0]),str(x[1]))
		output = x[2]
		result = test_showCity_single_case(driver,inputs,output)
		results[i] = result
		if result:
			logger.debug("Test " + str(i+1) + " passed")
		else:
			logger.error("Test " + str(i+1) + " failed")
	end_time = time.time()
	elapsed_time = round(end_time - start_time,4)
	
	logger.info("Time for testing Part A: " + str(elapsed_time) + "s")
	logger.info("Result for testing Part A: " + str(sum(results)) + "/" + str(len(results)) + " tests passed")
	
def test_showCity_single_case(driver, inputs, output):
	driver.get('https://139.179.210.39:5000/showCity')
	time.sleep(1)
	driver.find_element_by_id('lat').send_keys(inputs[0])
	driver.find_element_by_id('long').send_keys(inputs[1])
	driver.find_element_by_id('btn').click()
	time.sleep(1)
	result_city = (driver.find_element_by_id('city').text).split(":")[1].strip()
	result = result_city == output
	if result is False:
		logger.info((str(result_city), str(output)))
	return result
	
def test_nearestCity(driver):
	test_cases = [(39.8652539,32.7466006,"Çankaya","11.504 km"),(39.92652515450522,32.57341579682371,"Sincan","3.671 km"),(44.96908362329413,-93.25232934157854,"Minneapolis","1.512 km"),(32.99753361039027,73.25452405957748,"Jajial","6.777 km"),(33.73721444143737,72.84212921472779,"Hattar","12.607 km"),(33.73021494143737,72.84292921,"Golra Sharif","13.003 km"),(25.103809346243924,62.212696505284896,"Gwadar","11.52 km"),('23.43av',12.323,"Invalid Coordinates","Invalid Coordinates"),('abcd',"efgh","Invalid Coordinates","Invalid Coordinates"),('abcd',"","Invalid Coordinates","Invalid Coordinates")]
	logger.info("Test B part: Distance to the Nearest City")
	results = [False for i in range(len(test_cases))]
	start_time = time.time()
	for i,x in enumerate(test_cases):
		inputs = (str(x[0]),str(x[1]))
		outputs = (x[2],x[3])
		result = test_nearestCity_single_case(driver,inputs,outputs)
		results[i] = result
		if result:
			logger.debug("Test " + str(i+1) + " passed")
		else:
			logger.error("Test " + str(i+1) + " failed")
	end_time = time.time()
	elapsed_time = round(end_time - start_time,4)
	
	logger.info("Time for testing Part B: " + str(elapsed_time) + "s")
	logger.info("Result for testing Part B: " + str(sum(results)) + "/" + str(len(results)) + " tests passed")
	
def test_nearestCity_single_case(driver,inputs,outputs):
	driver.get('https://139.179.210.39:5000/nearestCity')
	time.sleep(1)
	driver.find_element_by_id('lat').send_keys(inputs[0])
	driver.find_element_by_id('long').send_keys(inputs[1])
	driver.find_element_by_id('btn').click()
	time.sleep(1)
	result_city = (driver.find_element_by_id('city').text).split(":")[1].strip()
	result_distance = (driver.find_element_by_id('distance').text).split(":")[1].strip()
	result = False
	result = result_city == outputs[0] and result_distance == outputs[1]
	if result is False:
		logger.info((str(result_city), str(outputs[0])))
		logger.info((str(result_distance), str(outputs[1])))
	return result
	
def test_earthDistance(driver):
	test_cases = [(39.8652539,32.7466006,"6364.582 km"),(39.92652515450522,32.57341579682371,"6365.621 km"),(44.96908362329413,-93.25232934157854,"6363.542 km"),(32.99753361039027,73.25452405957748,"6357.281 km"),(33.73721444143737,72.84212921472779,"6367.273 km"),(33.73021494143737,72.84292921,"6367.132 km"),(83.06125106066311, -50.27400709868172,"6357.126 km"),(27.9881, 86.9250,"6385.255 km"),(35.3606,138.7274,"6370.841 km"),('23.43av',12.323,"Invalid Coordinates"),('abcd',"efgh","Invalid Coordinates"),('abcd',"","Invalid Coordinates")]
	logger.info("Test C part: Distance to the Earth Center")
	results = [False for i in range(len(test_cases))]
	start_time = time.time()
	for i,x in enumerate(test_cases):
		inputs = (str(x[0]),str(x[1]))
		output = x[2]
		result = test_earthDistance_single_case(driver,inputs,output)
		results[i] = result
		if result:
			logger.debug("Test " + str(i+1) + " passed")
		else:
			logger.error("Test " + str(i+1) + " failed")
	end_time = time.time()
	elapsed_time = round(end_time - start_time,4)
	
	logger.info("Time for testing Part C: " + str(elapsed_time) + "s")
	logger.info("Result for testing Part C: " + str(sum(results)) + "/" + str(len(results)) + " tests passed")
	
def test_earthDistance_single_case(driver,inputs,output):
	driver.get('https://139.179.210.39:5000/earthDistance')
	time.sleep(1)
	driver.find_element_by_id('lat').send_keys(inputs[0])
	driver.find_element_by_id('long').send_keys(inputs[1])
	driver.find_element_by_id('btn').click()
	time.sleep(1)
	result_distance = (driver.find_element_by_id('distance').text).split(":")[1].strip()
	result = False
	result = result_distance == output
	if result is False:
		logger.info((str(result_distance), str(output)))
	return result
	
def tearDown(driver):
	logger.info("Exiting")
	driver.quit()
	
driver = setUp(sys.argv[1], sys.argv[2])
print("=======================================================================")
test_showCity(driver)
print("=======================================================================")
test_nearestCity(driver)
print("=======================================================================")
test_earthDistance(driver)
print("=======================================================================")
tearDown(driver)
print("=======================================================================")
	