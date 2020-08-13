import os
import array
import time
import struct
import random
from threading import Thread

import donkeycar as dk
import zmq

class Test_JoyStickSub(object):
    '''
    Use Zero Message Queue (zmq) to subscribe to control messages from a remote joystick
    '''
    def __init__(self, ip, port = 5560):
        import zmq
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://%s:%d" % (ip, port))
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.button = None
        self.button_state = 0
        self.axis = None
        self.axis_val = 0.0
        self.running = True

    def shutdown(self):
        self.running = False
        time.sleep(0.1)

    def update(self):
        while self.running:
            #payload = self.socket.recv().decode("utf-8")
            payload = self.socket.recv_string()
            print("got", payload)
            button, button_state, axis, axis_val = payload.split(' ')
            self.button = button
            self.button_state = (int)(button_state)
            self.axis = axis
            self.axis_val = (float)(axis_val)
            if self.button == "0":
                self.button = None
            if self.axis == "0":
                self.axis = None

    def run_threaded(self):
        pass

    def poll(self):
        ret = (self.button, self.button_state, self.axis, self.axis_val)
        self.button = None
        self.axis = None
        return ret

if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2:
        try:
            print("*** test joystick controller")
            #
            cfg = dk.load_config()

            js_down_port = int(args[1]) + 1
            print("port of zmq proxy: ", js_down_port)
            netwkJs = Test_JoyStickSub(ip=cfg.NETWORK_JS_SERVER_IP, port=js_down_port)
            while True:
                netwkJs.update()
        except KeyboardInterrupt:
            print("keyboard Interrupt")    
    else:
        print("Argument are too short")        

