#!/usr/bin/python2.7

from optparse import OptionParser
import collections
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import os
import scipy.signal
import wave
import struct

parser = OptionParser()
parser.add_option('-f', "--filename", help="Filename of file for processing", action="store")
options, args = parser.parse_args()

filename=options.filename


def GetArrAndMinMax(lines):
    #Loop Var initialization
    arr = [] #Time to ColToSpec
    ColToSpec = {} #Collision Energy to Spectrum
    mz = []
    intens = []

    mzActive = 0 #Switches to see if the mz have been collected
    intensActive = 0

    mzArray = 0 #Have i been to mz array yet? Because reasons Darien....reasons.....
    minMz = 0
    maxMz = 0

    mzBinArr = []
    for i in range(67, len(lines)):
        SpecDict = {}
        if "scan start time" in lines[i]:
            starttime = float(lines[i].split(', ')[1])
        if "collision energy" in lines[i]:
            collenergy = int(lines[i].split(', ')[1])
        if "m/z array" in lines[i]:
            mz = lines[i+1].split("] ")[1].split()
            if mzArray == 0:
                minMz = int(min(map(float, mz)))-1
                maxMz = int(max(map(float, mz)))+1 #Wrap city!!
            mzActive = 1
        if "intensity array" in lines[i]:
            intens = lines[i+1].split("] ")[1].split()
            intensActive = 1
        if ((mzActive & intensActive) != 0):
            SpecDict = collections.OrderedDict(zip(mz, intens))
            arr.append(SpecDict)
            mzActive = 0 #Switches to see if the mz have been collected
            intensActive = 0
            mz = []
            intens = []

    return arr, minMz, maxMz

def BinUnitMassToHz(arr, minMz, maxMz):
    musicHzMax = 20000
    musicHzMin = 20
    rate = int((musicHzMax-musicHzMin)/(maxMz-minMz))
    TotalArr = []
    binMzArr = np.arange(musicHzMin, musicHzMax, rate).tolist()
    for i in arr:
        intArr = np.zeros(len(binMzArr)).tolist()
        for j in i:
            index = (int(float(j)-minMz))
            intArr[index] += float(i[j])
        tmpDict = collections.OrderedDict(zip(binMzArr, intArr))
        TotalArr.append(tmpDict)
    return TotalArr

def GetIntensityOverTime(arr, minMz, maxMz):
    TotalArr = []
    counterArr = []
    counter = 0
    musicHzMax = 20000
    musicHzMin = 20
    rate = int((musicHzMax-musicHzMin)/(maxMz-minMz))
    binMzArr = np.arange(musicHzMin, musicHzMax, rate).tolist()
    for i in arr:
        intArr = np.zeros(len(binMzArr)).tolist()
        for j in i:
            index = (int(float(j)-minMz))
            intArr[index] += float(i[j])
        counterArr.append(counter)
        TotalArr.append(intArr)
        counter+=1
    return counterArr,binMzArr, TotalArr

def SpecToAudio(sigArr):
    AudioArr = []
    for i in sigArr:
        AudioArr.extend(np.fft.ifft(i))
    return AudioArr

def NormalizeVal(val, maxVal):
    return val/maxVal

def NormalizeToOne(arr):
    os.system("taskset -p 0xff %d" % os.getpid())
    pool = Pool(processes=2)
    newArr = []
    maxVal = max(arr)
    #newArr.append([pool.apply_async(NormalizeVal, args=(x, maxVal)) for x in arr])
    #for i in newArr:
    #    for j in i:
    #        print j 
    #        j = j.get()
    for i in arr:
        newArr.append(i/maxVal)
    return newArr

def DownSample(NewSampRate, arr):
    factor = len(arr)/NewSampRate
    decFactArr = []
    print factor
    while (factor > 7):
        factor = factor / 7
        if factor != 0:
            decFactArr.append(factor)
    intermed = arr
    for i in decFactArr:
       intermed = scipy.signal.decimate(intermed, i)
    return intermed

def WriteWav(audioArr):
    vals = []
    print len(audioArr)
    outputfile = wave.open('MS1.wav', 'w')
    outputfile.setparams((2,2,44100, 0, 'NONE', 'not compressed'))
    appendLen = 44100 - len(audioArr)
    for i in range(appendLen):
        audioArr.append(0)
    for j in range(0, 44100):
        value = audioArr[j]*32767
        packed_val = struct.pack('h', value)
        vals.append(packed_val)
        vals.append(packed_val)

    val_str = ''.join(vals)
    outputfile.writeframes(val_str)

    outputfile.close()
    

#---Main---#
file = open(filename, 'r')
MSlines = file.readlines()
MSArr, minVal, maxVal = GetArrAndMinMax(MSlines)
#HzArr = BinUnitMassToHz(MSArr, minVal, maxVal)
timeArr, HzArr, signalArr = GetIntensityOverTime(MSArr, minVal, maxVal)
plt.contour(HzArr, timeArr, signalArr)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Time (s)")
plt.savefig("MSSpectrogram.png")

plt.clf()

Audio = SpecToAudio(signalArr)
normAudio = NormalizeToOne(DownSample(44100, Audio))
plt.plot(normAudio)
plt.xlabel("Time (s)")
plt.ylabel("Audio Magnitude")
plt.savefig("AudioSpec.png")

WriteWav(normAudio)
