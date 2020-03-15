import gbsecuritycamera as gbsc
import gbvision as gbv


def main():
    camera = gbsc.SecurityCamera('10.0.0.8')
    camera.set_frame_size(640, 480)
    # camera.wait_start_reading()
    window = gbv.CameraWindow('feed', camera)

    camera.set_power_timeout(-1.0, -1.0, 0)
    window.show()


if __name__ == '__main__':
    main()
