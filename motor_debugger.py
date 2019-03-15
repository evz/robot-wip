import time
import sys
import logging

from robot import Robot

logger = logging.getLogger(__file__)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="A thing to make sure you're not crazy "
                                                 "and your motors are actually doing something")
    parser.add_argument('--motor', help="The name of the motor you want to test", required=True)
    parser.add_argument('--power', help="The power of the rotation", default=15)
    parser.add_argument('--position', help="The position you'd like to move the motor to", default=0)
    parser.add_argument('--debug', help="Crank up the logging, please", action="store_true")

    args = parser.parse_args()

    logger_kwargs = {
        'format': '%(asctime)s %(module)s.%(lineno)-4s %(levelname)s - %(message)s',
        'level': logging.INFO
    }

    if args.debug:
        logger_kwargs['level'] = logging.DEBUG

    logging.basicConfig(**logger_kwargs)

    robot = Robot()

    try:
        motor = getattr(robot, args.motor)
        motor.reset_position()
        # motor.set_power(args.power)
        motor.set_position(int(args.position))
    except AttributeError:
        logging.info('No motor called "{}"'.format(args.motor))
        sys.exit()

    start = time.time()
    current_time = 0

    while current_time < 5:
        logger.debug('Motor position {}'.format(motor.get_position()))
        current_time = time.time() - start
