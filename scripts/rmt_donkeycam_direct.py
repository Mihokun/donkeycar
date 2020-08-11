import sys
import os
import time
from threading import Thread
import zmq
import cv2
import numpy as np
import donkeycar as dk
from donkeycar.utils import binary_to_img, img_to_arr


class ZMQValueRcv(object):
    '''
    Use Zero Message Queue (zmq) to publish values
    '''
    def __init__(self, name, port = 5562, hwm=1, return_last=True):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.set_hwm(hwm)
        print("wait for bind")
        self.socket.bind("tcp://*:%d" % port)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.name = name
        self.return_last = return_last
        self.last = None
    
    def run(self):
        '''
        poll socket for input. returns None when nothing was recieved
        otherwize returns packet data
        '''
        try:
            z = self.socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again as e:
            if self.return_last:
                return self.last
            return None

        #if self.name == obj['name']:
        #    self.last = obj['val'] 
        #    return obj['val']
        self.last = z
        return z

        if self.return_last:
            return self.last
        return None

    def shutdown(self):
        print("shutting down zmq")
        #self.socket.close()
        context = zmq.Context()
        context.destroy()

# キャリブレーションCSVファイルを読み込む関数
def loadCalibrationFile(mtx_path, dist_path):
    try:
        mtx = np.loadtxt(mtx_path, delimiter=',')
        dist = np.loadtxt(dist_path, delimiter=',')
    except Exception as e:
        raise e
    return mtx, dist

def donkey_camera(port_no, title, undistort_flag):
    print("receiving camera data...")
    #mtx = [315.30341354,   0. ,         335.86219771,
    #         0. ,         316.76804977, 227.79438377,
    #         0. ,          0. ,          1.        ]
    #dist =  [-3.15014991e-01,  9.69147455e-02,  1.93736862e-03,  2.06359561e-04,  -1.29527346e-02]
    if undistort_flag == True:
        mtx_path = "mtx.csv"
        dist_path = "dist.csv"
        mtx, dist = loadCalibrationFile(mtx_path, dist_path)

    s = ZMQValueRcv("camera", port=port_no, hwm=1, return_last=True)
    while True:
        jpg = s.run()
        #print(res)
        if jpg != None:
            #print("got:", len(jpg))
            image = binary_to_img(jpg)
            img_arr = img_to_arr(image)
            if undistort_flag == False:
                scale = 1
                height = img_arr.shape[0] * scale
                width = img_arr.shape[1] * scale 
                img_bgr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
                result_img = cv2.resize(img_bgr, (width, height))
            else:
                img_bgr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
                result_img = cv2.undistort(img_bgr, mtx, dist, None) # 画像補正

            cv2.imshow(title, result_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 3:
        try:
            print("*** monitor driver view directly")
            #
            cfg = dk.load_config()
            #cloud_ip_address = cfg.NETWORK_CAM_SERVER_IP
            #print("addr of zmq proxy: ", cloud_ip_address)
            donkey_cam1_up_port = int(args[1]) + 2
            print("port of zmq proxy: ", donkey_cam1_up_port)

            undistort_flag = True
            thread_cam1 = Thread(target=donkey_camera, 
                args=(donkey_cam1_up_port, args[2], undistort_flag))

            thread_cam1.start()
        except KeyboardInterrupt:
            print("keyboard Interrupt")
    else:
        print("Argument are too short")
