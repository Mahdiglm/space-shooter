import time
import pygame
from collections import deque
from game_logger import log_performance, log_debug

class PerformanceMonitor:
    """
    Monitors and analyzes game performance metrics.
    """
    def __init__(self, sample_size=60):
        # Initialize timing metrics
        self.metrics = {
            "frame": deque(maxlen=sample_size),
            "update": deque(maxlen=sample_size),
            "render": deque(maxlen=sample_size),
            "collision": deque(maxlen=sample_size),
            "ai": deque(maxlen=sample_size),
            "input": deque(maxlen=sample_size)
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
        
        # Reporting interval (in seconds)
        self.report_interval = 5.0
        self.last_report_time = time.time()
        
        # Font for on-screen display
        self.font = pygame.font.Font(None, 20)
        
        # Initialize flags
        self.monitoring_enabled = True
        self.display_enabled = False

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
        
        # Generate performance report periodically
        if current_time - self.last_report_time >= self.report_interval:
            self._generate_report()
            self.last_report_time = current_time
            
        # Clear warnings after each frame
        self.warnings = []

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
            return
            
        # Background for readability
        metrics_bg = pygame.Rect(5, 5, 200, 115)
        pygame.draw.rect(surface, (0, 0, 0, 128), metrics_bg)
        pygame.draw.rect(surface, (255, 255, 255), metrics_bg, 1)
        
        # FPS counter
        fps_text = self.font.render(f"FPS: {self.fps:.1f}", True, (255, 255, 0))
        surface.blit(fps_text, (10, 10))
        
        # Section timing data
        y = 30
        for section in ["frame", "update", "render", "collision"]:
            if self.metrics[section]:
                avg = sum(self.metrics[section]) / len(self.metrics[section])
                text = self.font.render(f"{section.capitalize()}: {avg*1000:.1f}ms", True, (255, 255, 255))
                surface.blit(text, (10, y))
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

    def enable_monitoring(self, enabled=True):
        """Enable or disable performance monitoring."""
        self.monitoring_enabled = enabled
        
    def get_fps(self):
        """Get the current FPS value."""
        return self.fps 