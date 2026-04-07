# config.py

# Select target board: "esp32" or "pico"
BOARD = "pico"

# -----------------------------
# Board-specific pin mappings
# -----------------------------
if BOARD == "esp32":
    # HC-SR04 pins
    TRIG_PIN = 26
    ECHO_PIN = 4

    # Legacy stepper pin mappings kept for future use
    U5_STEPPER_PINS = [13, 12, 14, 27]
    U6_STEPPER_PINS = [23, 19, 18, 5]

    # Servo pin for scanner
    SERVO_PIN = 13

    # I2C + XSHUT pins
    I2C_SDA = 21
    I2C_SCL = 22

    TOF1_XSHUT = 25   # U2
    TOF2_XSHUT = 32   # U3
    TOF3_XSHUT = 33   # U4

elif BOARD == "pico":
    # Raspberry Pi Pico GPIO pins
    # Adjust these to match your wiring.

    # HC-SR04 pins
    TRIG_PIN = 2
    ECHO_PIN = 3

    # Legacy stepper pin mappings kept for future use
    U5_STEPPER_PINS = [6, 7, 8, 9]
    U6_STEPPER_PINS = [10, 11, 12, 13]

    # Servo pin for scanner
    SERVO_PIN = 6

    # I2C + XSHUT pins
    I2C_SDA = 16
    I2C_SCL = 17

    TOF1_XSHUT = 18   # U2
    TOF2_XSHUT = 19   # U3
    TOF3_XSHUT = 20   # U4

else:
    raise ValueError("Unsupported BOARD. Use 'esp32' or 'pico'.")

# Legacy alias kept for old stepper code paths
STEPPER_PINS = U5_STEPPER_PINS

# Optional future I2C addresses
TOF1_ADDR = 0x30
TOF2_ADDR = 0x31
TOF3_ADDR = 0x32

# -----------------------------
# Legacy stepper tuning
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

# -----------------------------
# Servo scan tuning
# -----------------------------
SERVO_BASE_DELAY = 0.01
SERVO_PER_DEGREE_DELAY = 0.0015
POST_READ_DELAY = 0.0