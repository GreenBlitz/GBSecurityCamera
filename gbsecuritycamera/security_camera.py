from base64 import standard_b64encode
import time
from threading import Thread
from typing import Tuple

import gbvision as gbv
import requests


class SecurityCamera(gbv.USBCamera):
    def __init__(self, ip: str, rtsp_port=554, data=gbv.UNKNOWN_CAMERA, user='admin', password=''):
        self.ip = ip
        self.rtsp_port = rtsp_port
        self.user = user
        self.password = password
        super().__init__(f'rtsp://{ip}:{rtsp_port}', data)

    @staticmethod
    def __create_move_request(x, y):
        return ('continuouspantiltmove', f'{x}, {y}'),

    def __request(self, action: str, params: Tuple):
        """
        send request to cam

        :param action: name of request
        :param params: tuple of tuples as each tuple includes param name and value

        :return: request object
        """
        auth = f'{self.user}:{self.password}'
        auth = standard_b64encode(auth.encode('ascii'))
        headers = {'Authorization': f'Basic {auth.decode()}'}
        return requests.get(f'http://{self.ip}/{action}', headers=headers, params=params)

    def __send_move_action(self, params):
        self.__request('ptz.cgi', params)

    def set_power(self, x, y):
        self.__send_move_action(self.__create_move_request(x, y))

    def stop(self):
        self.set_power(0, 0)

    def set_power_timeout(self, x, y, timeout):
        def __proc():
            self.set_power(x, y)
            time.sleep(timeout)
            self.stop()

        Thread(target=__proc).start()
