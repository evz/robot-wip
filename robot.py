import time
import logging
import logging.config
import math

import brickpi3
# from rubikscubesolver import Side, Square

from base import Motor, Sensor

module_logger = logging.getLogger(__file__)
sensor_logger = logging.getLogger('sensors')
motor_logger = logging.getLogger('motors')


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

    #   white = (235, 254, 250)
    #   green = (20, 105, 74)
    #   yellow = (210, 208, 2)
    #   orange = (148, 53, 9)
    #   blue = (22, 57, 103)
    #   red = (104, 4, 2)

    NORMALIZED_COLORS = {
        (235, 254, 250,): 'White',
        (20, 105, 74,): 'Green',
        (210, 208, 2,): 'Yellow',
        (148, 53, 9,): 'Orange',
        (22, 57, 103,): 'Blue',
        (104, 4, 2,): 'Red',
    }

    def __init__(self, **kwargs):
        super().__init__(self.PORT_1, **kwargs)
        self.set_sensor_type(self.port, self.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS)

    def get_normalized_color(self):
        observed_value = self.read_sensor()
        sensor_logger.debug('raw RGB {}, {}, {}'.format(*observed_value[:3]))

        def color_distance(color_tuple_1, color_tuple_2):
            (red1, green1, blue1,) = color_tuple_1
            (red2, green2, blue2,) = color_tuple_2

            return math.sqrt(((red1 - red2) ** 2) + ((green1 - green2) ** 2) + ((blue1 - blue2) ** 2))

        comparison_colors = list(self.NORMALIZED_COLORS.keys())
        sorted_comparisons = sorted(comparison_colors, key=lambda color: color_distance(color, observed_value[:3]))
        closest_color = sorted_comparisons[0]
        return self.NORMALIZED_COLORS[closest_color]


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
        self.wait_time = 0.5

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
            sensor_logger.debug('Waiting for cube {}'.format(value))
            time.sleep(self.wait_time)

    def read_cube_face(self):
        # self.wait_for_cube()

        self.color_sensor_arm.set_position(-475)
        color = self.color_sensor.get_normalized_color()
        sensor_logger.info('color {}'.format(color))

        self.color_sensor_arm.set_position_relative(130)
        color = self.color_sensor.get_normalized_color()
        sensor_logger.info('color {}'.format(color))

        # Spin the cube to read all the squares
        for side in range(7):

            self.spinner.set_position_relative(140)
            time.sleep(self.wait_time)

            # The corner pieces are a little farther out so we need to adjust for them
            if side in [0, 2, 4, 6]:
                self.color_sensor_arm.set_position_relative(60)
            elif side in [1, 3, 5]:
                self.color_sensor_arm.set_position_relative(-60)

            time.sleep(self.wait_time)

            color = self.color_sensor.get_normalized_color()
            sensor_logger.info('color {}'.format(color))


if __name__ == "__main__":
    import sys

    logging_config = {
        'formatters': {
            'normal': {
                'format': '%(asctime)s %(module)s.%(lineno)-4s %(levelname)s - %(message)s',
                'datefmt' : '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'normal',
                'level': 'DEBUG',
            }
        },
        'loggers': {
            'sensors': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
            'motors': {
                'level': 'INFO',
                'handlers': ['console'],
            },
        },
        'version': 1
    }

    logging.config.dictConfig(logging_config)

    robot = Robot()
    robot.reset_motor_positions()
    robot.read_cube_face()
    robot.reset_motor_positions()
