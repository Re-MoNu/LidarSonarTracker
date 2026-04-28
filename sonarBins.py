import time


class sonarBins:
    def __init__(self, move, read, alert, bins=60, step=2, start_angle=0, end_angle=180, error_margin=0.15, error_ratio=0.6, delay=0.002, debug=False, servo_base_delay=0.01, servo_per_degree_delay=0.0015, post_read_delay=0.0):
        self.move = move
        self.read = read
        self.alert = alert
        self.baseline = None
        self.bins = bins
        self.step = step
        self.delay = delay
        self.servo_base_delay = servo_base_delay
        self.servo_per_degree_delay = servo_per_degree_delay
        self.post_read_delay = post_read_delay
        self.last_init_coverage = 0.0
        self.last_init_valid_bins = 0
        
        self.direction = 1
        
        self.current_angle = start_angle
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.bin_width = (self.end_angle - self.start_angle) / bins
        
        # Warn if step is larger than bin width (may cause skipped bins)
        if self.step > self.bin_width:
            print("[Warning] step is larger than bin width. Scan may cause skipped angles.")
        self.error_margin = error_margin
        self.error_ratio = error_ratio
        
        self.debug=debug
        
    # Returns bin index from angle
    def _angle2bin(self,angle):
        bin_index = int((angle - self.start_angle) / self.bin_width)
        
        if bin_index < 0:
            return 0
        if bin_index >= self.bins:
            return self.bins-1
        
        return bin_index
    def _bin2angle(self,bin_index):
        return (bin_index+0.5)*self.bin_width + self.start_angle
    
    def _move_settle_read(self, angle, previous_angle):
        self.move(angle)
        settle = self.delay + self.servo_base_delay + abs(angle - previous_angle) * self.servo_per_degree_delay
        if settle > 0:
            time.sleep(settle)
        d = self.read()
        if self.post_read_delay > 0:
            time.sleep(self.post_read_delay)
        return d
    
    # Initialization of bins to create baseline, returns bins
    def initialize(self, sweeps=3):
        bins = [[] for _ in range(self.bins)]
        for x in range(sweeps):
            angle = self.start_angle
            previous_angle = self.start_angle
            # Forward Sweep
            while angle <= self.end_angle:
                d = self._move_settle_read(angle, previous_angle)
                if d is not None:
                    bins[self._angle2bin(angle)].append(d)
                previous_angle = angle
                angle += self.step
            
            # Backward Sweep
            angle = self.end_angle
            previous_angle = self.end_angle
            while angle >= self.start_angle:
                d = self._move_settle_read(angle, previous_angle)
                if d is not None:
                    bins[self._angle2bin(angle)].append(d)
                previous_angle = angle
                angle -= self.step
            
        self.make_baseline(bins)
        valid_bins = sum(1 for value in self.baseline if value is not None)
        self.last_init_valid_bins = valid_bins
        self.last_init_coverage = valid_bins / self.bins if self.bins else 0.0
        self.current_angle = self.start_angle
        if self.debug:
            print("[DEBUG] Initialization Complete!")
            print("[DEBUG] Baseline coverage:", self.last_init_valid_bins, "/", self.bins, "=", self.last_init_coverage)
            print(self.baseline)
        return bins
    
    # Get median of a bin
    def _median(self, values):
        if not values:
            return None
        values = sorted(values)
        n = len(values)
        mid_point = n // 2
        
        if n % 2 == 1:
            return values[mid_point]
        else:
            return (values[mid_point - 1] + values[mid_point]) / 2
        
    
    # Check to see if a bin is flagged against the baseline
    def _check_flag(self, sweep_bin, bin_index):
        if not sweep_bin:
            return False

        baseline_value = self.baseline[bin_index]
        if baseline_value is None:
            return False
        if baseline_value == 0:
            return False

        size = len(sweep_bin)
        error_count = 0
        for value in sweep_bin:
            error_p = abs(value - baseline_value) / baseline_value
            if error_p > self.error_margin:
                error_count += 1
        measured_ratio = error_count / size
        return measured_ratio >= self.error_ratio
            
    
    # Make and store baseline into self.baseline
    def make_baseline(self, bins):
        baseline = []
        for values in bins:
            baseline.append(self._median(values))
        self.baseline = baseline
    
    def sweep(self):
        if self.baseline is None:
            print("[!] Baseline is not initialized [!]")
            return False
        sweep_bin = []
        angle = self.current_angle
        last_bin = self._angle2bin(angle)
        
        previous_angle = angle
        while angle <= self.end_angle and angle >= self.start_angle:
            current_bin = self._angle2bin(angle)
            d = self._move_settle_read(angle, previous_angle)
            if last_bin != current_bin:
                if self._check_flag(sweep_bin, last_bin):
                    if self.debug:
                        print("[DEBUG] Flagged (during sweep)")
                        print("  Bin:", last_bin)
                        print("  Angle:", self._bin2angle(last_bin))
                        print("  Samples:", len(sweep_bin))
                        print("  Baseline:", self.baseline[last_bin])
                        print("  Values:", sweep_bin[:5], " (...)")
                    detected_angle = self._bin2angle(last_bin)
                    self.alert(detected_angle)
                    return detected_angle
                else:
                    self._adjust_baseline(last_bin, sweep_bin)
                last_bin = current_bin
                sweep_bin = []
                    
            if d is not None:
                sweep_bin.append(d)
            previous_angle = angle
            angle += self.step * self.direction
            self.current_angle = angle
            
        if self.direction == 1:
            self.current_angle = self.end_angle
        if self.direction == -1:
            self.current_angle = self.start_angle
        
        if self._check_flag(sweep_bin, last_bin):
            if self.debug:
                print("[DEBUG] Flagged (final bin)")
                print("  Bin:", last_bin)
                print("  Angle:", self._bin2angle(last_bin))
                print("  Samples:", len(sweep_bin))
                print("  Baseline:", self.baseline[last_bin])
                print("  Values:", sweep_bin)
            self.alert(self._bin2angle(last_bin))
            return True
        else:
            self._adjust_baseline(last_bin, sweep_bin)
        self.direction*=-1
        
        return False
    def _adjust_baseline(self, last_bin, sweep_bin):
        if not sweep_bin:
            return False
        if self.baseline is None:
            return False

        median_val = self._median(sweep_bin)
        if median_val is None:
            return False

        current = self.baseline[last_bin]
        if current is None:
            self.baseline[last_bin] = median_val
            return True
        if current == 0:
            return False

        final_baseline = current * 0.99 + median_val * 0.01
        self.baseline[last_bin] = final_baseline
        return True