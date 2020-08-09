import zmq
import time
import sys

class Forward_device(object):

    def __init__(self, frontend_port, backend_port):
        self.frontend_port = frontend_port
        self.backend_port = backend_port

        print("zmq forwarder: initialize")
        self.context = zmq.Context(1)
        # Socket facing clients
        self.frontend = self.context.socket(zmq.SUB)
        self.frontend.bind("tcp://*:%s" % (self.frontend_port))

        self.frontend.setsockopt_string(zmq.SUBSCRIBE, "")
        print("frontend")
        #time.sleep(1)

        # Socket facing services
        self.backend = self.context.socket(zmq.PUB)
        self.backend.bind("tcp://*:%s" % (self.backend_port))
        print("backend")

    def connect(self):
        print("zmq forwarder: connect port",
            self.frontend_port, "--->", self.backend_port)
        zmq.proxy(self.frontend, self.backend)
        print("zmq forwarder: connected")

    def shutdown(self):
        print("zmq forwarder: terminated")
        self.frontend.close()
        self.backend.close()
        self.context.term()

if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 3:
        forward = Forward_device(args[1], args[2])
        forward.connect()
    else:
        print("Argument are too short")
