from datetime import *

class Help:
    def __init__(self):
        # For the help topics of commands of Virgobeta.
        # Keys are commands, values are help text to send.
        self.topics = {"help":"Gives help about Virgobeta commands.\nUsage: &help [command]\n",
                       "hi":"Greets you or someone.\nUsage: &hi [person]",
                       "bf":"The brainf--- interpreter.\nUsage: &bf <bf_code>",
                       "ul":"Underload interpreter.\nUsage: &ul <ul_code>. Not implemented yet.",
                       "unlambda":"Unlambda interpreter.\nUsage: &unlambda <unlambda_code>. Not implemented yet.",
                       "join":"Joins Virgobeta to the specific channel. Recommended to use PM.\nUsage: &join <#channel>."}
        
    def requestHelp(self, topic):
        if topic in self.topics:
            # if topic found
            return self.topics[topic].split("\n")
        else:
            # if not found
            return ["-> Topic is not available :("]

    def requestTopics(self):
        # generate the topic list
        topicstr = "Topics are: %s" % " ".join(self.topics)
        return topicstr
