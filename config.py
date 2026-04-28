# config.py
# ESP32 + sonarBins baseline configuration
# Keep the user's sonarBins baseline/bin algorithm as the detection core.

# -------------------------------------------------
# Pin Layout
# -------------------------------------------------

# Ultrasonic center sensor
TRIG_PIN = 5
ECHO_PIN = 18

# Servo
SERVO_PIN = 19

# I2C Bus for ToF sensors
I2C_SDA = 21
I2C_SCL = 22

# ToF / LiDAR XSHUT pins
LEFT_XSHUT = 25
RIGHT_XSHUT = 26

# ToF I2C addresses
TOF1_ADDR = 0x30
TOF2_ADDR = 0x31

# Optional compatibility aliases
TOF1_XSHUT = LEFT_XSHUT
TOF2_XSHUT = RIGHT_XSHUT
TOF3_XSHUT = None

# -------------------------------------------------
# Legacy Stepper Pins (unused by current algorithm)
# -------------------------------------------------
U5_STEPPER_PINS = [13, 12, 14, 27]
U6_STEPPER_PINS = [23, 19, 18, 5]

STEPPER_PINS = U5_STEPPER_PINS

STEPS_PER_REV = 4096
STEP_DELAY_MS = 2

# -------------------------------------------------
# Physical Servo Range
# -------------------------------------------------
# The servo can move a little wider than the scan range.
MIN_ANGLE = 80
MAX_ANGLE = 190

# -------------------------------------------------
# Algorithm Sweep Range
# -------------------------------------------------
# Detection scans this range, then ignores margin bins near the edges.
START_ANGLE = 90
END_ANGLE = 180

SCAN_MARGIN_DEGREES = 6

BINS = 45
STEP_ANGLE = 2

PARK_ANGLE = START_ANGLE

# -------------------------------------------------
# Detection Settings
# -------------------------------------------------
ERROR_MARGIN = 0.35
ERROR_RATIO = 0.75
INIT_SWEEPS = 5
DELAY = 0.002
DEBUG = True

# -------------------------------------------------
# Servo Timing
# -------------------------------------------------
SERVO_BASE_DELAY = 0.02
SERVO_PER_DEGREE_DELAY = 0.002
POST_READ_DELAY = 0.0

# -------------------------------------------------
# Tracking Settings
# -------------------------------------------------
TRACK_STEP = 2
TRACK_LOST_LIMIT = 8
TRACK_SETTLE_DELAY = 0.03
TRACK_MIN_SCORE = ERROR_MARGIN
TRACK_MAX_CYCLES = 80

LEFT_SENSOR_OFFSET = -10
RIGHT_SENSOR_OFFSET = 10
