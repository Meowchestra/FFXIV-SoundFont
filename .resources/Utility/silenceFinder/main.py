import fileinput
from pydub import AudioSegment, silence
import glob, pydub
import collections
import struct

import pathlib

import common
from common import SampleStruct, MidiToIngameDict

#Sample top dir goes here
pth = "C:\\tmp\\samples\\"

structholder = []
cstruct = []

def findsilence(name):
    myaudio = AudioSegment.from_file_using_temporary_files(name)
    maxDB = myaudio.max_dBFS
    dBFS = myaudio.dBFS
    vol =  ((maxDB-dBFS) * 90 / 100) #don't ask ...
    fsilence = pydub.silence.detect_silence(myaudio, min_silence_len=1, silence_thresh=dBFS -vol)

    fsilence = [((start),(stop)) for start,stop in fsilence] #in ms

    mstruct = ""
    for x in structholder:
        if x.Samplename.startswith(pathlib.Path(name).name.split(".")[0]):
            if common.has_numbers(pathlib.Path(name).name.split(".")[1]):
                if pathlib.Path(name).name.split(".")[1].startswith(x.ScdNum):
                    mstruct = x
                    break
            else:
                mstruct = x
                break


    #refresh the structs
    structholder.remove(mstruct)
    mstruct.SampleDelay = fsilence[0][1]
    structholder.append(mstruct)

    print ("---------------------------------------------------------------------------------------------------------------")
    print (("Samplename:           %s" % name.replace(pth, "")))
    print(("Sample frequency kHz: %u" % myaudio.frame_rate))
    print(("Silence:              %ums" % fsilence[0][1]))
    print(("Sample Index:         %s" % ("scd" + str(mstruct.Index))))
    print(("Sample Basekey:       %u" % mstruct.KeyIndex))
    print(("Sample Lowkey:        %u" % mstruct.LowKey))
    print(("Sample Highkey:       %u" % mstruct.HighKey))

    output = ""
    for n in range((mstruct.HighKey - mstruct.LowKey) + 1):
        output += str(mstruct.SampleDelay) + ", "
    print (output)
    return fsilence[0][1]

#Use the scd to extract the sample base, start and end key (it's in midi code)
def findsamplescales(name):
    buf = collections.deque(maxlen=3) #circular buffer
    buf.append(0)
    buf.append(0)
    buf.append(0)
    file = open (name, mode="rb")
    while True:
        if buf[0] == b"\x00":
            if buf[1] == b"\x40":
                if buf[2] == b"\x00":
                    break
        buf.append(file.read(1))

    max_samples = struct.unpack('>H', file.read(2))[0]
    version = ord(file.read(1))
    for i in range(max_samples):
        sstruct = SampleStruct()
        sstruct.Unk1 = ord(file.read(1))
        sstruct.BankNumber = struct.unpack('<H', file.read(2))[0]
        sstruct.Index = struct.unpack('<H', file.read(2))[0]
        sstruct.Samplename = pathlib.Path(name).name
        sstruct.KeyIndex = ord(file.read(1))
        sstruct.LowKey = ord(file.read(1))
        sstruct.HighKey = ord(file.read(1))
        sstruct.ScdNum = "scd_" + str(sstruct.Index)
        sstruct.InstrumentNumber = int(pathlib.Path(name).name.split(".")[0][:3])
        file.read(4)
        if sstruct.LowKey < sstruct.HighKey:
            structholder.append(sstruct)

    file.close()
    return

def cleanup():
    removelist =[]
    for x in structholder:
        if x.SampleDelay == -1:
            removelist.append(x)
    for x in removelist:
        structholder.remove(x)
    removelist.clear()
    return

def do_silence():
    for filename in glob.iglob(pth + '**/*.wav', recursive=True):
        name=filename
        findsilence(name)
    cleanup()

def do_range():
    for filename in glob.iglob(pth + '**/*.scd', recursive=True):
        name=filename
        findsamplescales(name)

def create_cstruct():
    a = sorted(structholder, key=lambda x: (x.InstrumentNumber, x.Index), reverse=True)
    print (common.MidiToIngameDict)
    output = {}

    old =""
    xiv_instnum = -1
    for x in a:
        if x.Samplename.split(".")[0] != old:
            if old is not "":
                output[xiv_instnum] += "},"

            old = x.Samplename.split(".")[0]
            xiv_instnum = MidiToIngameDict[old]
            output[xiv_instnum] = "new byte[] " + common.Comments[xiv_instnum] + "\r\n"
            output[xiv_instnum] += "{\r\n"
            output[xiv_instnum] += "    "
            f = x.HighKey - x.LowKey
            for n in range(f+1):
                output[xiv_instnum] += str(x.SampleDelay) + ", "
            output[xiv_instnum] += "\r\n"
        else:
            f = x.HighKey - x.LowKey
            for n in range(f+1):
                output[xiv_instnum] += str(x.SampleDelay) + ", "
            output[xiv_instnum] += "\r\n"

        print (x.ScdNum)

    #file = open(pth + "offsetTable.txt")

    #file.writelines("new byte[]")
    #file.writelines("{")


    #file.writelines("},")
    #file.close()
    return

do_range()
do_silence()
#create_cstruct()