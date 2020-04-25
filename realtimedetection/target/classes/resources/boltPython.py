import sklearn
from sklearn import preprocessing, tree
from sklearn.preprocessing import LabelBinarizer, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier

import imblearn #solve imbalance
from imblearn.over_sampling import SMOTE
import numpy as np 
import pandas as pd
import random
from itertools import zip_longest

#Linken met apache storm
import storm

#Alle aanvals categoriëen (15) onderbrengen in 6 globale klassen
dict_category = {
    "Benign"                : "Benign",
    "Bot"                   : "Bot", #02/03 
    "Infilteration"         : "Infilteration", #28/02,01/03
    "SQL Injection"         : "SQL Injection", #22/02,23/02

    "Brute Force -Web"      : "Brute Force", #22/02,23/02
    "Brute Force -XSS"      : "Brute Force", #22/02,23/02
    "FTP-BruteForce"        : "Brute Force", #14/02 
    "SSH-Bruteforce"        : "Brute Force",  #14/02

    "DDOS attack-LOIC-UDP"  : "DOS",#20/02,21/02 
    "DDOS attack-HOIC"      : "DOS",  #21/02 
    "DDoS attacks-LOIC-HTTP" : "DOS", #20/02 
    "DoS attacks-SlowHTTPTest" : "DOS", #16/02 
    "DoS attacks-Hulk"      : "DOS",    #16/02 
    "DoS attacks-Slowloris" : "DOS", #15/02
    "DoS attacks-GoldenEye" : "DOS" #15/02 
}

dict_binary = {
    "Benign"                : 0, # x
    "Bot"                   : 1, #02/03 x
    "Infilteration"         : 0, #28/02,01/03
    "SQL Injection"         : 0, #22/02,23/02
    "Brute Force"           : 0,
    "DOS"                   : 0
}

DATA_0302 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Friday-02-03-2018_TrafficForML_CICFlowMeter.csv"
DATA_0301 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv"
DATA_0228 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0223 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Friday-23-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0222 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Thursday-22-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0221 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Wednesday-21-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0220 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Tuesday-20-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0216 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Friday-16-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0215 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv"
DATA_0214 = r"C:\Users\Arthur\Desktop\masterproef\ML_models\csecicids2018-clean\Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv"
datasets = [DATA_0302, DATA_0301, DATA_0228, DATA_0222, DATA_0221, DATA_0220, DATA_0216, DATA_0215, DATA_0214]
dataset_names = ["DATA_0302", "DATA_0301", "DATA_0228", "DATA_0223", "DATA_0222", "DATA_0221", "DATA_0220", "DATA_0216",
 "DATA_0215", "DATA_0214"]

############### Functies ###############

def read_random(filename,sample_size):
    if sample_size is None:
        df = pd.read_csv(filename)
    else:
        n = sum(1 for line in open(filename)) - 1 #number of records in file (excludes header)
        skip = sorted(random.sample(range(1,n+1),n-sample_size)) #the 0-indexed header will not be included in the skip list
        df = pd.read_csv(filename, skiprows=skip)
    return df

def relabel_minorities(labels):
    relabelled = []
    for i in labels:
        relabelled.append(dict_category[i]) 
    
    #Numpy array
    return np.array(relabelled)

def encode_to_binary_classification(y_train,y_test):
    #Encode output labels
    y_train_encoded = []
    y_test_encoded = []
    for i,j in zip_longest(y_train,y_test, fillvalue="end"):
        if i != "end":
            y_train_encoded.append(dict_binary[i])
        if j != "end":
            y_test_encoded.append(dict_binary[j])
    return (y_train_encoded,y_test_encoded)

############### Implementatie ###############

class BoltPython(storm.BasicBolt):

    def initialize(self, conf, context):
        self._conf = conf
        self._context = context
        storm.logInfo("Bolt starting...")
        #pretrain model
        df = None 
        df_next = None

        for i in datasets:
            if df is None:
                df = read_random(i,20000)
                df_next = df
            else:
                df_next = read_random(i,20000)
                df = pd.concat([df,df_next])

        df_next = pd.read_csv(DATA_0223,skiprows=range(1,1500),nrows=20000)
        df = pd.concat([df, df_next])

        df = df.drop(df.columns[2],axis=1) #drop timestamp

        labels = df.iloc[:,-1].values
        labels = relabel_minorities(labels)

        #Omzetten naar binary classification
        labels_to_binary = []
        for i in labels:
            labels_to_binary.append(dict_binary[i])

        unique_df = pd.DataFrame(data=labels[1:], columns=["Label"])

        y = labels_to_binary
        X = df.iloc[:,:-1]

        #train decision tree
        
        oversample = SMOTE(sampling_strategy=1)
        x_train, y_train = oversample.fit_resample(X,y)

        DT = DecisionTreeClassifier()
        DT.fit(np.array(x_train), np.array(y_train))

        self._DT = DT
        storm.logInfo("Bolt ready...")

    def process(self, tuple):
        network_line = tuple.values[0]
        storm.logInfo("Bolt received: " + network_line)
        
        features = np.array(network_line.split(','))
        features = np.delete(features,[2,79],None)

        #processing
        prediction = self._DT.predict(features.reshape(1,-1))
        
        storm.logInfo("Prediction: " + str(prediction))
        
        #prediction is array, niet json serializable
        #haal dus de waarde uit de array
        #en converteer de numpy int32 naar een normale int
        storm.emit(prediction.tolist())

BoltPython().run()