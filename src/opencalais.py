import requests
import json
import datetime
import time
from http import HTTPStatus

calais_url = 'https://api.thomsonreuters.com/permid/calais'
usage_file = 'usage.json'
token_file = 'openctoken'


class OpenCalais:
	def __init__(self, access_token=None, token_daily_limit=5000):
		if access_token:
			self.access_token = access_token
		else:
			self.access_token = self.load_token()
		if not self.access_token:
			raise Exception('No access token')
		self.max_daily_requests = token_daily_limit
		self.output_format = 'application/json'
		self.daily_requests = 0
		self.load_request_count()

	@staticmethod
	def load_token():
		try:
			with open(token_file, 'r') as file:
				return str(file.readline()).strip()
		except Exception as e:
			print(e)

	def load_request_count(self):
		try:
			with open(usage_file, 'r') as file:
				usage = json.load(file)
				if 'day' in usage:
					if usage['day'] == datetime.date.today().isoformat():
						if 'requests' in usage:
							self.daily_requests = usage['requests']
		except IOError:
			self.daily_requests = 0
		except Exception as e:
			print(e)

	def save_request_count(self):
		try:
			with open(usage_file, 'w') as file:
				usage = {'day': datetime.date.today().isoformat(), 'requests': self.daily_requests}
				json.dump(usage, file)
		except Exception as e:
			print(e)

	def post_data(self, request_data):
		if self.daily_requests >= self.max_daily_requests:
			raise Exception('Usage limit reached')
		try:
			headers = {'X-AG-Access-Token': self.access_token, 'Content-Type': 'text/raw', 'outputformat': self.output_format}

			response = requests.post(calais_url, data=request_data, headers=headers, timeout=80)

			if response.status_code == HTTPStatus.OK:
				return response.text
			else:
				s = 'status code: ' + str(response.status_code) + 'Results received: ' + response.text
				raise Exception(s)
		except Exception:
			raise
		finally:
			self.daily_requests = self.daily_requests + 1
			self.save_request_count()


if __name__ == "__main__":
	try:
		open_calais_connection = OpenCalais()
		with open('test1.json', 'w') as testfile:
			testfile.write(open_calais_connection.post_data('Dinner meeting with Jonathan Fisher'))
		time.sleep(1)

		test_string2 = "the Open University, Birmingham Metropolitan College, Richmond Adult and Community College, Association of Colleges, Leicester College, Ford of Britain, SKOPE, Trafford College, Trades Union Congress, DavyMarkham, Beyond Standards Ltd, National Institute of Adult Continuing Education, University of London, King's College London"
		with open('test2.json', 'w') as testfile:
			testfile.write(open_calais_connection.post_data(test_string2))
		time.sleep(1)

	except Exception as ex:
		print(ex)
