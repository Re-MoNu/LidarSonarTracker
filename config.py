# config.py

# -----------------------------
# HC-SR04 pins
# -----------------------------
TRIG_PIN = 26
ECHO_PIN = 4

# -----------------------------
# Stepper motor pins
# U5 = scanner stepper
# U6 = second stepper
# -----------------------------
U5_STEPPER_PINS = [13, 12, 14, 27]
U6_STEPPER_PINS = [23, 19, 18, 5]

# For sonarBins scanner, use U5
STEPPER_PINS = U5_STEPPER_PINS

# -----------------------------
# ToF I2C + XSHUT pins
# -----------------------------
I2C_SDA = 21
I2C_SCL = 22

TOF1_XSHUT = 25   # U2
TOF2_XSHUT = 32   # U3
TOF3_XSHUT = 33   # U4

# Optional future I2C addresses
TOF1_ADDR = 0x30
TOF2_ADDR = 0x31
TOF3_ADDR = 0x32

# -----------------------------
# Stepper tuning
# -----------------------------
STEPS_PER_REV = 4096
STEP_DELAY_MS = 2

# -----------------------------
# Sweep range
# -----------------------------
MIN_ANGLE = 0
MAX_ANGLE = 180

# -----------------------------
# sonarBins config
# -----------------------------
BINS = 60
STEP_ANGLE = 2
START_ANGLE = 0
END_ANGLE = 180
ERROR_MARGIN = 0.15
ERROR_RATIO = 0.6
DELAY = 0.002
DEBUG = True

INIT_SWEEPS = 3