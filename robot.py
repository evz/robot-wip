import time
import logging

import brickpi3
from rubikscubesolver import Side, Square

from base import Motor, Sensor

logger = logging.getLogger(__file__)


class SensorTimeoutError(Exception):
    pass


class MotorTimeoutError(Exception):
    pass


class ColorSensorArm(Motor):
    name = 'Color Sensor Arm'
    def __init__(self, **kwargs):
        super().__init__(self.PORT_C, **kwargs)


class Flipper(Motor):
    name = 'Brick Flipper'
    def __init__(self, **kwargs):
        super().__init__(self.PORT_A, **kwargs)


class Spinner(Motor):
    name = 'Spinner'
    def __init__(self, **kwargs):
        super().__init__(self.PORT_B, **kwargs)


class ColorSensor(Sensor):
    def __init__(self, **kwargs):
        super().__init__(self.PORT_1, **kwargs)
        self.set_sensor_type(self.port, self.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS)


class Ultrasonic(Sensor):
    def __init__(self, **kwargs):
        super().__init__(self.PORT_2, **kwargs)
        self.set_sensor_type(self.port, self.SENSOR_TYPE.EV3_ULTRASONIC_INCHES)


class Robot(object):
    '''
    L = Green
    R = Blue
    U = White
    D = Yellow
    F = Red
    B = Orange
    '''

    def __init__(self):
        self.ultrasonic = Ultrasonic()
        self.color_sensor = ColorSensor()

        self.flipper = Flipper()
        self.spinner = Spinner()
        self.color_sensor_arm = ColorSensorArm()

        self.motors = [self.flipper, self.spinner, self.color_sensor_arm]

    def reset_motor_positions(self):
        for motor in self.motors:
            motor.reset_position()


    def wait_for_cube(self):
        value = None

        # TODO: This always seems to report a number less than 10 now. WHYYY???

        while not value or value > 10:
            value = self.read_sensor(self.ultrasonic)
            logger.debug('Waiting for cube {}'.format(value))
            time.sleep(0.2)

    def read_cube_face(self):
        # self.wait_for_cube()
        self.color_sensor_arm.set_position(-500)
        color = self.color_sensor.read_sensor()
        logger.info('color {}'.format(color))


if __name__ == "__main__":
    import sys

    logger_kwargs = {
        'format': '%(asctime)s %(module)s.%(lineno)-4s %(levelname)s - %(message)s',
        'level': logging.INFO,
    }

    try:
        debug = sys.argv[1]
        logger_kwargs['level'] = logging.DEBUG
    except IndexError:
        pass

    logging.basicConfig(**logger_kwargs)

    robot = Robot()
    robot.reset_motor_positions()
    robot.read_cube_face()
    robot.reset_motor_positions()
