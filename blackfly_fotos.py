import PySpin
import cv2
from datetime import datetime, timedelta
import os
import time
import signal




def init():
    if 'BFsys' not in globals():
        try:
            global BFsys, BFcamlist
            BFsys = PySpin.System.GetInstance()
            BFcamlist = BFsys.GetCameras()
            print('Blackfly System initialized')
        except PySpin.SpinnakerException as ex:
            print('Problem with pyspin.system or system.getcameras: %s' % ex)

        serialRGB = '19346543'

        try:
            cam = BFcamlist.GetBySerial(serialRGB)
            cam.Init()
            if cam.DeviceSerialNumber() == serialRGB:
                print('Cam RGB initialized')
        except PySpin.SpinnakerException as ex:
            print('Cam NOT available: %s' % ex)

        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        if PySpin.IsWritable(cam.SensorShutterMode):
            cam.SensorShutterMode.SetValue(PySpin.SensorShutterMode_Rolling)  # Rolling, GlobalReset GlobalReset: schafft AutoExposure nicht

        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        cam.BeginAcquisition()
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

    return cam

def getPic():
    global cam
    cam.TriggerSoftware.Execute()
    img_result = cam.GetNextImage()
    img = img_result.Convert(PySpin.PixelFormat_BGR8)
    return img.GetNDArray()

def clear():
    global cam
    cam.EndAcquisition()
    cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    cam.DeInit()
    del cam
    print('cam cleared!')


signal.signal(signal.SIGINT, clear)
signal.signal(signal.SIGTERM, clear)
signal.signal(signal.SIGABRT, clear)
signal.signal(signal.SIGSEGV, clear)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    global cam

    cam = init()

    cv2.namedWindow('image', cv2.WINDOW_FULLSCREEN)

    #print('max exposuretime: ',cam.ExposureTime.GetMax())

    path = '/home/pi/Desktop/Fotos/'

    t0 = datetime.now()
    for i in range(100000):
        img = getPic()
        zeit = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        imgKlein = cv2.resize(img, (640, 480))
        cv2.imshow('image', imgKlein)

        if datetime.now()-t0 > timedelta(seconds=20):
            t0 = datetime.now()
            cv2.imwrite(path + zeit + '.png', img)
            print(zeit+'.png saved')
        wk = cv2.waitKey(1)
        if wk == ord('q'):
            break

        #inp = input('exposure time in ms:')

        #if inp == '0':
        #    cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

        #else:
        #    cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        #    exposure_time_to_set = float(inp)*1e3
        #    cam.ExposureTime.SetValue(exposure_time_to_set)




        #time.sleep(2)

    clear()

    cv2.destroyAllWindows()

    #while True:
    #    img = getPic(cam)
    #    cv2.imshow('image', img)
    #    wk = cv2.waitKey(1)
    #    if wk == ord('q'):
    #        break

    #cv2.destroyAllWindows()
