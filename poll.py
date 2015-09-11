class Poll:
    def __init__(self, candidates):
        self.candidates = [x.lower() for x in candidates]
        self.voters = {}

    def votefor(self, user, candidate):
        if candidate.lower() in self.candidates:
            self.voters[user] = candidate.lower()
            return 1
        else:
            return 0

    def getcandidates(self):
        return self.candidates


class PollingSystem:
    def __init__(self):
        self.polls = {}

    def addpoll(self, pname, *candidates):
        self.polls[pname] = Poll(candidates)

    def votefor(self, pname, user, candidate):
        if pname in self.polls and candidate in self.polls[pname].getcandidates():
            self.polls[pname].votefor(user, candidate)
        else:
            return 'You cannot vote for an invalid candidate or poll!'

    def delpoll(self, pname):
        if pname in self.polls:
            del self.polls[pname]
        else:
            return 'Invalid poll name'