import gbsecuritycamera as gbsc
import gbvision as gbv
import cv2


def main():
    camera = gbsc.SecurityCamera('192.168.1.251', password='')
    # camera.wait_start_reading()
    window = gbv.CameraWindow('feed', camera, drawing_pipeline=lambda x: cv2.resize(x, (640, 480)))

    camera.set_power_timeout(-1.0, -1.0, 0)
    window.show()


if __name__ == '__main__':
    main()
