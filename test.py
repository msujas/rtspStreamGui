#from ffpyplayer.player import MediaPlayer
import time
import numpy as np
import cv2

lib_opts = {'framerate':'30', 'video_size':'320x240',
'pixel_format': 'yuv420p', 'rtbufsize':'27648000'}
ff_opts = {'f':'dshow'}
ff_opts =  {}
address = 'rtsp://fisheye-bm31.esrf.fr:554/stream1'
#player = MediaPlayer(address)
                     #ff_opts=ff_opts, lib_opts=lib_opts)'
def run():
    vcap = cv2.VideoCapture(address)
    count = 0

    '''
    while 1:
        
        frame, val = player.get_frame()
        if val == 'eof':
            break
        elif frame is None:
            time.sleep(0.01)
            count += 1
        else:
            img, t = frame
            h = img.get_size()[1]
            w = img.get_size()[0]

            break
    '''
    while 1:
        t0=time.time()
        #frame, val = player.get_frame()
        #ret,array = vcap.read()
        ret = vcap.grab()
        ret,array = vcap.retrieve()
        '''   
        if frame is None:
            continue
        img, t = frame
        #print(val, t, img.get_pixel_format(), img.get_buffer_size())
        #time.sleep(val)

        
        array = np.uint8(np.asarray(list(img.to_bytearray()[0])).reshape(h,w,3))
        array = array[:,:,::-1]
        ttest = time.time()
        
        print(f'{ttest-t0:.2e}')
        '''

        resize = cv2.resize(array,(960,540))
        #print(array.shape)
        
        cv2.imshow('test',resize)
        t1=time.time()
        #print(1/(t1-t0))
        key = cv2.waitKey(1)
        if key == 27:
            break
            
    cv2.destroyAllWindows()

run()

