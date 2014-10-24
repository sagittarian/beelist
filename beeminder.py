#!/usr/bin/python3

'''Implementation of the Beeminder API: https://www.beeminder.com/api
   Still very incomplete.'''

import json
import re

import requests

class BeeminderMock:

	def __init__(self, mockdata):
		self.mockdata = mockdata

	@staticmethod
	def getidp(ath):
		m = re.search('([a-z0-9]+)\.json$', path)
		return m.group(1) if m else None

	def execute(self, path, params=None, request_type='get'):
		print(path, params, request_type)
		if path.endswith('datapoints.json'):
			return self.mockdata
		if request_type == 'delete':
			dataid = self.getid(path)
			for (i, pt) in enumerate(self.mockdata):
			        if pt['id'] == dataid:
				        del self.mockdata[i]
				        return pt
			else:
				return None
		raise ValueError((path, params, request_type))

class BeeminderBackend:

	API_URL = 'https://www.beeminder.com/api/v1/'

	def __init__(self, auth_token, dryrun, debug):
		self.auth_token = auth_token
		self.dryrun = dryrun
		self.debug = debug

	def execute(self, path, params=None, request_type='get'):
		'''Return the url for accessing path, adding the given args
		and the auth token'''
		if self.debug:
			print('{method} {path} {params}'.format(
				method=request_type.upper(),
				path=path,
				params=params or ''
			))
		if self.dryrun:
			print('{} {} {}'.format(request_type.upper(), path, params))
			key = (path,
				   tuple(sorted(params.items())) if params is not None else (),
				   request_type)
			print(repr(key))
			return self.dryrun[key]
		path = path.lstrip('/')
		method = getattr(requests, request_type)
		args = {'auth_token': self.auth_token}
		if params is not None:
			args.update(params)
		response = method(self.API_URL + path, params=args)
		return response.json()


class Beeminder:

	def __init__(self, auth_token, username=None, dryrun=False, debug=False):
		self._username = username
		self._user = None
		self._goals = {}
		self._data = {}
		if not debug:
			self.backend = BeeminderBackend(auth_token, dryrun, debug)
		else:
			import mock
			self.backend = BeeminderMock(mock.mockdata)

	def get(self, path, params=None):
		return self.backend.execute(path, params, 'get')

	def delete(self, path, params=None):
		return self.backend.execute(path, params, 'delete')

	def put(self, path, params=None):
		return self.backend.execute(path, params, 'put')

	def post(self, path, params=None):
		return self.backend.execute(path, params, 'post')

	@property
	def user(self):
		'''Return the user object'''
		if self._user is None:
			self._user = self.get('/users/me.json')
		return self._user

	@property
	def username(self):
		'''Return the user's username'''
		return self._username or self.user['username']

	def goal(self, slug):
		'''Return the goal object for the given slug'''
		if slug not in self._goals:
			path = '/users/{}/goals/{}.json'.format(
				self.username, slug)
			self._goals[slug] = self.get(path)
		return self._goals[slug]

	@property
	def goals(self):
		'''Return the list of goals'''
		path = '/users/{}/goals.json'.format(self.username)
		goal_list = self.get(path)
		for goal in goal_list:
			slug = goal['slug']
			self._goals[slug] = goal
		return self._goals

	def data(self, slug):
		'''Return the datapoints for the given goal'''
		if slug not in self._data:
			path = '/users/{}/goals/{}/datapoints.json'.format(
				self.username, slug)
			self._data[slug] = self.get(path)
		return self._data[slug]

	def delete_point(self, slug, data_id):
		path = '/users/{}/goals/{}/datapoints/{}.json'.format(
			self.username, slug, data_id)
		return self.delete(path)

	def update_point(self, slug, data_id,
					 timestamp=None, value=None, comment=None):
		path = '/users/{}/goals/{}/datapoints/{}.json'.format(
			self.username, slug, data_id)
		params = {}
		if timestamp is not None:
			params['timestamp'] = timestamp
		if value is not None:
			params['value'] = value
		if comment is not None:
			params['comment'] = comment
		if params:
			return self.put(path, params=params)

	def create_all(self, slug, points):
		path = '/users/{}/goals/{}/datapoints/create_all.json'.format(
			self.username, slug)
		datapoints = json.dumps(points)
		self.post(path, params={'datapoints': datapoints})
