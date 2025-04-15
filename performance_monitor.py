import time
import pygame
import sys
import psutil
import os
from collections import deque
from game_logger import log_performance, log_debug, log_info, log_warning

class PerformanceMonitor:
    """
    Monitors and analyzes game performance metrics.
    Provides real-time FPS reporting to terminal and on-screen display.
    Also tracks memory usage to identify potential memory leaks.
    """
    def __init__(self, sample_size=60, memory_sample_size=120):
        # Initialize timing metrics with efficient data structure
        self.metrics = {
            "frame": deque(maxlen=sample_size),
            "update": deque(maxlen=sample_size),
            "render": deque(maxlen=sample_size),
            "collision": deque(maxlen=sample_size),
            "ai": deque(maxlen=sample_size),
            "input": deque(maxlen=sample_size),
            "loading": deque(maxlen=sample_size)  # Add loading metric
        }
        
        # Initialize memory metrics
        self.memory_metrics = {
            "rss": deque(maxlen=memory_sample_size),      # Resident Set Size
            "vms": deque(maxlen=memory_sample_size),      # Virtual Memory Size
            "percent": deque(maxlen=memory_sample_size),  # Memory usage as percentage
            "allocated": deque(maxlen=memory_sample_size) # Allocated objects (for leak detection)
        }
        
        # Memory monitoring info
        self.process = psutil.Process(os.getpid())
        self.memory_sample_interval = 1.0  # Sample memory every second
        self.last_memory_sample_time = time.time()
        self.memory_warning_threshold = 500  # MB
        self.memory_critical_threshold = 1000  # MB
        self.memory_leak_detection_enabled = True
        self.memory_leak_threshold = 0.05  # 5% increase over time indicates potential leak
        
        # Memory leak detection variables
        self.memory_baseline = None
        self.memory_samples_for_leak_detection = 10  # Number of samples to consider for leak detection
        self.consecutive_increases = 0
        self.leak_detected = False
        self.last_leak_warning_time = 0
        self.leak_warning_interval = 30.0  # Only warn about leaks every 30 seconds
        
        # Current frame timing data
        self.current_frame = {}
        
        # Overall frame timing
        self.frame_start_time = 0
        self.last_fps_update = 0
        self.fps = 0
        self.frame_count = 0
        
        # Performance warnings
        self.warnings = []
        self.warning_threshold = 1.0/30.0  # 33ms (30fps)
        
        # Reporting intervals
        self.report_interval = 5.0  # Detailed report interval
        self.fps_report_interval = 1.0  # FPS report interval
        self.last_report_time = time.time()
        self.last_fps_report_time = time.time()
        
        # Performance statistics
        self.min_fps = float('inf')
        self.max_fps = 0
        self.avg_fps_samples = deque(maxlen=10)  # Last 10 seconds
        
        # Font for on-screen display (preload to improve performance)
        self.font = pygame.font.Font(None, 20)
        self.fps_text_cache = {}  # Cache rendered text surfaces
        
        # Initialize flags
        self.monitoring_enabled = True
        self.display_enabled = False
        self.terminal_reporting_enabled = True
        self.memory_display_enabled = True
        
        # Performance bottleneck detection
        self.bottleneck_threshold = 0.5  # 50% of frame time
        self.identified_bottlenecks = []
        
        # Precompute common text surfaces
        self._precompute_common_text()
        
        # Initialize memory tracking
        self._sample_memory()
        self.memory_baseline = self._get_current_memory_mb("rss")
        log_info(f"Initial memory usage: {self.memory_baseline:.2f} MB")

    def _precompute_common_text(self):
        """Precompute common text surfaces to improve rendering performance."""
        self.section_labels = {}
        for section in ["frame", "update", "render", "collision"]:
            self.section_labels[section] = self.font.render(f"{section.capitalize()}: ", True, (255, 255, 255))
        
        # Precompute FPS text for common values
        for fps in range(10, 121, 5):  # 10, 15, ..., 120 FPS
            self.fps_text_cache[fps] = self.font.render(f"FPS: {fps}", True, (255, 255, 0))
            
        # Add memory labels
        self.section_labels["memory"] = self.font.render("Memory: ", True, (255, 255, 255))

    def start_frame(self):
        """Start timing a new frame."""
        if not self.monitoring_enabled:
            return
            
        self.frame_start_time = time.time()
        self.current_frame = {}

    def start_section(self, section):
        """Start timing a specific section of the frame processing."""
        if not self.monitoring_enabled:
            return
            
        self.current_frame[f"{section}_start"] = time.time()

    def end_section(self, section):
        """End timing a specific section and record the duration."""
        if not self.monitoring_enabled or f"{section}_start" not in self.current_frame:
            return
            
        duration = time.time() - self.current_frame[f"{section}_start"]
        self.metrics[section].append(duration)
        
        # Check for performance warnings
        if duration > self.warning_threshold:
            self.warnings.append(f"{section.capitalize()} taking too long: {duration*1000:.1f}ms")
            log_debug(f"Performance warning: {section} took {duration*1000:.1f}ms")

    def end_frame(self):
        """End timing the current frame and calculate FPS."""
        if not self.monitoring_enabled:
            return
            
        # Calculate frame duration
        frame_time = time.time() - self.frame_start_time
        self.metrics["frame"].append(frame_time)
        
        # Update FPS calculation
        self.frame_count += 1
        current_time = time.time()
        time_diff = current_time - self.last_fps_update
        
        if time_diff >= 0.5:  # Update FPS every half second
            self.fps = self.frame_count / time_diff
            self.frame_count = 0
            self.last_fps_update = current_time
            
            # Track min/max FPS
            self.min_fps = min(self.min_fps, self.fps)
            self.max_fps = max(self.max_fps, self.fps)
            self.avg_fps_samples.append(self.fps)
        
        # Sample memory usage at regular intervals
        if current_time - self.last_memory_sample_time >= self.memory_sample_interval:
            self._sample_memory()
            self.last_memory_sample_time = current_time
            
            # Check for memory leaks if enabled
            if self.memory_leak_detection_enabled:
                self._check_for_memory_leaks()
        
        # Report FPS to terminal every second
        if self.terminal_reporting_enabled and current_time - self.last_fps_report_time >= self.fps_report_interval:
            self._report_fps_to_terminal()
            self.last_fps_report_time = current_time
        
        # Generate detailed performance report periodically
        if current_time - self.last_report_time >= self.report_interval:
            self._generate_report()
            self.last_report_time = current_time
            
        # Clear warnings after each frame
        self.warnings = []
        
        # Detect bottlenecks
        self._detect_bottlenecks(frame_time)

    def _sample_memory(self):
        """Sample current memory usage and store in metrics."""
        try:
            # Force a garbage collection to get more accurate memory usage
            import gc
            gc.collect()
            
            # Update memory info
            mem_info = self.process.memory_info()
            
            # Store memory info in MB
            rss_mb = mem_info.rss / (1024 * 1024)
            vms_mb = mem_info.vms / (1024 * 1024)
            
            # Store in metrics
            self.memory_metrics["rss"].append(rss_mb)
            self.memory_metrics["vms"].append(vms_mb)
            self.memory_metrics["percent"].append(self.process.memory_percent())
            
            # Check for memory warnings
            if rss_mb > self.memory_critical_threshold:
                log_warning(f"CRITICAL: Memory usage too high: {rss_mb:.2f} MB")
                self.warnings.append(f"CRITICAL: Memory usage: {rss_mb:.2f} MB")
            elif rss_mb > self.memory_warning_threshold:
                log_warning(f"WARNING: Memory usage high: {rss_mb:.2f} MB")
                self.warnings.append(f"Warning: Memory usage: {rss_mb:.2f} MB")
                
            # Track object allocations for leak detection
            self.memory_metrics["allocated"].append(len(gc.get_objects()))
            
            return rss_mb
        except Exception as e:
            log_warning(f"Error sampling memory: {e}")
            return 0

    def _check_for_memory_leaks(self):
        """Check if memory usage is consistently increasing (potential leak)."""
        if len(self.memory_metrics["rss"]) < self.memory_samples_for_leak_detection:
            return  # Not enough samples yet
        
        # Get a slice of recent samples
        recent_samples = list(self.memory_metrics["rss"])[-self.memory_samples_for_leak_detection:]
        
        # Check if memory is consistently increasing
        is_increasing = all(recent_samples[i] <= recent_samples[i+1] for i in range(len(recent_samples)-1))
        
        # Calculate growth percentage
        if len(recent_samples) >= 2:
            growth_percent = (recent_samples[-1] - recent_samples[0]) / recent_samples[0]
        else:
            growth_percent = 0
        
        # Check if growth exceeds our threshold (indicating a potential leak)
        if is_increasing and growth_percent > self.memory_leak_threshold:
            self.consecutive_increases += 1
            
            # Only consider it a leak after several consecutive increases
            if self.consecutive_increases >= 3 and not self.leak_detected:
                self.leak_detected = True
                current_time = time.time()
                
                # Don't spam warnings about the same leak
                if current_time - self.last_leak_warning_time > self.leak_warning_interval:
                    log_warning(f"Potential memory leak detected! Memory increased by {growth_percent*100:.2f}% over last {self.memory_samples_for_leak_detection} samples")
                    self.warnings.append("Potential memory leak detected!")
                    self.last_leak_warning_time = current_time
        else:
            # Reset consecutive counter if not increasing
            self.consecutive_increases = 0
            if self.leak_detected and len(recent_samples) >= 2 and recent_samples[-1] < recent_samples[-2]:
                self.leak_detected = False  # Consider the leak resolved if memory decreases

    def _get_current_memory_mb(self, metric="rss"):
        """Get the current memory usage in MB for the specified metric."""
        if not self.memory_metrics[metric]:
            return 0
        return self.memory_metrics[metric][-1]

    def _report_fps_to_terminal(self):
        """Report current FPS and memory usage to terminal."""
        avg_fps = sum(self.avg_fps_samples) / len(self.avg_fps_samples) if self.avg_fps_samples else self.fps
        
        # Color coding based on FPS
        if self.fps >= 55:
            color = '\033[92m'  # Green
        elif self.fps >= 30:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
        
        reset = '\033[0m'
        
        # Report FPS to terminal with color
        print(f"FPS: {color}{self.fps:.1f}{reset} (Avg: {avg_fps:.1f}, Min: {self.min_fps:.1f}, Max: {self.max_fps:.1f})")
        
        # Report memory usage
        mem_rss = self._get_current_memory_mb("rss")
        mem_color = '\033[92m'  # Green by default
        
        if mem_rss > self.memory_critical_threshold:
            mem_color = '\033[91m'  # Red
        elif mem_rss > self.memory_warning_threshold:
            mem_color = '\033[93m'  # Yellow
            
        print(f"Memory: {mem_color}{mem_rss:.1f} MB{reset}")
        
        # Log to file as well
        log_info(f"FPS: {self.fps:.1f} (Avg: {avg_fps:.1f}, Min: {self.min_fps:.1f}, Max: {self.max_fps:.1f})")
        log_info(f"Memory: {mem_rss:.1f} MB")
        
        # Print identified bottlenecks if any
        if self.identified_bottlenecks:
            bottleneck_str = ", ".join(self.identified_bottlenecks)
            print(f"Bottlenecks: {bottleneck_str}")
            self.identified_bottlenecks = []  # Reset after reporting

    def _detect_bottlenecks(self, frame_time):
        """Detect performance bottlenecks in the game."""
        if frame_time <= 0:
            return
            
        self.identified_bottlenecks = []
        
        # Check each section for potential bottlenecks
        for section in ["update", "render", "collision", "ai", "input"]:
            if not self.metrics[section]:
                continue
                
            avg_time = sum(self.metrics[section]) / len(self.metrics[section])
            percentage = avg_time / frame_time
            
            if percentage > self.bottleneck_threshold:
                self.identified_bottlenecks.append(f"{section} ({percentage*100:.0f}%)")

    def _generate_report(self):
        """Generate a performance report with averages."""
        if not self.monitoring_enabled or not self.metrics["frame"]:
            return
            
        # Calculate averages
        avg_frame = sum(self.metrics["frame"]) / len(self.metrics["frame"])
        avg_fps = 1.0 / avg_frame if avg_frame > 0 else 0
        
        # Log performance data
        log_performance("FPS", avg_fps)
        log_performance("Frame Time", avg_frame)
        
        # Log memory usage
        if self.memory_metrics["rss"]:
            current_mem = self.memory_metrics["rss"][-1]
            avg_mem = sum(self.memory_metrics["rss"]) / len(self.memory_metrics["rss"])
            initial_mem = self.memory_baseline if self.memory_baseline is not None else 0
            
            log_performance("Memory (MB)", current_mem)
            log_performance("Avg Memory (MB)", avg_mem)
            
            # Calculate memory growth
            if initial_mem > 0:
                growth = (current_mem - initial_mem) / initial_mem * 100
                log_performance("Memory Growth (%)", growth)
        
        # Log individual section times if they have data
        for section in ["update", "render", "collision", "ai", "input"]:
            if not self.metrics[section]:
                continue
                
            avg_time = sum(self.metrics[section]) / len(self.metrics[section])
            log_performance(f"{section.capitalize()} Time", avg_time)
            
            # Calculate percentage of frame time
            if avg_frame > 0:
                percent = avg_time / avg_frame * 100
                log_performance(f"{section.capitalize()} %", percent)

    def draw(self, surface):
        """Draw performance metrics on screen."""
        if not self.display_enabled:
            return None
            
        # Background for readability
        metrics_height = 135
        if self.memory_display_enabled:
            metrics_height += 60  # Add space for memory display
            
        metrics_bg = pygame.Rect(5, 5, 200, metrics_height)
        pygame.draw.rect(surface, (0, 0, 0, 128), metrics_bg)
        pygame.draw.rect(surface, (255, 255, 255), metrics_bg, 1)
        
        # FPS counter - use cached text if available
        rounded_fps = round(self.fps / 5) * 5  # Round to nearest 5
        if rounded_fps in self.fps_text_cache:
            fps_text_surface = self.fps_text_cache[rounded_fps]
        else:
            # Dynamic color based on FPS
            if self.fps >= 55:
                color = (100, 255, 100)  # Green
            elif self.fps >= 30:
                color = (255, 255, 100)  # Yellow
            else:
                color = (255, 100, 100)  # Red
                
            fps_text_surface = self.font.render(f"FPS: {self.fps:.1f}", True, color)
            
        surface.blit(fps_text_surface, (10, 10))
        
        # Section timing data
        y = 30
        for section in ["frame", "update", "render", "collision"]:
            if self.metrics[section]:
                avg = sum(self.metrics[section]) / len(self.metrics[section])
                
                # Use precomputed label
                surface.blit(self.section_labels[section], (10, y))
                
                # Render value dynamically
                value_text = self.font.render(f"{avg*1000:.1f}ms", True, (255, 255, 255))
                surface.blit(value_text, (80, y))
                y += 20
                
        # Display performance stats
        if self.avg_fps_samples:
            avg_fps = sum(self.avg_fps_samples) / len(self.avg_fps_samples)
            stats_text = self.font.render(f"Min/Avg/Max: {self.min_fps:.0f}/{avg_fps:.0f}/{self.max_fps:.0f}", True, (200, 200, 200))
            surface.blit(stats_text, (10, y))
            y += 20
        
        # Memory usage display
        if self.memory_display_enabled:
            # Add a small separator line
            pygame.draw.line(surface, (150, 150, 150), (10, y), (190, y), 1)
            y += 10
            
            # Display current memory usage
            mem_rss = self._get_current_memory_mb("rss")
            
            # Choose color based on memory usage
            if mem_rss > self.memory_critical_threshold:
                mem_color = (255, 0, 0)  # Red
            elif mem_rss > self.memory_warning_threshold:
                mem_color = (255, 255, 0)  # Yellow
            else:
                mem_color = (0, 255, 0)  # Green
                
            surface.blit(self.section_labels["memory"], (10, y))
            mem_text = self.font.render(f"{mem_rss:.1f} MB", True, mem_color)
            surface.blit(mem_text, (80, y))
            y += 20
            
            # Show memory change from baseline
            if self.memory_baseline is not None:
                change = mem_rss - self.memory_baseline
                change_pct = (change / self.memory_baseline * 100) if self.memory_baseline > 0 else 0
                
                # Color based on change percentage
                if change_pct > 50:
                    change_color = (255, 0, 0)  # Red
                elif change_pct > 20:
                    change_color = (255, 255, 0)  # Yellow
                else:
                    change_color = (200, 200, 200)  # Gray
                
                change_prefix = "+" if change >= 0 else ""
                change_text = self.font.render(f"Change: {change_prefix}{change:.1f} MB ({change_prefix}{change_pct:.1f}%)", 
                                               True, change_color)
                surface.blit(change_text, (10, y))
                y += 20
            
            # Display leak warning if detected
            if self.leak_detected:
                leak_text = self.font.render("Memory leak detected!", True, (255, 0, 0))
                surface.blit(leak_text, (10, y))
                y += 20
                
    def toggle_display(self):
        """Toggle display of performance metrics."""
        self.display_enabled = not self.display_enabled
        return self.display_enabled
        
    def toggle_terminal_reporting(self):
        """Toggle terminal reporting of performance metrics."""
        self.terminal_reporting_enabled = not self.terminal_reporting_enabled
        return self.terminal_reporting_enabled
        
    def toggle_memory_display(self):
        """Toggle display of memory metrics."""
        self.memory_display_enabled = not self.memory_display_enabled
        return self.memory_display_enabled
        
    def enable_monitoring(self, enabled=True):
        """Enable or disable performance monitoring."""
        self.monitoring_enabled = enabled
        return self.monitoring_enabled
        
    def get_fps(self):
        """Get the current FPS."""
        return self.fps
        
    def get_performance_summary(self):
        """Get a summary of performance metrics."""
        summary = {
            "fps": self.fps,
            "avg_fps": sum(self.avg_fps_samples) / len(self.avg_fps_samples) if self.avg_fps_samples else 0,
            "min_fps": self.min_fps,
            "max_fps": self.max_fps,
            "memory_mb": self._get_current_memory_mb("rss"),
            "memory_baseline_mb": self.memory_baseline,
            "memory_growth_percent": ((self._get_current_memory_mb("rss") - self.memory_baseline) / self.memory_baseline * 100) 
                                     if self.memory_baseline and self.memory_baseline > 0 else 0,
            "leak_detected": self.leak_detected
        }
        
        return summary
        
    def reset_memory_baseline(self):
        """Reset the memory baseline to current usage. Useful after loading is complete."""
        self._sample_memory()
        self.memory_baseline = self._get_current_memory_mb("rss")
        self.leak_detected = False
        self.consecutive_increases = 0
        log_info(f"Memory baseline reset to {self.memory_baseline:.2f} MB")
        return self.memory_baseline 