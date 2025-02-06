from pyo import *

s = Server()
s.setOutputDevice(1)
s.boot()

s.start()

# stereo playback with a slight shift between the two channels.
sf = SfPlayer("dream.aiff", speed=[1, 0.995], loop=True, mul=0.4).out()

s.gui(locals())
