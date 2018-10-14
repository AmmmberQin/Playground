# -*- coding: utf-8 -*-
import time
import os
import sys
import numpy as np
import wave
import math
import random
import pygame
import argparse
from collections import deque

'''
C4 | 261.6
Eb | 311.1
F  | 349.2
G  | 392.0
Bb | 466.2 
'''
# 采样率44100HZ，产生5s的220HZ的正弦波音频
def foo(freq, file_name):
    sRate = 44100
    nSamples = sRate * 5
    x = np.arange(nSamples)/float(sRate)
    vals = np.sin(2.0*math.pi*freq*x)
    data = np.array(vals*32767, 'int16').tostring()
    file = wave.open(file_name, 'wb')
    file.setparams((1,2,sRate,nSamples,'NONE','uncompressed'))
    file.writeframes(data)
    file.close()

def generateNote(freq):
    nSamples = 44100
    sampleRate = 44100
    N = sampleRate//freq
    buf = deque([random.random() - 0.5 for _ in range(N)])
    samples = np.array([0]*nSamples, 'float32')
    for i in range(nSamples):
        samples[i] = buf[0]
        avg = 0.996 * 0.5 * (buf[0] + buf[1])
        buf.append(avg)
        buf.popleft()
    samples = np.array(samples*32767, 'int16')
    return samples.tostring()

def writeWave(fname, data):
    file = wave.open(fname, 'wb')
    nChannels = 1
    sampleWidth = 2
    frameRate = 44100
    nFrames = 44100
    file.setparams((nChannels, sampleWidth, frameRate, nFrames, 'NONE', 'uncompressed'))
    file.writeframes(data)
    file.close()

class NotePlayer():
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        self.notes = {}

    def add(self, filename):
        self.notes[filename] = pygame.mixer.Sound(filename)

    def play(self, filename):
        try:
            self.notes[filename].play()
        except:
            print(f"{filename} not found!")
    def playRandom(self):
        index = random.randint(0, len(self.notes)-1)
        note = list(self.notes.values())[index]
        note.play()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generating sounds with Karplus String Algorithm")
    parser.add_argument('-d','--display', action='store_true', required=False)
    parser.add_argument('-p','--play', action='store_true', required=False)
    parser.add_argument('-o','--piano', action='store_true', required=False)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    gShowPlot = False
    pmNotes = {'C4': 262, 'Eb': 311, 'F': 349, 'G':391, 'Bb':466}
    args = parse_arguments()
    if args.display:
        gShowPlot = True
        plt.ion()

    nplayer = NotePlayer()
    print("Creating notes...")
    for name, freq in list(pmNotes.items()):
        fileName = f"{name}.wav"
        if not os.path.exists(fileName) or args.display:
            data = generateNote(freq)
            print(f'Creating {fileName}...')
            writeWave(fileName, data)
        else:
            print(f"{fileName} already created, skipping...")

        nplayer.add(fileName)

        if args.display:
            nplayer.play(fileName)
            time.sleep(0.5)

    if args.play:
        while True:
            try:
                nplayer.playRandom()
                rest = np.random.choice([1, 2, 4, 8], 1, p=[0.15, 0.7, 0.1, 0.05])
                time.sleep(0.25*rest[0])
            except KeyboardInterrupt:
                sys.exit()

    if args.piano:
        while True:
            for event in pygame.event.get():
                if (event.type == pygame.KEYUP):
                    print("key pressed")
                    nplayer.playRandom()
                    time.sleep(0.5)