import socket
import os, os.path
import time
import sys
import scipy.io
# Load libraries
import glob
import pandas
# Load libraries
import numpy as np
import scipy.stats.stats as st
import math
import operator

def find(a):
    if a is not None:
        return np.flatnonzero(a.ravel())
    else:
        return 0

def weight_biases(Entradas,Pesos,BiasofHiddenNeurons):
    NumberofTrainingData = 1;
    #tempH_new= Pesos * Entradas;
    tempH_new= np.dot(Pesos, Entradas);
    #print Pesos.shape # 1000,14
    #print Entradas.shape #14
    #print tempH_new.shape # 1000,1
    BiasMatrix=BiasofHiddenNeurons;
    #print BiasMatrix.shape
    for i in xrange(0,1000):
        tempH_new[i]=tempH_new.transpose()[i]+BiasMatrix[i];
    e = np.exp(-tempH_new)
    ho =  1 / (1 + e );
    return ho

server_address = 'ESEmbarcados'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise
# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print 'starting up on %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
e1 = []
e2 = []
i = 0
count = 0
while count < 1200:
    # Wait for a connection
    print  'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            #print float(data)
            #print repr(data)
            try:
                data = float(data.replace("\x00",""))
                print data
                if data:
                    if i == 0:
                        e1.append(data)
                        i = i + 1
                    else:
                        e2.append(data)
                        i = 0
                    print 'sending data back to the client'
                    connection.sendall("ack")
                    count = count + 1
                else:
                    print 'no more data from', client_address
                    break
            except:
                pass
    finally:
        # Clean up the connection
        connection.close()

d = {'e1': e1, 'e2': e2}
df = DataFrame(data=d, index=index)

mat = scipy.io.loadmat('S1_SW_256_NP_7_PS_0.66_M_6_PR_21_F1_R1.mat')
weight_fin = mat['weight_fin']


bias_fin = mat['bias_fin']

funcao = mat['funcao']
header = ['e1','e2']
"""
# Load dataset
allFiles = glob.glob("HC-1.csv")
frame = pandas.DataFrame()
list_ = []
for file_ in allFiles:
    df = pandas.read_csv(file_,index_col=None, names=header)
    #list_.append(df)
#frame = pandas.concat(list_)
#frame['class'] = 1
"""
print df

lin = 600
col = 2
SLOPECHANGES_a = []
SLOPECHANGES_a = np.zeros((col,1));
ZEROCROSSINGS_a = np.zeros((col,1));
SKEWNESS_a = np.zeros((col,1));
HJORTHPARAM_activity_a = np.zeros((col,1));
HJORTHPARAM_mobility_a = np.zeros((col,1));
HJORTHPARAM_complexity_a = np.zeros((col,1));
WAVEFORMLENGTH_a = np.zeros((col,1));

temp = df.transpose()

tempc,templ = temp.shape


for n in xrange(0, 600-1):
    for m in xrange(0,2):
        WAVEFORMLENGTH_a[m] = WAVEFORMLENGTH_a[m] + (-temp[n][m]+temp[n+1][m]);


temp = list(temp.values)

#print len(find(np.diff(np.sign(temp[0][:]))))
for o in xrange(0, 2):
    ZEROCROSSINGS_a[o] = len(find(np.diff(np.sign(temp[o][0:599]))));
    SLOPECHANGES_a[o] = len(find(np.diff(np.sign(np.diff(temp[o][0:599])))));
    SKEWNESS_a[o] = st.skew(temp[o][0:599]);
    HJORTHPARAM_activity_a[o] = np.var(temp[o][0:599]);
    HJORTHPARAM_mobility_a[o] = np.sqrt((np.var(np.diff(temp[o][0:599])))/np.var(temp[o][0:599]));
    HJORTHPARAM_complexity_a[o] = (np.sqrt(np.var(np.diff(np.diff(temp[o][0:599]))))/(np.var(np.diff(temp[o][0:599]))))/np.sqrt((np.var(np.diff(temp[o][0:599])))/np.var(temp[o][0:599]));

ZEROCROSSINGS_a = ZEROCROSSINGS_a.transpose()
SLOPECHANGES_a = SLOPECHANGES_a.transpose()
SKEWNESS_a = SKEWNESS_a.transpose()
HJORTHPARAM_activity_a = HJORTHPARAM_activity_a.transpose()
HJORTHPARAM_mobility_a = HJORTHPARAM_mobility_a.transpose()
HJORTHPARAM_complexity_a = HJORTHPARAM_complexity_a.transpose()
WAVEFORMLENGTH_a = WAVEFORMLENGTH_a.transpose()
# Concatenando os atributos para formar a matriz de dados
data = [];

for i in xrange(0, 2):
    alfa = np.concatenate(([SLOPECHANGES_a[0][i]],[ZEROCROSSINGS_a[0][i]],
    [SKEWNESS_a[0][i]], [HJORTHPARAM_activity_a[0][i]], [HJORTHPARAM_mobility_a[0][i]],
    [HJORTHPARAM_complexity_a[0][i]],[WAVEFORMLENGTH_a[0][i]]))
    data = np.concatenate((data,alfa));

#Normalizando os dados de acordo com o conjunto treino da rede
a = -0.5;
b = 0.5;
data_train_raw = pandas.read_csv('S1_Treino_SW_256_NP_7_PS_0.66_M_6_PR_21.csv')
data_train_raw.drop(data_train_raw.columns[[0]], axis=1, inplace=True)

#data_train = ((b-a)*((data-np.tile(min(data_train_raw),len(data[:][1]),1))/  (np.tile(max(data_train_raw),len(data[:][1]),1)-np.tile(min(data_train_raw), len(data[:][1]),1)))+a);
minByColumn = []
maxByColumn = []
for i in xrange(0,14):
    minByColumn.append(min(data_train_raw.ix[:,i]))
    maxByColumn.append(max(data_train_raw.ix[:,i]))


sub1 = np.array(data) - np.array(minByColumn)
sub2 = np.array(maxByColumn) - np.array(minByColumn)
data_train = (b-a)*(sub1/sub2) + a

Output = []
#Classificao usando ELM
tam_peso = len(weight_fin[0])
h = data_train.transpose();
for i in xrange(0, tam_peso):
    if i == tam_peso-1:
        Output = np.dot(np.array(h).transpose(),np.array(weight_fin[0][i])).transpose()
    else:
        H = weight_biases(h, weight_fin[0][i], (bias_fin[0][i]).transpose())
        h = H;
# output a resposta esperada da rede+1
#maior valor e index do maior valor
#print Output.shape

maxVal = max(Output)
#idx = np.array(Output).index(max(Output))

for i in xrange(0,len(Output)):
    if Output[i] == maxVal:
        idx = i
        break;

print maxVal
print idx
