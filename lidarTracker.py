# lidarTracker.py

import time


class lidarTracker:
    """
    Three-ray tracker layered on top of the sonarBins baseline/bin engine.

    This does not replace sonarBins detection. It uses the existing baseline bins
    to score each physical ray:
      - left ToF ray
      - center ultrasonic ray
      - right ToF ray

    Trigger pattern:
      center + left  -> move left
      center + right -> move right
      center only    -> stay
      left only      -> nudge left
      right only     -> nudge right
      nothing        -> lost counter
    """

    def __init__(
        self,
        bins_engine,
        move,
        read_center,
        read_left,
        read_right,
        alert=None,
        track_step=2,
        lost_limit=8,
        settle_delay=0.03,
        min_score=0.25,
        max_cycles=80,
        left_offset=-10,
        right_offset=10,
        center_hold_limit=10,
        debug=False,
    ):
        self.bins_engine = bins_engine
        self.move = move
        self.read_center = read_center
        self.read_left = read_left
        self.read_right = read_right
        self.alert = alert

        self.track_step = track_step
        self.lost_limit = lost_limit
        self.settle_delay = settle_delay
        self.min_score = min_score
        self.max_cycles = max_cycles
        self.left_offset = left_offset
        self.right_offset = right_offset
        self.center_hold_limit = center_hold_limit
        self.debug = debug

    def _clamp_angle(self, angle):
        if angle < self.bins_engine.start_angle:
            return self.bins_engine.start_angle
        if angle > self.bins_engine.end_angle:
            return self.bins_engine.end_angle
        return angle

    def _score_reading(self, ray_angle, distance):
        if distance is None:
            return 0

        if self.bins_engine.baseline is None:
            return 0

        ray_angle = self._clamp_angle(ray_angle)
        bin_index = self.bins_engine._angle2bin(ray_angle)
        baseline = self.bins_engine.baseline[bin_index]

        if baseline is None or baseline == 0:
            return 0

        return abs(distance - baseline) / baseline

    def _read_scores(self, center_angle):
        center_angle = self._clamp_angle(center_angle)

        self.move(center_angle)

        if self.settle_delay > 0:
            time.sleep(self.settle_delay)

        center_distance = self.read_center()
        left_distance = self.read_left()
        right_distance = self.read_right()

        left_angle = center_angle + self.left_offset
        right_angle = center_angle + self.right_offset

        center_score = self._score_reading(center_angle, center_distance)
        left_score = self._score_reading(left_angle, left_distance)
        right_score = self._score_reading(right_angle, right_distance)

        center_hit = center_score >= self.min_score
        left_hit = left_score >= self.min_score
        right_hit = right_score >= self.min_score

        if self.debug:
            print(
                "[TRACK] angle:", center_angle,
                "L:", left_distance, left_score, left_hit,
                "C:", center_distance, center_score, center_hit,
                "R:", right_distance, right_score, right_hit,
            )

        return {
            "left_hit": left_hit,
            "center_hit": center_hit,
            "right_hit": right_hit,
            "left_score": left_score,
            "center_score": center_score,
            "right_score": right_score,
            "left_distance": left_distance,
            "center_distance": center_distance,
            "right_distance": right_distance,
        }

    def _choose_direction(self, scores):
        left_hit = scores["left_hit"]
        center_hit = scores["center_hit"]
        right_hit = scores["right_hit"]

        if center_hit and left_hit and not right_hit:
            return -1, "CENTER+LEFT"

        if center_hit and right_hit and not left_hit:
            return 1, "CENTER+RIGHT"

        if center_hit and not left_hit and not right_hit:
            return 0, "CENTER"

        if left_hit and not center_hit and not right_hit:
            return -1, "LEFT"

        if right_hit and not center_hit and not left_hit:
            return 1, "RIGHT"

        if left_hit and right_hit and not center_hit:
            if scores["left_score"] > scores["right_score"]:
                return -1, "LEFT+RIGHT -> LEFT"
            if scores["right_score"] > scores["left_score"]:
                return 1, "LEFT+RIGHT -> RIGHT"
            return 0, "LEFT+RIGHT -> STAY"

        if left_hit and center_hit and right_hit:
            if scores["left_score"] > scores["right_score"]:
                return -1, "ALL -> LEFT"
            if scores["right_score"] > scores["left_score"]:
                return 1, "ALL -> RIGHT"
            return 0, "ALL -> STAY"

        return None, "LOST"

    def track(self, initial_angle):
        center_angle = self._clamp_angle(initial_angle)
        lost_count = 0
        center_hold_count = 0
        cycles = 0

        self.move(center_angle)

        if self.debug:
            print("[TRACK] start:", center_angle)

        while lost_count < self.lost_limit and cycles < self.max_cycles:
            cycles += 1

            scores = self._read_scores(center_angle)
            direction, label = self._choose_direction(scores)

            if direction is None:
                lost_count += 1
                center_hold_count = 0

                if self.debug:
                    print(
                        "[TRACK] lost:",
                        lost_count,
                        "angle:",
                        center_angle,
                    )

                continue

            lost_count = 0

            if direction == 0:
                center_hold_count += 1

                if self.debug:
                    print(
                        "[TRACK]",
                        label,
                        "angle:",
                        center_angle,
                        "cycle:",
                        cycles,
                        "hold:",
                        center_hold_count,
                    )

                if center_hold_count >= self.center_hold_limit:
                    if self.debug:
                        print("[TRACK] center stable; return to sweep")
                    return center_angle

                continue

            center_hold_count = 0

            if direction < 0:
                center_angle = self._clamp_angle(center_angle - self.track_step)
            elif direction > 0:
                center_angle = self._clamp_angle(center_angle + self.track_step)

            self.move(center_angle)

            if self.alert is not None:
                self.alert(center_angle)

            if self.debug:
                print(
                    "[TRACK]",
                    label,
                    "angle:",
                    center_angle,
                    "cycle:",
                    cycles,
                )

        if self.debug:
            print("[TRACK] return to sweep")

        return center_angle
