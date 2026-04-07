# hardware.py
# Hardware wrapper for:
# - 28BYJ-48 + ULN2003 stepper
# - HC-SR04 ultrasonic
# Compatible with sonarBins interface:
#   move(angle)
#   read()
#   alert(angle)

from machine import Pin, time_pulse_us
import time


class Stepper28BYJ48:
    # Half-step sequence for ULN2003
    SEQ = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1],
    ]

    def __init__(self, pins, step_delay_ms=2):
        self.pins = [Pin(p, Pin.OUT) for p in pins]
        self.step_delay_ms = step_delay_ms
        self.index = 0
        self.current_step_position = 0
        self.release()

    def _write(self, pattern):
        for pin, val in zip(self.pins, pattern):
            pin.value(val)

    def step(self, steps, direction=1):
        for _ in range(abs(steps)):
            self.index = (self.index + direction) % len(self.SEQ)
            self._write(self.SEQ[self.index])
            self.current_step_position += direction
            time.sleep_ms(self.step_delay_ms)

    def release(self):
        for pin in self.pins:
            pin.value(0)


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
        except OSError:
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
        motor_pins,
        trig_pin,
        echo_pin,
        min_angle=0,
        max_angle=180,
        steps_per_rev=4096,
        step_delay_ms=2,
    ):
        self.motor = Stepper28BYJ48(motor_pins, step_delay_ms=step_delay_ms)
        self.sonar = HCSR04(trig_pin, echo_pin)

        self.min_angle = min_angle
        self.max_angle = max_angle
        self.steps_per_rev = steps_per_rev
        self.steps_per_degree = steps_per_rev / 360.0

        self.current_angle = 0

    def _clamp_angle(self, angle):
        if angle < self.min_angle:
            return self.min_angle
        if angle > self.max_angle:
            return self.max_angle
        return angle

    def angle_to_steps(self, angle):
        return int(angle * self.steps_per_degree)

    def move(self, angle):
        """
        Move scanner to an absolute angle in degrees.
        """
        angle = self._clamp_angle(angle)

        target_steps = self.angle_to_steps(angle)
        current_steps = self.angle_to_steps(self.current_angle)
        delta_steps = target_steps - current_steps

        if delta_steps > 0:
            self.motor.step(delta_steps, direction=1)
        elif delta_steps < 0:
            self.motor.step(-delta_steps, direction=-1)

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