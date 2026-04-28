# hardware.py
# Hardware wrapper for:
# - Servo motor scanner
# - HC-SR04 ultrasonic center sensor
# - Two VL53L1X ToF sensors on left/right angled rays
#
# sonarBins-compatible interface:
#   move(angle)
#   read()          -> center ultrasonic alias
#   read_center()   -> ultrasonic center
#   read_left()     -> left VL53L1X
#   read_right()    -> right VL53L1X
#   alert(angle)

from machine import Pin, PWM, I2C, time_pulse_us
import time

try:
    from vl53l1x import VL53L1X
except ImportError:
    VL53L1X = None


class ServoMotor:
    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.freq = freq
        self.min_us = min_us
        self.max_us = max_us
        self.current_angle = None

    def _angle_to_duty_u16(self, angle):
        angle = max(0, min(180, angle))
        pulse_us = self.min_us + (self.max_us - self.min_us) * (angle / 180)
        period_us = 1000000 / self.freq
        return int((pulse_us / period_us) * 65535)

    def write_angle(self, angle):
        angle = max(0, min(180, angle))
        self.pwm.duty_u16(self._angle_to_duty_u16(angle))
        self.current_angle = angle

    def release(self):
        self.pwm.deinit()
        self.current_angle = None


class HCSR04:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.value(0)
        time.sleep_ms(50)

    def distance_cm(self):
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

        try:
            duration = time_pulse_us(self.echo, 1, 30000)
        except (OSError, ValueError):
            return None

        if duration is None or duration <= 0:
            return None

        return (duration / 2) / 29.1


class ToFSensor:
    def __init__(self, sensor):
        self.sensor = sensor

    def read_cm(self):
        if self.sensor is None:
            return None

        try:
            if hasattr(self.sensor, "read"):
                value = self.sensor.read()
            elif hasattr(self.sensor, "distance"):
                value = self.sensor.distance()
            elif hasattr(self.sensor, "read_range_single_millimeters"):
                value = self.sensor.read_range_single_millimeters()
            elif hasattr(self.sensor, "readRangeSingleMillimeters"):
                value = self.sensor.readRangeSingleMillimeters()
            else:
                return None
        except Exception:
            return None

        if value is None:
            return None

        # VL53L1X drivers usually return millimeters.
        # sonarBins baseline currently uses centimeters from the ultrasonic sensor,
        # so convert ToF mm to cm for comparable deviation scoring.
        value_cm = value / 10

        if value_cm <= 0 or value_cm > 400:
            return None

        return value_cm


class SweepScanner:
    def __init__(
        self,
        motor_pin,
        trig_pin,
        echo_pin,
        min_angle=0,
        max_angle=180,
        i2c_sda=None,
        i2c_scl=None,
        left_xshut=None,
        right_xshut=None,
        left_addr=0x30,
        right_addr=0x31,
        tof_required=False,
    ):
        self.motor = ServoMotor(motor_pin)
        self.sonar = HCSR04(trig_pin, echo_pin)

        self.min_angle = min_angle
        self.max_angle = max_angle

        if self.min_angle > self.max_angle:
            raise ValueError("min_angle must be <= max_angle")

        self.current_angle = self.min_angle

        self.i2c = None
        self.left_tof = ToFSensor(None)
        self.right_tof = ToFSensor(None)

        if i2c_sda is not None and i2c_scl is not None:
            self._init_tof_sensors(
                i2c_sda=i2c_sda,
                i2c_scl=i2c_scl,
                left_xshut=left_xshut,
                right_xshut=right_xshut,
                left_addr=left_addr,
                right_addr=right_addr,
                tof_required=tof_required,
            )

    def _clamp_angle(self, angle):
        if angle < self.min_angle:
            return self.min_angle
        if angle > self.max_angle:
            return self.max_angle
        return angle

    def _set_sensor_address(self, sensor, new_addr):
        if sensor is None:
            return False

        try:
            if hasattr(sensor, "set_address"):
                sensor.set_address(new_addr)
                return True
            if hasattr(sensor, "setAddress"):
                sensor.setAddress(new_addr)
                return True

            # Common VL53L1X register for I2C slave device address.
            # Some simple MicroPython drivers do not expose set_address().
            if hasattr(sensor, "writeReg"):
                sensor.writeReg(0x0001, new_addr & 0x7F)
                sensor.address = new_addr & 0x7F
                time.sleep_ms(10)
                return True
        except Exception:
            return False

        return False

    def _start_continuous_if_supported(self, sensor):
        if sensor is None:
            return

        method_names = (
            "start_continuous",
            "startContinuous",
            "start_ranging",
            "StartRanging",
        )

        for name in method_names:
            if hasattr(sensor, name):
                try:
                    method = getattr(sensor, name)
                    try:
                        method()
                    except TypeError:
                        method(50)
                    return
                except Exception:
                    return

    def _init_tof_sensors(
        self,
        i2c_sda,
        i2c_scl,
        left_xshut,
        right_xshut,
        left_addr,
        right_addr,
        tof_required,
    ):
        if VL53L1X is None:
            if tof_required:
                raise RuntimeError("vl53l1x.py is missing from the ESP32 filesystem")
            print("[WARN] vl53l1x.py missing; left/right ToF disabled")
            return

        if left_xshut is None or right_xshut is None:
            if tof_required:
                raise RuntimeError("Both left_xshut and right_xshut are required for dual VL53L1X")
            print("[WARN] XSHUT pins missing; left/right ToF disabled")
            return

        self.i2c = I2C(0, sda=Pin(i2c_sda), scl=Pin(i2c_scl))

        left_shutdown = Pin(left_xshut, Pin.OUT)
        right_shutdown = Pin(right_xshut, Pin.OUT)

        left_shutdown.value(0)
        right_shutdown.value(0)
        time.sleep_ms(20)

        try:
            # Bring up left sensor alone at default address, then move it.
            left_shutdown.value(1)
            time.sleep_ms(20)
            left_sensor = VL53L1X(self.i2c)
            if not self._set_sensor_address(left_sensor, left_addr):
                raise RuntimeError("Could not set left VL53L1X address")
            self._start_continuous_if_supported(left_sensor)
            self.left_tof = ToFSensor(left_sensor)

            # Bring up right sensor. Left is already moved off default address.
            right_shutdown.value(1)
            time.sleep_ms(20)
            right_sensor = VL53L1X(self.i2c)
            if not self._set_sensor_address(right_sensor, right_addr):
                raise RuntimeError("Could not set right VL53L1X address")
            self._start_continuous_if_supported(right_sensor)
            self.right_tof = ToFSensor(right_sensor)

            print("[INFO] VL53L1X left/right initialized")

        except Exception as e:
            self.left_tof = ToFSensor(None)
            self.right_tof = ToFSensor(None)

            if tof_required:
                raise e

            print("[WARN] VL53L1X init failed; left/right ToF disabled")
            try:
                print(e)
            except Exception:
                pass

    def move(self, angle):
        angle = self._clamp_angle(angle)
        self.motor.write_angle(angle)
        self.current_angle = angle

    def read_center(self):
        d = self.sonar.distance_cm()

        if d is None:
            return None

        if d <= 0 or d > 400:
            return None

        return d

    def read_left(self):
        return self.left_tof.read_cm()

    def read_right(self):
        return self.right_tof.read_cm()

    def read(self):
        return self.read_center()

    def alert(self, angle):
        print("ALERT at angle:", angle)

    def home(self, angle=None):
        if angle is None:
            angle = self.min_angle
        self.move(angle)

    def release(self):
        self.motor.release()
