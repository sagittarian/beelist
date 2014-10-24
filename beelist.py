#!/usr/bin/python3
'''Create a basic todo list based on Beeminder goals,
   sorted by how close they are to derailing.'''

import configparser
import itertools
import os
import time

import beeminder

TYPES = {'biker', 'hustler'}
SECONDS_PER_DAY = 24 * 60 * 60
IDEAL_DAYS_LEFT = 3

def get_config():
	config = configparser.ConfigParser(defaults=dict(ideal=IDEAL_DAYS_LEFT),
	                                   default_section='default',
	                                   interpolation=None)
	config.read(os.path.expanduser('~/.beelistrc'))
	return config

class Beelist:

	def __init__(self, config, format='{slug}: {limsum}'):
		self.format = format
		self._list = None
		self.now = time.time()
		self.config = config
		self.auth_token = config.get('common', 'auth_token')
		self.bm = beeminder.Beeminder(self.auth_token)

	def key(self, goal):
		slug = goal['slug']
		losedate = goal['losedate']
		if slug not in self.config:
			self.config.add_section(slug)
		ideal = self.config.getint(slug, 'ideal')
		daysleft = int((losedate - self.now) / SECONDS_PER_DAY)
		if not daysleft:
			return daysleft
		normideal = daysleft / ideal
		if normideal > 1:
			return float('inf')
		default_ideal = self.config.getint('default', 'ideal')
		return int(normideal * default_ideal)

	@property
	def list(self):
		if self._list is None:
			goals = sorted((goal for goal in
			                self.bm.goals.values()
			                if goal['goal_type'] in TYPES and not goal['frozen']),
			               key=lambda goal: goal['losedate'])
			groups = itertools.groupby(goals, self.key)
			self._list = {key: [self.format.format(**goal) for goal in group] for (key, group) in groups}
		return self._list

	def __str__(self):
		list = self.list
		keys = sorted(list.keys())
		result = []
		for key in keys:
			result.append('== Priority {} =='.format(key))
			result.extend(list[key])
			result.append('')
		return '\n'.join(result)

def main():
	config = get_config()
	print(Beelist(config))

if __name__ == '__main__':
	main()
