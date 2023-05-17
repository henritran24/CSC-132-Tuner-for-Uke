import sounddevice as sd
import numpy as np
import scipy.fftpack
import os
import sys
import tkinter as tk
from random import randint
import RPi.GPIO as GPIO

# General settings
SAMPLE_FREQ = 44100 # sample frequency in Hz
WINDOW_SIZE = 44100 # window size of the DFT in samples
WINDOW_STEP = 21050 # step size of window
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ # length of the window in seconds
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ # length between two samples in seconds
windowSamples = [0 for _ in range(WINDOW_SIZE)]

CONCERT_PITCH = 440 #Basic frequency for western music
ALL_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]#list of all notes

NOTE_FREQS = {"G": 392, "C": 262, "E": 330, "A": 444}#Uke
NOTE_FREQS2 = {"E": 82, "A": 110, "D": 146, "G": 196, "B":247, "e":330}#Guitar

TARGET_FREQ = None

green = 16 #GPIO Green
red = 12 #GPIO Red

GPIO.setmode(GPIO.BCM)

GPIO.setup(green, GPIO.OUT)
GPIO.setup(red, GPIO.OUT)

def find_closest_note(pitch):
  # Utilizes a Fourier Transformation to find the note being played
  i = int(np.round(np.log2(pitch/CONCERT_PITCH)*12))
  closest_note = ALL_NOTES[i%12] + str(4 + (i + 9) // 12)
  closest_pitch = CONCERT_PITCH*2**(i/12)
  return closest_note, closest_pitch


def callback(indata, frames, time, status):
  global windowSamples
  if status:
    print(status)
  if any(indata):
    windowSamples = np.concatenate((windowSamples,indata[:, 0])) # append new samples
    windowSamples = windowSamples[len(indata[:, 0]):] # remove old samples
    magnitudeSpec = abs( scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2] )

    for i in range(int(62/(SAMPLE_FREQ/WINDOW_SIZE))):
      magnitudeSpec[i] = 0 

    maxInd = np.argmax(magnitudeSpec)
    maxFreq = maxInd * (SAMPLE_FREQ/WINDOW_SIZE)
    if TARGET_FREQ is not None:
        closestNote, closestPitch = find_closest_note(TARGET_FREQ)
    else:
        closestNote, closestPitch = find_closest_note(maxFreq)
  
    os.system('cls' if os.name=='nt' else 'clear')
    x = f"Closest note: {closestNote} {maxFreq:.1f}/{closestPitch:.1f}" #sets the ouput to a variable

    
    # check if the detected frequency is in tune with the target frequency
    if TARGET_FREQ is not None:
        GPIO.output(green, GPIO.LOW)
        GPIO.output(red, GPIO.LOW)
        if abs(maxFreq - TARGET_FREQ) <= 5:#Gives us a range to tune to, no guitar or Uke will be perfect
            GPIO.output(green, GPIO.HIGH)#Turns green on to show in tune
            x += " (in tune)" # Concatenates orignal output x
            GUIlabel(x,"green")     
        else:
            GPIO.output(red, GPIO.HIGH)#Turn red light on to show out of tune
            x += " (out of tune)" # Concatenates orignal output x
            GUIlabel(x,"red")
            
  else:
        print('no input') # No dected frequency, this is rare because the input is always making a noise,
                           # Troubleshoots interface/mic, ensures there is an acutal input


def GUIlabel(note,color):
  # deletes the old label, and replaces it with a new one with the newest note played
  # also changes the color of the background based on whether it is
  # in tune or not
  global label # text
  label.destroy()# destroys old text
  label = tk.Label(text=f"{note}", bg= color, height=2,font=("Arial",40))#repklaces
  label.grid(row=1,column=0,columnspan=6)
  root.update()#tkinter function for updating GUI


def GUIbutton_callback(note, listy):#listy = NOTE_FREQ UKE and Guitar
  global TARGET_FREQ
  TARGET_FREQ = listy[note]#Accesses lists to set frequency with corresponding note
  # reset the message when a button is pressed
  GUIlabel("","white")


def SetupButton(instra):#accepts parameter for Guitar or UKE
  # delete all old widgets
  for widgets in root.winfo_children():
    widgets.destroy()
  root.children.clear()

  #creates the buttons for the Uke
  if instra == "Uke":
    buttonG = tk.Button(text="G", bg="lightgray", command=lambda: GUIbutton_callback("G",NOTE_FREQS), height = 20, width = 25)
    buttonG.grid(row=0,column=0)

    buttonC = tk.Button(text="C", bg="lightgray", command=lambda: GUIbutton_callback("C",NOTE_FREQS), height = 20, width = 25)
    buttonC.grid(row=0,column=1)

    buttonE = tk.Button(text="E", bg="lightgray", command=lambda: GUIbutton_callback("E",NOTE_FREQS), height = 20, width = 25)
    buttonE.grid(row=0,column=2)

    buttonA = tk.Button(text="A", bg="light gray", command=lambda: GUIbutton_callback("A",NOTE_FREQS), height = 20, width = 25)
    buttonA.grid(row=0,column=3)

    buttonS = tk.Button(text="Switch to Guitar", bg="White", command=lambda: SetupButton("Guitar"), height = 20, width = 25)
    buttonS.grid(row=0,column=4)

  # creates the buttons for the Guitar
  elif instra == "Guitar":
    buttonE = tk.Button(text="E", bg="lightgray", command=lambda: GUIbutton_callback("E",NOTE_FREQS2), height = 20, width = 25)
    buttonE.grid(row=0,column=0)

    buttonA = tk.Button(text="A", bg="lightgray", command=lambda: GUIbutton_callback("A", NOTE_FREQS2), height = 20, width = 25)
    buttonA.grid(row=0,column=1)

    buttonD = tk.Button(text="D", bg="lightgray", command=lambda: GUIbutton_callback("D", NOTE_FREQS2), height = 20, width = 25)
    buttonD.grid(row=0,column=2)

    buttonG = tk.Button(text="G", bg="light gray", command=lambda: GUIbutton_callback("G", NOTE_FREQS2), height = 20, width = 25)
    buttonG.grid(row=0,column=3)

    buttonB = tk.Button(text="B", bg="lightgray", command=lambda: GUIbutton_callback("B", NOTE_FREQS2), height = 20, width = 25)
    buttonB.grid(row=0,column=4)

    buttone = tk.Button(text="e", bg="light gray", command=lambda: GUIbutton_callback("e", NOTE_FREQS2), height = 20, width = 25)
    buttone.grid(row=0,column=5)

    buttonS = tk.Button(text="Switch to Uke", bg="White", command=lambda: SetupButton("Uke"), height = 20, width = 25)
    buttonS.grid(row=0,column=6)
    
  root.update()


#Creates the GUI with tkinter
root = tk.Tk()
root.geometry("1200x900")
label = tk.Label(text = "")
SetupButton("Guitar")

#Start microphone input stream
try:
  with sd.InputStream(channels=1, callback=callback,
    blocksize=WINDOW_STEP,
    samplerate=SAMPLE_FREQ):
    root.mainloop()
    while True:
      pass
except Exception as e:
    print(str(e))



