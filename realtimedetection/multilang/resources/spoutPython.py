import storm
import time
from time import sleep

DATA_0302 = r"/home/Arthur/Desktop/data/csecicids2018-clean/Friday-02-03-2018_TrafficForML_CICFlowMeter.csv"
DATA_0301 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv"
DATA_0228 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0223 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Friday-23-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0222 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Thursday-22-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0221 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Wednesday-21-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0220 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Tuesday-20-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0216 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Friday-16-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0215 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0214 = r"/home/Arthur/Desktop/data/csecicids2018-clean\Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv"

class SpoutPython(storm.Spout):
    def initialize(self, conf, context):
        self._conf = conf
        self._context = context
        self.tuple_counter = 0
        storm.logInfo("Spout starting...")
        try:  
            self.f = open(DATA_0302, 'r')
            self.f.readline() #skip header
            storm.logInfo("Spout ready...")
        except OSError:
            storm.logInfo("File error")
            exit()
        
    def activate(self):
        pass

    def deactivate(self):
        pass

    def ack(self, id):
        storm.logInfo("Tuple "+ str(self.tuple_counter) +" processed")
        self.tuple_counter+=1

    def fail(self, id):
        storm.logInfo("Tuple "+ str(self.tuple_counter) + " failed")
        self.tuple_counter+=1

    def nextTuple(self):
        for line in self.f.readlines():
            storm.logInfo("emiting %s" % line)
            storm.emit([line])
            sleep(0.5)
            
SpoutPython().run()
