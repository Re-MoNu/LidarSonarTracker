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
    )

    print("BOOT: hardware created")

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

    print("BOOT: sonarBins created")

    tracker = lidarTracker(
        bins_engine=scanner,
        move=scanner_hw.move,
        read=scanner_hw.read,
        alert=scanner_hw.alert,
        track_step=config.TRACK_STEP,
        lost_limit=config.TRACK_LOST_LIMIT,
        settle_delay=config.TRACK_SETTLE_DELAY,
        min_score=config.TRACK_MIN_SCORE,
        max_cycles=config.TRACK_MAX_CYCLES,
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

            if isinstance(result, (int, float)):
                tracker.track(result)
            else:
                print("TRACK SKIPPED: sweep did not return angle")

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