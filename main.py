# main.py
# Clean entry point

from hardware import SweepScanner
from sonarBins import sonarBins
import config
import time

scanner_hw = SweepScanner(
    motor_pins=config.STEPPER_PINS,
    trig_pin=config.TRIG_PIN,
    echo_pin=config.ECHO_PIN,
    min_angle=config.MIN_ANGLE,
    max_angle=config.MAX_ANGLE,
    steps_per_rev=config.STEPS_PER_REV,
    step_delay_ms=config.STEP_DELAY_MS,
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
)

print("Homing scanner...")
scanner_hw.home()

print("Building baseline...")
scanner.initialize(sweeps=config.INIT_SWEEPS)

print("Starting scan loop...")
while True:
    triggered = scanner.sweep()

    if triggered:
        print("Deviation detected")
        time.sleep_ms(300)