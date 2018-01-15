import requests
import json
import datetime
import time
from http import HTTPStatus

calais_url = 'https://api.thomsonreuters.com/permid/calais'
usage_file = 'usage.json'
token_file = 'openctoken'


class OpenCalais:
	def __init__(self, access_token=None, token_daily_limit=5000, min_wait=0.750):
		if access_token:
			self.access_token = access_token
		else:
			self.access_token = self.load_token()
		if not self.access_token:
			raise ValueError('No access token')
		self.max_daily_requests = token_daily_limit
		self.output_format = 'application/json'
		self.daily_requests = 0
		self.load_request_count()
		self.last_request_time = 0
		self.min_wait = min_wait
		print('OpenCalais session setup. {uses} uses remaining today'.format(uses=self.max_daily_requests - self.daily_requests))

	@staticmethod
	def load_token():
		try:
			with open(token_file, 'r') as file:
				return str(file.readline()).strip()
		except EnvironmentError:
			print('Error loading access token from file')

	def load_request_count(self):
		try:
			with open(usage_file, 'r') as file:
				usage = json.load(file)
				if 'day' in usage:
					if usage['day'] == datetime.date.today().isoformat():
						if 'requests' in usage:
							self.daily_requests = usage['requests']
							print('Loaded daily uses from file. Current daily uses: {uses}'.format(uses=self.daily_requests))
		except EnvironmentError:
			self.daily_requests = 0
			print('Error loading usage file, daily uses set to 0')

	def save_request_count(self):
		try:
			with open(usage_file, 'w') as file:
				usage = {'day': datetime.date.today().isoformat(), 'requests': self.daily_requests}
				json.dump(usage, file)
				print('Saved daily uses to file. Current daily uses: {uses}'.format(uses=self.daily_requests))
		except EnvironmentError:
			print('Error saving usage file. Current daily uses: {uses}'.format(uses=self.daily_requests))

	def post_data(self, request_data):
		if not request_data:
			return
		if self.daily_requests > self.max_daily_requests:
			raise ValueError('Usage limit reached')
		sleep_time = self.last_request_time + self.min_wait - time.time()
		if sleep_time > 0:
			# ensure it has been at least 750 ms since last request
			time.sleep(sleep_time)
		try:
			headers = {'X-AG-Access-Token': self.access_token, 'Content-Type': 'text/raw', 'outputformat': self.output_format}

			response = requests.post(calais_url, data=request_data, headers=headers, timeout=80)

			if response.status_code == HTTPStatus.OK:
				if self.daily_requests == self.max_daily_requests:
					# We lost track of uses somewhere, this should have returned too many requests
					# keep going until we get the too many requests response from the server
					self.daily_requests = self.max_daily_requests - 1
				# print('OK ' + str(self.daily_requests))
				return response.text
			elif response.status_code == HTTPStatus.BAD_REQUEST:
				raise ValueError('Header or language problem caused server to reject request')
			elif response.status_code == HTTPStatus.UNAUTHORIZED:
				raise ValueError('Access token refused by server')
			elif response.status_code == HTTPStatus.NOT_ACCEPTABLE:
				raise ValueError('Server cannot handle requested output format')
			elif response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
				print('Request was too large: {data}'.format(data=request_data))
			elif response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
				raise ValueError('Server cannot handle request content format')
			elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
				if 'You exceeded the concurrent request limit for your license key. Please try again later or contact support to upgrade your license.' in response.text:
					print('Too many requests, must wait at least 750 ms between requests.')
					# Add another 250 ms to the wait time
					self.min_wait = self.min_wait + 0.250
				else:
					self.daily_requests = self.max_daily_requests
					raise ValueError('Usage limit reached')
					# TODO parse server message to get license limit and refresh time
					# You exceeded the allowed quota of <VALUE> requests per day. Please try again at: <DATE_TIME>
			elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR or response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
				print('Server error')
				# TODO can retry 3 times
			else:
				s = 'status code: ' + str(response.status_code) + 'Results received: ' + response.text
				raise ValueError(s)
		except requests.exceptions.RequestException:
			print('Connection error.')
			raise
		finally:
			self.daily_requests = self.daily_requests + 1
			self.save_request_count()
			self.last_request_time = time.time()


def best_match(results_str):
	entities = []
	d = json.loads(results_str)
	for k in d:
		item = d[k]
		if '_typeGroup' in item:
			if item['_typeGroup'] == 'entities':
				if item['_type'] == 'Company' or item['_type'] == 'Organization' or item['_type'] == 'Person':
					entities.append(item)
	return entities


if __name__ == "__main__":
	try:
		open_calais_connection = OpenCalais()
		with open('test1.json', 'w') as testfile:
			testfile.write(open_calais_connection.post_data('Dinner meeting with Jonathan Fisher'))

		test_string2 = "the Open University, Birmingham Metropolitan College, Richmond Adult and Community College, Association of Colleges, Leicester College, Ford of Britain, SKOPE, Trafford College, Trades Union Congress, DavyMarkham, Beyond Standards Ltd, National Institute of Adult Continuing Education, University of London, King's College London"
		with open('test2.json', 'w') as testfile:
			testfile.write(open_calais_connection.post_data(test_string2))

	except Exception as ex:
		print(ex)
