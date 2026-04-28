# config.py
# Fixed ESP32 config
# Your algorithm stays the same.
# Only pins / labels updated.

# -------------------------------------------------
# Pin Layout
# -------------------------------------------------

# Ultrasonic Sensor
TRIG_PIN = 5
ECHO_PIN = 18

# Servo
SERVO_PIN = 19

# I2C Bus
I2C_SDA = 21
I2C_SCL = 22

# ToF / LiDAR Labels
LEFT_XSHUT = 25
RIGHT_XSHUT = 26

# Optional compatibility aliases
TOF1_XSHUT = LEFT_XSHUT
TOF2_XSHUT = RIGHT_XSHUT
TOF3_XSHUT = None

# Optional future addresses
TOF1_ADDR = 0x30
TOF2_ADDR = 0x31

# -------------------------------------------------
# Legacy Stepper Pins (unused by current algorithm)
# -------------------------------------------------
U5_STEPPER_PINS = [13, 12, 14, 27]
U6_STEPPER_PINS = [23, 19, 18, 5]

STEPPER_PINS = U5_STEPPER_PINS

STEPS_PER_REV = 4096
STEP_DELAY_MS = 2

# -------------------------------------------------
# Safe Physical Servo Range
# -------------------------------------------------
MIN_ANGLE = 90
MAX_ANGLE = 180

# -------------------------------------------------
# Algorithm Sweep Range
# -------------------------------------------------
START_ANGLE = 90
END_ANGLE = 180

# Match 2° stepping across 50° range
BINS = 36
STEP_ANGLE = 2

# Safe parked angle
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
TRACK_WINDOW = 10
TRACK_STEP = 2
TRACK_LOST_LIMIT = 5
TRACK_SETTLE_DELAY = 0.03
TRACK_MIN_SCORE = ERROR_MARGIN