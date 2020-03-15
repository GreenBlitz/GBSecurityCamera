import time
from threading import Thread

import gbsecuritycamera as gbsc
import gbvision as gbv


def main():
    camera = gbsc.SecurityCamera('10.0.0.8')
    camera.set_frame_size(640, 480)
    # camera.wait_start_reading()
    window = gbv.CameraWindow('feed', camera)
    moving = True

    def __turn_left_and_right():
        while moving:
            camera.set_power(20, 0)
            for i in range(100):
                if moving:
                    time.sleep(0.1)
                else:
                    return
            camera.set_power(-20, 0)
            for i in range(100):
                if moving:
                    time.sleep(0.1)
                else:
                    return

    Thread(target=__turn_left_and_right).start()
    window.show()
    moving = False
    time.sleep(0.2)
    camera.to_home()


if __name__ == '__main__':
    main()
