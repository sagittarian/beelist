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

	def __init__(self, config, format='{slug}: {limsum} ({mostrecent}: {curval})'):
		self.format = format
		self._list = None
		self.now = time.time()
		self.today = time.strftime('%Y-%m-%d', time.localtime(self.now))
		self.config = config
		self.auth_token = config.get('common', 'auth_token')
		self.bm = beeminder.Beeminder(self.auth_token)

	def groupkey(self, goal):
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
		return int(normideal * default_ideal) or 1

	def test(self, goal):
		goal_type = goal['goal_type']
		lastday = goal['lastday']
		frozen = goal['frozen']
		slug = goal['slug']
		mostrecent = goal['mostrecent']
		if slug not in self.config:
			self.config.add_section(slug)
		isdaily = self.config.getboolean(slug, 'daily')
		#print('{}, curday is {}'.format(slug, curday), self.now - curday > SECONDS_PER_DAY, isdaily)
		return (goal_type in TYPES and not frozen and
		        (not isdaily or self.today != mostrecent))

	@property
	def goals(self):
		values = self.bm.goals.values()
		for goal in values:
			goal['mostrecent'] = time.strftime('%Y-%m-%d',
			                                   time.localtime(goal['lastday']))
		return values

	@property
	def list(self):
		if self._list is None:
			goals = sorted((goal for goal in self.goals if self.test(goal)),
			               key=lambda goal: (self.groupkey(goal), goal['losedate']))
			groups = itertools.groupby(goals, self.groupkey)
			self._list = {key: [self.format.format(**goal) for goal in group] for (key, group) in groups}
		return self._list

	def __str__(self):
		list = self.list
		keys = sorted(list.keys())
		result = []
		result.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
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
