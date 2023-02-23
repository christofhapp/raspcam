import PySpin
import cv2
from datetime import datetime
import os

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

    return cam

def getPic(cam):
    cam.TriggerSoftware.Execute()
    img_result = cam.GetNextImage()
    img = img_result.Convert(PySpin.PixelFormat_BGR8)
    return img.GetNDArray()

def clear(cam):
    cam.EndAcquisition()
    cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
    cam.DeInit()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    cam = init()

    cv2.namedWindow('image', cv2.WINDOW_FULLSCREEN)


    path = '/home/pi/Desktop/Fotos/'

    for i in range(10):
        img = getPic(cam)
        zeit = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        imgKlein = cv2.resize(img, (640, 480))
        cv2.imshow('image', imgKlein)
        cv2.imwrite(path + zeit + '.png', img)
        print(zeit+'.png saved')
        wk = cv2.waitKey(1)
        if wk == ord('q'):
            break

    clear(cam)
    cv2.destroyAllWindows()

    #while True:
    #    img = getPic(cam)
    #    cv2.imshow('image', img)
    #    wk = cv2.waitKey(1)
    #    if wk == ord('q'):
    #        break

    #cv2.destroyAllWindows()
