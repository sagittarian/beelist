#!/usr/bin/python3

'''Implementation of the Beeminder API: https://www.beeminder.com/api
   Still very incomplete.'''

import requests

API_URL = 'https://www.beeminder.com/api/v1/'

class Beeminder:

    def __init__(self, auth_token):
        self.auth_token = auth_token
        self._user = None
        self._goals = {}

    def get(self, path, args=None):
        '''Return the url for accessing path, adding the given args
        and the auth token'''
        path = path.lstrip('/')
        response = requests.get(API_URL + path,
                                params={'auth_token': self.auth_token})
        return response.json

    @property
    def user(self):
        '''Return the user object'''
        if self._user is None:
            self._user = self.get('/users/me.json')
        return self._user

    def goal(self, slug):
        '''Return the goal object for the given slug'''
        if slug not in self._goals:
            path = '/users/{}/goals/{}.json'.format(
                self.user['username'], slug)
            self._goals[slug] = self.get(path)
        return self._goals[slug]

    @property
    def goals(self):
        path = '/users/{}/goals.json'.format(self.user['username'])
        goal_list = self.get(path)
        for goal in goal_list:
            slug = goal['slug']
            self._goals[slug] = goal
        return self._goals

