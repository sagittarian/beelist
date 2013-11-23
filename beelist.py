#!/usr/bin/python3
'''Create a basic todo list based on Beeminder goals,
   sorted by how close they are to derailing.'''

import beeminder

TYPES = {'biker', 'hustler'}

class Beelist:

    def __init__(self, auth_token, format='{title}: {limsum}'):
        self.auth_token = auth_token
        self.format = format
        self._list = None
        self.bm = beeminder.Beeminder(auth_token)

    @property
    def list(self):
        if self._list is None:
            goals = sorted((goal for goal in
                    self.bm.goals.values()
                    if goal['goal_type'] in TYPES and not goal['frozen']),
                key=lambda goal: goal['losedate'])
            self._list = [self.format.format(**goal) for goal in goals]
        return self._list

    def list_str(self, bullet='- [ ] '):
        seq = [bullet + item for item in self.list]
        return '\n'.join(seq)

def main():
    import sys
    if len(sys.argv) < 2:
        sys.stderr.write('usage: {} <auth_token>\n'.format(sys.argv[0]))
        sys.exit(1)
    auth_token = sys.argv[1]
    print(Beelist(auth_token).list_str())

if __name__ == '__main__':
    main()
