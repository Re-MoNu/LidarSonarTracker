# lidarTracker.py

import time


class lidarTracker:
    """
    Gradient tracker for sonarBins baseline detection.

    Uses YOUR bin/baseline algorithm.
    It checks left / center / right deviation,
    then moves the center toward the stronger deviation.
    """

    def __init__(
        self,
        bins_engine,
        move,
        read,
        alert=None,
        track_step=2,
        lost_limit=8,
        settle_delay=0.03,
        min_score=0.25,
        max_cycles=80,
        debug=False,
    ):
        self.bins_engine = bins_engine
        self.move = move
        self.read = read
        self.alert = alert

        self.track_step = track_step
        self.lost_limit = lost_limit
        self.settle_delay = settle_delay
        self.min_score = min_score
        self.max_cycles = max_cycles
        self.debug = debug

    def _clamp_angle(self, angle):
        if angle < self.bins_engine.start_angle:
            return self.bins_engine.start_angle
        if angle > self.bins_engine.end_angle:
            return self.bins_engine.end_angle
        return angle

    def _score_angle(self, angle):
        angle = self._clamp_angle(angle)

        self.move(angle)

        if self.settle_delay > 0:
            time.sleep(self.settle_delay)

        distance = self.read()

        if distance is None:
            return 0, distance

        bin_index = self.bins_engine._angle2bin(angle)
        baseline = self.bins_engine.baseline[bin_index]

        if baseline is None or baseline == 0:
            return 0, distance

        score = abs(distance - baseline) / baseline
        return score, distance

    def _best_direction(self, center_angle):
        center_angle = self._clamp_angle(center_angle)

        left_angle = self._clamp_angle(center_angle - self.track_step)
        right_angle = self._clamp_angle(center_angle + self.track_step)

        left_score, left_distance = self._score_angle(left_angle)
        center_score, center_distance = self._score_angle(center_angle)
        right_score, right_distance = self._score_angle(right_angle)

        best_angle = center_angle
        best_score = center_score
        best_distance = center_distance
        direction = "CENTER"

        if left_score > best_score:
            best_angle = left_angle
            best_score = left_score
            best_distance = left_distance
            direction = "LEFT"

        if right_score > best_score:
            best_angle = right_angle
            best_score = right_score
            best_distance = right_distance
            direction = "RIGHT"

        return best_angle, best_score, best_distance, direction

    def track(self, initial_angle):
        center_angle = self._clamp_angle(initial_angle)
        lost_count = 0
        cycles = 0

        if self.debug:
            print("[TRACK] start:", center_angle)

        while lost_count < self.lost_limit and cycles < self.max_cycles:
            cycles += 1

            next_angle, score, distance, direction = self._best_direction(center_angle)

            if score < self.min_score:
                lost_count += 1

                if self.debug:
                    print(
                        "[TRACK] lost:",
                        lost_count,
                        "angle:",
                        center_angle,
                        "score:",
                        score,
                    )

                continue

            lost_count = 0
            center_angle = next_angle

            self.move(center_angle)

            if self.alert is not None:
                self.alert(center_angle)

            if self.debug:
                print(
                    "[TRACK]",
                    direction,
                    "angle:",
                    center_angle,
                    "score:",
                    score,
                    "distance:",
                    distance,
                )

        if self.debug:
            print("[TRACK] return to sweep")

        return center_angle