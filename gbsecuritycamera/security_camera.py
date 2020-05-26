from base64 import standard_b64encode
import time
from threading import Thread
from typing import Tuple, List

import gbvision as gbv
import requests
import numpy as np


class SecurityCamera(gbv.USBCamera):
    def __init__(self, ip: str, rtsp_port=554, data=gbv.UNKNOWN_CAMERA, user='admin', password=''):
        """
        A class connecting to the security camera

        :param ip: the ip of the camera
        :param rtsp_port: the port to which the camera streams using rstp (default is 554)
        :param data: the camera data object of the camera
        :param user: the user name of the camera (default is admin)
        :param password: the password to the username (default is empty)
        """
        self.ip = ip
        self.rtsp_port = rtsp_port
        self.user = user
        self.password = password
        super().__init__(f'rtsp://{ip}:{rtsp_port}', data)

    @staticmethod
    def __create_continues_move_request(speed_x, speed_y):
        return ('continuouspantiltmove', f'{speed_x}, {speed_y}'),

    @staticmethod
    def __create_move_request(move, speed):
        return ('move', move), ('speed', speed), ('random', np.random.rand())

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

    def __request_with_random(self, action, params):
        return self.__request(action, params + (('random', np.random.rand()),))

    def __send_ptz(self, params):
        self.__request('ptz.cgi', params)

    def set_power(self, speed_x, speed_y):
        """
        sets the power to the camera's engines

        :param speed_x: the speed by which to move the x axis (sideways)
        :param speed_y: the speed by which to move the y axis (up/down)
        """
        self.__send_ptz(self.__create_continues_move_request(speed_x, speed_y))

    def stop(self):
        """
        stops the camera's movement
        """
        self.set_power(0, 0)

    def set_power_timeout(self, speed_x, speed_y, timeout):
        """
        moves the camera in a constant speed for timeout seconds (unblocking)

        :param speed_x: the speed in the x axis by which to move
        :param speed_y: the speed on the y axis by which to move
        :param timeout: the time (in seconds) to move the camera
        """
        def __proc():
            self.set_power(speed_x, speed_y)
            time.sleep(timeout)
            self.stop()

        Thread(target=__proc).start()

    def to_home(self, speed=50):
        """
        moves the camera to the starting position (home state)

        :param speed: the speed by which to move (default 50)
        """
        self.to_state('home', speed)

    def get_states_list(self) -> List[str]:
        """
        gets the full list of saved state (without 'home')

        :return: a list of all saved state, ordered by the time they were created (excluding 'home')
        """
        answer = self.__request_with_random('asp/config.cgi', (
            ('action', 'list'), ('group', 'PTZ.PresetPos,GuardTour,Fisheye'))).content
        return [x.split('=')[1].split('~')[0] for x in answer.decode('ascii').strip('\n\r').split('\n')]

    def save_state(self, state_name: str):
        """
        saves the current camera location as a state that can be returned to at any time (see \
        `gbsecuritycamera.SecurityCamera.to_state`)

        :param state_name: the name of the state, if this state already exists it will override it
        """
        self.__request_with_random('configptz.cgi', (('setserverpresetname', state_name),))

    def to_state(self, state, speed=50):
        """
        moves the camera to a saved state

        :param state: the name of the saved state (see `gbsecuritycamera.SecurityCamera.save_state`)
        :param speed: the speed in which to move (default 50)
        """
        self.__send_ptz(self.__create_move_request(state, speed))
