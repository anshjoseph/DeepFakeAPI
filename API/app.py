from fastapi import requests, FastAPI, File, UploadFile, BackgroundTasks
from uuid import uuid4
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model
from pydantic import BaseModel
import cv2
import numpy as np
import numpy as np
from matplotlib import pyplot as plt
import scipy.io.wavfile as wav
from numpy.lib import stride_tricks
import librosa    
from scipy.io.wavfile import write

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LOAD MODEL
MODEL = load_model("../MODEL/model.h5")
# GLOBAL DATA STORE
Result:dict = dict()

# img = cv2.imread("/media/ansh/22A048A8A04883EF/WORK/ML/DeepFakeVoiceDectection/Train/Spectrogram/FAKE/0d4d5e35-ab2f-4b80-bb47-bc65f53801dd.png")
# img = cv2.resize(img,(256,256))
# print(MODEL.predict(np.array([img])))
# DATA PROCESSING
""" short time fourier transform of audio signal """
def stft(sig, frameSize, overlapFac=0.5, window=np.hanning):
    win = window(frameSize)
    hopSize = int(frameSize - np.floor(overlapFac * frameSize))

    # zeros at beginning (thus center of 1st window should be for sample nr. 0)   
    samples = np.append(np.zeros(int(np.floor(frameSize/2.0))), sig)    
    # cols for windowing
    cols = np.ceil( (len(samples) - frameSize) / float(hopSize)) + 1
    # zeros at end (thus samples can be fully covered by frames)
    samples = np.append(samples, np.zeros(frameSize))

    frames = stride_tricks.as_strided(samples, shape=(int(cols), frameSize), strides=(samples.strides[0]*hopSize, samples.strides[0])).copy()
    frames *= win

    return np.fft.rfft(frames)    

""" scale frequency axis logarithmically """    
def logscale_spec(spec, sr=44100, factor=20.):
    timebins, freqbins = np.shape(spec)

    scale = np.linspace(0, 1, freqbins) ** factor
    scale *= (freqbins-1)/max(scale)
    scale = np.unique(np.round(scale))

    # create spectrogram with new freq bins
    newspec = np.complex128(np.zeros([timebins, len(scale)]))
    for i in range(0, len(scale)):        
        if i == len(scale)-1:
            newspec[:,i] = np.sum(spec[:,int(scale[i]):], axis=1)
        else:        
            newspec[:,i] = np.sum(spec[:,int(scale[i]):int(scale[i+1])], axis=1)

    # list center freq of bins
    allfreqs = np.abs(np.fft.fftfreq(freqbins*2, 1./sr)[:freqbins+1])
    freqs = []
    for i in range(0, len(scale)):
        if i == len(scale)-1:
            freqs += [np.mean(allfreqs[int(scale[i]):])]
        else:
            freqs += [np.mean(allfreqs[int(scale[i]):int(scale[i+1])])]

    return newspec, freqs

""" plot spectrogram"""
def plotstft(audiopath, binsize=2**10, plotpath=None, colormap="jet"):
    samplerate, samples = wav.read(audiopath)

    s = stft(samples, binsize)

    sshow, freq = logscale_spec(s, factor=1.0, sr=samplerate)

    ims = 20.*np.log10(np.abs(sshow)/10e-6) # amplitude to decibel

    timebins, freqbins = np.shape(ims)

    print("timebins: ", timebins)
    print("freqbins: ", freqbins)

    plt.figure(figsize=(15, 7.5))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, interpolation="none")
    plt.colorbar()

    plt.xlabel("time (s)")
    plt.ylabel("frequency (hz)")
    plt.xlim([0, timebins-1])
    plt.ylim([0, freqbins])

    xlocs = np.float32(np.linspace(0, timebins-1, 5))
    plt.xticks(xlocs, ["%.02f" % l for l in ((xlocs*len(samples)/timebins)+(0.5*binsize))/samplerate])
    ylocs = np.int16(np.round(np.linspace(0, freqbins-1, 10)))
    plt.yticks(ylocs, ["%.02f" % freq[i] for i in ylocs])

    if plotpath:
        plt.savefig(plotpath, bbox_inches="tight")
    else:
        plt.show()

    plt.clf()

    return ims
def genrateSpectroGram(path:str,id:str):
    plotstft(path,plotpath=f"./TEMP/{id}.png")
    data = cv2.imread(f"./TEMP/{id}.png")
    os.remove(f"./TEMP/{id}.png")
    return data[13:593,104:1032]




def RunModel(id:str,model):
    Result[id] = {"out":None,"status":0,"message":"file start processing"}
    try:
        y, s = librosa.load(f'./uploaded/{id}.wav', sr=32000)
        duration = len(y)/32000
        
        if duration<=8 and duration>=6:
            # file resampled
            write(f'./uploaded/{id}.wav',32000,y)
            Result[id] = {"out":None,"status":1,"message":"file get resampled"}
            # file resampled
            img = genrateSpectroGram(f'./uploaded/{id}.wav',id)
            Result[id] = {"out":None,"status":2,"message":"file converted into spectrogram"}
            # data preprocessing
            img = cv2.resize(img,(256,256))
            img = img/255
            img = np.array([img])
            Result[id] = {"out":None,"status":3,"message":"data pre processing done"}
            # MODEL prediction
            result = model.predict(img)
            Result[id] = {"out":None,"status":4,"message":"model processing the data"}
            # Result
            Result[id] = {"out":int(result[0][0]),"status":5,"message":"model prediction"}
            
        else:
            Result[id] = {"out":None,"status":-1,"message":"duration error"}
            return
    except:
        # file pasrse error
        Result[id] = {"out":None,"status":-2,"message":"file parse error"}
        return


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    temp = await file.read()
    id = str(uuid4())
    path = f"./uploaded/{id}.wav"
    with open(path, 'a') as file:
        pass
    with open(path, 'wb') as file:
        file.write(temp)
    background_tasks.add_task(RunModel, id, MODEL)
    return {"id": id}

@app.get('/status/')
async def checkStatus(id: str):
    if Result.get(id)!= None:
        print(Result.get(id))
        return Result.get(id)
    else:
        return {"out":None,"status":None,"message":"server retrive the file"}
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", reload=True, port=8000)