import serial
import time
import struct
import random
import numpy as np
import RPi.GPIO as GPIO
from pydub import AudioSegment
import pygame

# ---- GPIO SETUP ----
BUTTON_PIN = 3  # Change if using a different GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up mode

# ---- SERIAL SENSOR SETUP ----
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# ---- SENSOR COMMANDS ----
NITROGEN_CMD = bytes.fromhex("01 03 00 1E 00 01 E4 0C")
POTASSIUM_CMD = bytes.fromhex("01 03 00 20 00 01 85 C0")
PHOSPHORUS_CMD = bytes.fromhex("01 03 00 20 00 01 85 C0")

# ---- AUDIO SETUP ----
AUDIO_FILE = "/home/gtg662w/Desktop/sound.wav"
SEGMENT_DURATION = 3000  # 1 seconds in milliseconds

# Load audio file
audio = AudioSegment.from_wav(AUDIO_FILE)

# Ensure the file is at least 60 seconds long
if len(audio) < 60000:
    raise ValueError("Audio file must be at least 60 seconds long.")

# Split into 20 segments
segments = [audio[i:i + SEGMENT_DURATION] for i in range(0, 60000, SEGMENT_DURATION)]

# Initialize pygame for audio playback
pygame.mixer.init()

def send_command(command):
    """Send command to sensor and read response"""
    ser.write(command)
    time.sleep(0.1)  # Allow response time
    response = ser.read(7)  # Expecting a 7-byte response
    return response

def parse_response(response):
    """Extract sensor value from response"""
    if len(response) == 7 and response[0] == 0x01 and response[1] == 0x03:
        value = struct.unpack(">H", response[3:5])[0]  # Extract value
        return value
    return None

def get_average_sensor_value():
    """Reads all three sensors and returns the average value"""
    values = []
    
    for cmd in [NITROGEN_CMD, POTASSIUM_CMD, PHOSPHORUS_CMD]:
        response = send_command(cmd)
        value = parse_response(response)
        if value is not None:
            values.append(value)

    if values:
        return sum(values) / len(values)  # Calculate average
    return 0  # Default to 0 if no valid readings

def play_segment(segment):
    """Plays a given audio segment"""
    segment.export("temp.wav", format="wav")  # Save segment temporarily
    pygame.mixer.music.load("temp.wav")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for playback to finish
        time.sleep(0.1)
        
def weighted_shuffle(arr, randomness):
    """Moves elements randomly within a range proportional to randomness."""
    arr = arr[:]
    n = len(arr)
    max_shift = int(randomness * n)  # Max distance an element can move
    
    for i in range(n):
        shift = random.randint(-max_shift, max_shift)
        j = min(n-1, max(0, i + shift))  # Keep within bounds
        arr[i], arr[j] = arr[j], arr[i]
    
    return arr



def start_audio_playback():
    """Reads sensor values and starts playing audio"""
    avg_value = get_average_sensor_value()
    print(f"Average Sensor Value: {avg_value}")
    
    # randomness = (avg_value -  oldmin)*(newmax - newmin) / (oldmax - oldmin) + newmin  
    randomness = (avg_value -  0)*(1 - 0) / (100 - 0) + 0
    
    play_order = weighted_shuffle(segments,randomness)
    

    # # Determine playback order
    # if avg_value < 100:
        # print("Playing segments in RANDOM order")
        # play_order = random.sample(segments, len(segments))  # Shuffle segments
    # else:
        # print("Playing segments in SEQUENTIAL order")
        # play_order = segments  # Play in order

    # Keep playing the segments while the switch is open
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:  # Button released (open)
        for segment in play_order:
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # If button is pressed (closed), stop
                print("Button pressed! Stopping playback...")
                pygame.mixer.music.stop()
                return
            play_segment(segment)

def main_loop():
    """Waits for button release to start playback, stops when pressed again"""
    print("Waiting for button release...")

    while True:
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)  # Wait for button release
        print("Button released! Starting playback...")
        time.sleep(1)
        start_audio_playback()  # Start playback when switch opens

try:
    main_loop()
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
