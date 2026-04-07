# main.py
# Clean entry point

from hardware import SweepScanner
from sonarBins import sonarBins
import config
import time

scanner_hw = SweepScanner(
    motor_pin=config.SERVO_PIN,
    trig_pin=config.TRIG_PIN,
    echo_pin=config.ECHO_PIN,
    min_angle=config.MIN_ANGLE,
    max_angle=config.MAX_ANGLE,
)

scanner = sonarBins(
    move=scanner_hw.move,
    read=scanner_hw.read,
    alert=scanner_hw.alert,
    bins=config.BINS,
    step=config.STEP_ANGLE,
    start_angle=config.START_ANGLE,
    end_angle=config.END_ANGLE,
    error_margin=config.ERROR_MARGIN,
    error_ratio=config.ERROR_RATIO,
    delay=config.DELAY,
    debug=config.DEBUG,
    servo_base_delay=config.SERVO_BASE_DELAY,
    servo_per_degree_delay=config.SERVO_PER_DEGREE_DELAY,
    post_read_delay=config.POST_READ_DELAY,
)

print("Parking scanner at start angle...")
scanner_hw.home()

print("Building baseline...")
scanner.initialize(sweeps=config.INIT_SWEEPS)

print("Starting scan loop...")
try:
    while True:
        triggered = scanner.sweep()

        if triggered:
            print("Deviation detected")
except KeyboardInterrupt:
    print("Stopping scan loop...")
finally:
    scanner_hw.home()
    if hasattr(scanner_hw.motor, "release"):
        scanner_hw.motor.release()