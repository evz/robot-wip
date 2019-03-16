import time
import logging

import brickpi3

module_logger = logging.getLogger(__file__)
motor_logger = logging.getLogger('motors')

class SensorTimeoutError(Exception):
    pass


class MotorTimeoutError(Exception):
    pass


class Motor(brickpi3.BrickPi3):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.position_tolerance = 7

    def reset_position(self):
        self.set_position(0)

    def set_power(self, power=None):
        if not power:
            power = self.power

        self.set_motor_power(self.port, power)

    def get_position(self):
        return self.get_motor_encoder(self.port)

    def set_position(self, position):
        motor_logger.debug('setting {} to position {}'.format(self.name, position))
        upper_limit = self.position_tolerance + position
        lower_limit = position - self.position_tolerance

        current_position = self.get_position()

        self.set_motor_position(self.port, position)
        self.wait(current_position,
                  lower_limit,
                  upper_limit)

    def set_position_relative(self, relative_degrees):
        current_position = self.get_position()
        target_position = current_position + relative_degrees
        self.set_position(target_position)

    def wait(self, current_position, lower_limit, upper_limit):
        motor_logger.debug('{} current_position before op {}'.format(self.name, current_position))
        motor_logger.debug('lower_limit: {}, upper_limit: {}'.format(lower_limit, upper_limit))

        within_bounds = lower_limit < current_position < upper_limit

        while not within_bounds:
            motor_logger.debug('{} current_position before {}'.format(self.name, current_position))
            time.sleep(0.1)

            motor_logger.debug('{} current_position after {}'.format(self.name, current_position))

            current_position = self.get_position()
            within_bounds = lower_limit < current_position < upper_limit


class Sensor(brickpi3.BrickPi3):

    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.port = port
        self.timeout = 5

    def read_sensor(self):
        value = None

        wait_time = 0

        while not value:
            if wait_time > self.timeout:
                raise SensorTimeoutError('The sensor on {} timed out'.format(sensor))
            try:
                value = self.get_sensor(self.port)
            except brickpi3.SensorError:
                pass

            time.sleep(0.2)
            wait_time += 0.2

        return value
