# main.py

import time
time.sleep(2)  # silent delay so console can attach

try:
    print("BOOT: main.py started")

    from hardware import SweepScanner
    from sonarBins import sonarBins
    from lidarTracker import lidarTracker
    import config

    print("BOOT: imports OK")

    scanner_hw = SweepScanner(
        motor_pin=config.SERVO_PIN,
        trig_pin=config.TRIG_PIN,
        echo_pin=config.ECHO_PIN,
        min_angle=config.MIN_ANGLE,
        max_angle=config.MAX_ANGLE,
        i2c_sda=config.I2C_SDA,
        i2c_scl=config.I2C_SCL,
        left_xshut=config.LEFT_XSHUT,
        right_xshut=config.RIGHT_XSHUT,
        left_addr=config.TOF1_ADDR,
        right_addr=config.TOF2_ADDR,
    )

    print("BOOT: hardware created")

    scanner = sonarBins(
        move=scanner_hw.move,
        read=scanner_hw.read_center,
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
        scan_margin_degrees=config.SCAN_MARGIN_DEGREES,
    )

    print("BOOT: sonarBins created")

    tracker = lidarTracker(
        bins_engine=scanner,
        move=scanner_hw.move,
        read_center=scanner_hw.read_center,
        read_left=scanner_hw.read_left,
        read_right=scanner_hw.read_right,
        alert=scanner_hw.alert,
        track_step=config.TRACK_STEP,
        lost_limit=config.TRACK_LOST_LIMIT,
        settle_delay=config.TRACK_SETTLE_DELAY,
        min_score=config.TRACK_MIN_SCORE,
        max_cycles=config.TRACK_MAX_CYCLES,
        left_offset=config.LEFT_SENSOR_OFFSET,
        right_offset=config.RIGHT_SENSOR_OFFSET,
        debug=config.DEBUG,
    )

    print("BOOT: tracker created")

    print("Parking scanner...")
    scanner_hw.home(config.PARK_ANGLE)
    print("BOOT: parked")

    print("Building baseline...")
    scanner.initialize(sweeps=config.INIT_SWEEPS)
    print("BOOT: baseline complete")

    print("Starting scan + track loop...")

    while True:
        result = scanner.sweep()

        if result is not False:
            print("Deviation detected:", result)
            tracker.track(result)

except Exception as e:
    print("CRASH:", type(e).__name__)
    print(e)

    try:
        import sys
        sys.print_exception(e)
    except Exception:
        pass

    while True:
        time.sleep(1)
