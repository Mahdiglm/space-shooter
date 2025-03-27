import time
import pygame
import sys
from collections import deque
from game_logger import log_performance, log_debug, log_info

class PerformanceMonitor:
    """
    Monitors and analyzes game performance metrics.
    Provides real-time FPS reporting to terminal and on-screen display.
    """
    def __init__(self, sample_size=60):
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
        
        # Performance bottleneck detection
        self.bottleneck_threshold = 0.5  # 50% of frame time
        self.identified_bottlenecks = []
        
        # Precompute common text surfaces
        self._precompute_common_text()

    def _precompute_common_text(self):
        """Precompute common text surfaces to improve rendering performance."""
        self.section_labels = {}
        for section in ["frame", "update", "render", "collision"]:
            self.section_labels[section] = self.font.render(f"{section.capitalize()}: ", True, (255, 255, 255))
        
        # Precompute FPS text for common values
        for fps in range(10, 121, 5):  # 10, 15, ..., 120 FPS
            self.fps_text_cache[fps] = self.font.render(f"FPS: {fps}", True, (255, 255, 0))

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

    def _report_fps_to_terminal(self):
        """Report current FPS to terminal."""
        avg_fps = sum(self.avg_fps_samples) / len(self.avg_fps_samples) if self.avg_fps_samples else self.fps
        
        # Color coding based on FPS
        if self.fps >= 55:
            color = '\033[92m'  # Green
        elif self.fps >= 30:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
        
        reset = '\033[0m'
        
        # Report to terminal with color
        print(f"FPS: {color}{self.fps:.1f}{reset} (Avg: {avg_fps:.1f}, Min: {self.min_fps:.1f}, Max: {self.max_fps:.1f})")
        
        # Log to file as well
        log_info(f"FPS: {self.fps:.1f} (Avg: {avg_fps:.1f}, Min: {self.min_fps:.1f}, Max: {self.max_fps:.1f})")
        
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
        
        # Log individual section times if they have data
        for section in ["update", "render", "collision", "ai", "input"]:
            if self.metrics[section]:
                avg = sum(self.metrics[section]) / len(self.metrics[section])
                percentage = (avg / avg_frame) * 100 if avg_frame > 0 else 0
                log_performance(f"{section.capitalize()} Time", avg)
                log_performance(f"{section.capitalize()} %", percentage)

    def draw(self, surface):
        """Draw performance metrics on screen."""
        if not self.display_enabled:
            return None
            
        # Background for readability
        metrics_bg = pygame.Rect(5, 5, 200, 135)
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
                
        # Display the most recent warning
        if self.warnings:
            warning_text = self.font.render(self.warnings[-1], True, (255, 100, 100))
            surface.blit(warning_text, (10, y))
            
        # Return the rectangle that was modified
        return metrics_bg

    def toggle_display(self):
        """Toggle the on-screen display of performance metrics."""
        self.display_enabled = not self.display_enabled
        return self.display_enabled
        
    def toggle_terminal_reporting(self):
        """Toggle FPS reporting to terminal."""
        self.terminal_reporting_enabled = not self.terminal_reporting_enabled
        return self.terminal_reporting_enabled

    def enable_monitoring(self, enabled=True):
        """Enable or disable performance monitoring."""
        self.monitoring_enabled = enabled
        
    def get_fps(self):
        """Get the current FPS value."""
        return self.fps
        
    def get_performance_summary(self):
        """Get a summary of performance metrics for diagnostics."""
        if not self.metrics["frame"]:
            return "No performance data available"
            
        avg_frame = sum(self.metrics["frame"]) / len(self.metrics["frame"])
        avg_fps = 1.0 / avg_frame if avg_frame > 0 else 0
        
        summary = []
        summary.append(f"FPS: {self.fps:.1f} (Min: {self.min_fps:.1f}, Max: {self.max_fps:.1f})")
        summary.append(f"Frame time: {avg_frame*1000:.1f}ms")
        
        for section in ["update", "render", "collision"]:
            if self.metrics[section]:
                avg = sum(self.metrics[section]) / len(self.metrics[section])
                percentage = (avg / avg_frame) * 100 if avg_frame > 0 else 0
                summary.append(f"{section}: {avg*1000:.1f}ms ({percentage:.1f}%)")
                
        return "\n".join(summary) 