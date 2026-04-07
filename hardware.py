# hardware.py
# Hardware wrapper for:
# - Servo motor scanner
# - HC-SR04 ultrasonic
# Compatible with sonarBins interface:
#   move(angle)
#   read()
#   alert(angle)

from machine import Pin, PWM, time_pulse_us
import time


class ServoMotor:
    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.freq = freq
        self.min_us = min_us
        self.max_us = max_us
        self.current_angle = None
        self.write_angle(0)

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
        # Send trigger pulse
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

        # Convert microseconds to centimeters
        return (duration / 2) / 29.1


class SweepScanner:
    """
    sonarBins-compatible wrapper:
      move(angle)
      read()
      alert(angle)
    """

    def __init__(
        self,
        motor_pin,
        trig_pin,
        echo_pin,
        min_angle=0,
        max_angle=180,
    ):
        self.motor = ServoMotor(motor_pin)
        self.sonar = HCSR04(trig_pin, echo_pin)

        self.min_angle = min_angle
        self.max_angle = max_angle

        if self.min_angle > self.max_angle:
            raise ValueError("min_angle must be <= max_angle")

        self.current_angle = self.min_angle

    def _clamp_angle(self, angle):
        if angle < self.min_angle:
            return self.min_angle
        if angle > self.max_angle:
            return self.max_angle
        return angle

    def move(self, angle):
        """
        Move scanner to an absolute angle in degrees.
        """
        angle = self._clamp_angle(angle)
        self.motor.write_angle(angle)
        self.current_angle = angle

    def read(self):
        """
        Return ultrasonic distance in cm, or None on bad read.
        """
        d = self.sonar.distance_cm()

        if d is None:
            return None

        # simple sanity filter
        if d <= 0 or d > 400:
            return None

        return d

    def alert(self, angle):
        """
        Called by sonarBins when a deviation is detected.
        """
        print("ALERT at angle:", angle)

    def home(self):
        self.move(self.min_angle)

    def release(self):
        self.motor.release()