import sys
import cv2
import zmq
import time
import donkeycar as dk
from donkeycar.utils import img_to_binary, arr_to_img

class ZMQValuePub_connect(object):
    '''
    Use Zero Message Queue (zmq) to publish values
    '''
    def __init__(self, name, ip, port = 5556, hwm=10):
        context = zmq.Context()
        self.name = name
        self.socket = context.socket(zmq.PUB)
        self.socket.set_hwm(hwm)
        self.socket.connect("tcp://%s:%d" % (ip, port))

    def run(self, values):
        #packet = { "name": self.name, "val" : values }
        #print("*** ", type(values))
        if values != None:
            #print("send :" , len(values))
            #p = pickle.dumps(packet)
            #z = zlib.compress(p)
            self.socket.send(values)

    def shutdown(self):
        print("shutting down zmq")
        #self.socket.close()
        context = zmq.Context()
        context.destroy()


if __name__ == "__main__":
    cfg = dk.load_config()
    cap.set(3, cfg.IMAGE_W) # WIDTH
    cap.set(4, cfg.IMAGE_H) # HEIGHT
    cap.set(5,4) # FPS

    cloud_cam_ip_address = cfg.NETWORK_CAM_SERVER_IP
    birdview_up_port = cfg.NETWORK_CLOUD_PORT + 4

    cap = cv2.VideoCapture(0)

    pub = ZMQValuePub_connect("web_camera",
                ip=cloud_cam_ip_address, port=birdview_up_port, hwm=1)
    print("start to capture")
    while True:
        ret, img_arr = cap.read()
        image = arr_to_img(img_arr)
        jpg = img_to_binary(image)
        pub.run(jpg)

        k = cv2.waitKey(1)
        if k == 27: #Esc入力時は終了
            break
    # termination
    cap.release()
    pub.shutdown()
