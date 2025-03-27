import pygame
import time
from game_logger import log_performance, log_debug

class GameRenderer:
    """
    Optimized renderer for the Space Shooter game.
    Implements dirty rectangle rendering to minimize GPU operations.
    """
    def __init__(self, screen, background_color=(0, 0, 0)):
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.background_color = background_color
        self.background_image = None
        
        # Initialize dirty rectangles tracking
        self.dirty_rects = []
        self.previous_sprite_rects = {}
        self.full_redraw_needed = True
        
        # Performance tracking
        self.frame_count = 0
        self.render_time = 0
        self.last_performance_log = time.time()
        
        # Create background surface for partial redraw
        self.background_surface = pygame.Surface((self.screen_rect.width, self.screen_rect.height))
        self.background_surface.fill(self.background_color)
        
        # Default font for performance metrics
        self.debug_font = pygame.font.Font(None, 24)
        self.show_metrics = False

    def set_background(self, image=None):
        """Set background image or color."""
        if image:
            self.background_image = image
            # Scale the background image to fit the screen
            self.background_image = pygame.transform.scale(
                self.background_image, 
                (self.screen_rect.width, self.screen_rect.height)
            )
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_image = None
            self.background_surface.fill(self.background_color)
        
        # Full redraw needed after background change
        self.full_redraw_needed = True

    def clear(self, sprite_groups):
        """
        Clear previous sprite positions by tracking their rectangles.
        This creates "dirty rectangles" that need to be redrawn.
        """
        # Track rectangles for all sprites
        for group in sprite_groups:
            for sprite in group:
                sprite_id = id(sprite)
                # If sprite existed in previous frame, mark its previous position as dirty
                if sprite_id in self.previous_sprite_rects:
                    prev_rect = self.previous_sprite_rects[sprite_id]
                    self.dirty_rects.append(prev_rect)
                
                # Store current position for next frame
                self.previous_sprite_rects[sprite_id] = sprite.rect.copy()

        # Remove rectangles for sprites that no longer exist
        current_sprite_ids = set()
        for group in sprite_groups:
            for sprite in group:
                current_sprite_ids.add(id(sprite))
        
        removed_sprites = set(self.previous_sprite_rects.keys()) - current_sprite_ids
        for sprite_id in removed_sprites:
            rect = self.previous_sprite_rects.pop(sprite_id)
            self.dirty_rects.append(rect)

    def draw(self, sprite_groups):
        """
        Draw sprites efficiently using dirty rectangle rendering.
        Only redraws parts of the screen that have changed.
        """
        start_time = time.time()
        
        # If full redraw is needed, do it
        if self.full_redraw_needed:
            if self.background_image:
                self.screen.blit(self.background_image, (0, 0))
            else:
                self.screen.fill(self.background_color)
            
            # Draw all sprites
            for group in sprite_groups:
                dirty_rects = group.draw(self.screen)
                self.dirty_rects.extend(dirty_rects)
            
            # Reset flag
            self.full_redraw_needed = False
        else:
            # Redraw background only in dirty areas
            for rect in self.dirty_rects:
                if self.background_image:
                    area = rect.clip(self.screen_rect)
                    self.screen.blit(self.background_surface, area, area)
                else:
                    self.screen.fill(self.background_color, rect)
            
            # Draw sprites and collect their areas as new dirty rects
            new_dirty_rects = []
            for group in sprite_groups:
                # Draw the group and collect the updated areas
                updated_rects = group.draw(self.screen)
                new_dirty_rects.extend(updated_rects)
            
            # Replace old dirty rects with new ones
            self.dirty_rects = new_dirty_rects
        
        # Update performance metrics
        render_duration = time.time() - start_time
        self.render_time += render_duration
        self.frame_count += 1
        
        # Log performance metrics every 5 seconds
        current_time = time.time()
        if current_time - self.last_performance_log >= 5.0:
            avg_render_time = self.render_time / max(1, self.frame_count)
            log_performance("Rendering", avg_render_time)
            log_debug(f"Dirty rectangles: {len(self.dirty_rects)}")
            
            # Reset metrics
            self.render_time = 0
            self.frame_count = 0
            self.last_performance_log = current_time
        
        # Draw performance metrics if enabled
        if self.show_metrics:
            self._draw_performance_metrics(render_duration)
        
        return self.dirty_rects

    def _draw_performance_metrics(self, render_time):
        """Draw performance metrics on screen for debugging."""
        metrics = [
            f"FPS: {int(1.0 / max(0.001, render_time))}",
            f"Render: {render_time * 1000:.1f}ms",
            f"Dirty: {len(self.dirty_rects)}"
        ]
        
        y = 10
        for text in metrics:
            text_surface = self.debug_font.render(text, True, (255, 255, 0))
            text_rect = text_surface.get_rect(topleft=(10, y))
            self.screen.blit(text_surface, text_rect)
            y += 25
            # Add text rectangles to dirty areas
            self.dirty_rects.append(text_rect)

    def toggle_metrics_display(self):
        """Toggle display of performance metrics."""
        self.show_metrics = not self.show_metrics
        self.full_redraw_needed = True

    def force_full_redraw(self):
        """Force a full screen redraw on next frame."""
        self.full_redraw_needed = True
        
    def update_display(self, areas=None):
        """Update only the necessary parts of the screen."""
        if areas:
            pygame.display.update(areas)
        else:
            pygame.display.flip() 