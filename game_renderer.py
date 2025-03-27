import pygame
import time
from pygame.locals import *
from game_logger import log_info, log_performance, log_debug

class GameRenderer:
    """
    Handles efficient rendering of game elements using dirty rectangle technique
    with optimizations for improved performance.
    """
    def __init__(self, screen_width, screen_height, background_color=(0, 0, 0), performance_monitor=None):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.background_color = background_color
        self.dirty_rects = []
        self.background = None
        self.performance_monitor = performance_monitor
        
        # Rendering cache for frequently used images
        self.image_cache = {}
        
        # Sprite groups for better organization and culling
        self.all_sprites = pygame.sprite.Group()
        self.visible_sprites = pygame.sprite.Group()
        
        # Performance optimization flags
        self.last_update_time = time.time()
        self.report_interval = 5.0  # seconds
        self.total_render_time = 0
        self.render_count = 0
        self.rect_count = 0
        
        # Batching optimization
        self.max_batch_size = 100
        self.allow_skipping = True
        self.skip_threshold = 1/120  # Skip if behind by 8.33ms (120fps target)
        
        # Surface caching
        self.text_surfaces = {}
        self.effect_surfaces = {}
        
        # Debug flags
        self.show_dirty_rects = False
        self.show_performance = False
        
        # Last full redraw time
        self.last_full_redraw = 0
        self.force_full_redraw_interval = 10.0  # Increase to 10 seconds to reduce blinking
        self.last_frame_count = 0  # Track last frame count for smoother redraw timing
        
        # Initialize background buffer
        self.background_buffer = pygame.Surface((screen_width, screen_height))
        self.background_buffer.fill(background_color)
        
        log_info("GameRenderer initialized with resolution {}x{}".format(screen_width, screen_height))

    def set_background_image(self, surface):
        """Set the background directly from an already loaded surface."""
        if surface:
            self.background = surface
            # Update background buffer with provided surface
            self.background_buffer.blit(self.background, (0, 0))
            
            # Force a full redraw when background changes
            self.force_full_redraw()
            return True
        return False
        
    def add_to_cache(self, key, image):
        """Add an image to the rendering cache."""
        if image and key not in self.image_cache:
            self.image_cache[key] = image
            return True
        return False

    def set_background(self, image_path=None):
        """Set the background image or color."""
        if image_path:
            try:
                # Cache the background to avoid reloading
                if image_path in self.image_cache:
                    self.background = self.image_cache[image_path]
                else:
                    self.background = pygame.image.load(image_path).convert()
                    self.background = pygame.transform.scale(self.background, 
                                                           (self.screen_width, self.screen_height))
                    self.image_cache[image_path] = self.background
                
                # Update background buffer
                self.background_buffer.blit(self.background, (0, 0))
            except Exception as e:
                log_debug(f"Failed to load background: {e}")
                self.background = None
                self.background_buffer.fill(self.background_color)
        else:
            self.background = None
            self.background_buffer.fill(self.background_color)
            
        # Force a full redraw when background changes
        self.force_full_redraw()

    def clear_previous(self, sprites):
        """Clear previous sprite positions by restoring background."""
        for sprite in sprites:
            if hasattr(sprite, 'prev_rect') and sprite.prev_rect:
                # Only add to dirty rects if actually different (optimization)
                if sprite.prev_rect.width > 0 and sprite.prev_rect.height > 0:
                    # Add a small padding to ensure complete clearing
                    padded_rect = sprite.prev_rect.inflate(4, 4)
                    # Copy from background buffer to screen
                    self.screen.blit(self.background_buffer, padded_rect, padded_rect)
                    self.dirty_rects.append(padded_rect)

    def draw_sprites(self, sprites):
        """Draw sprites efficiently using dirty rectangle technique."""
        # Performance monitoring
        if self.performance_monitor:
            self.performance_monitor.start_section("render")
            
        start_time = time.time()
        
        # Check if we need a full redraw - use time-based or distance-based checks
        current_time = time.time()
        force_full = (current_time - self.last_full_redraw) > self.force_full_redraw_interval
        
        # Only do frame-based redraw check if we haven't done a time-based full redraw recently
        # This prevents double-redraw blinking effect
        frame_based_redraw = False
        if self.performance_monitor and not force_full:
            # Only do a frame-based redraw every 300 frames (about 5 seconds at 60fps)
            # And make sure at least 2 seconds have passed since last full redraw
            current_frame = self.performance_monitor.frame_count
            frames_passed = current_frame - self.last_frame_count
            time_since_last = current_time - self.last_full_redraw
            
            if frames_passed >= 300 and time_since_last >= 2.0:
                frame_based_redraw = True
                self.last_frame_count = current_frame
                log_debug("Frame-based full redraw")
        
        # Force full redraw when needed, less frequently to prevent blinking
        if force_full or frame_based_redraw:
            # Complete redraw - blit background and update all
            self.screen.blit(self.background_buffer, (0, 0))
            self.dirty_rects = [pygame.Rect(0, 0, self.screen_width, self.screen_height)]
            self.last_full_redraw = current_time
            if force_full:
                log_debug("Time-based full screen redraw")
        else:
            # Partial redraw - just update dirty areas
            self.clear_previous(sprites)
        
        # Cull sprites outside viewport (optimization)
        visible_sprites = []
        screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        
        # Batch processing of sprites for better performance
        batch_counter = 0
        batch_limit = min(len(sprites), self.max_batch_size)
        
        for sprite in sprites:
            # Skip offscreen sprites (culling)
            if not hasattr(sprite, 'rect') or not sprite.rect:
                continue
                
            # Skip if too far outside viewport
            if sprite.rect.right < -50 or sprite.rect.left > self.screen_width + 50 or \
               sprite.rect.bottom < -50 or sprite.rect.top > self.screen_height + 50:
                continue
                
            # Skip invisible sprites
            if hasattr(sprite, 'visible') and not sprite.visible:
                continue
                
            # Check if we should skip this frame for performance
            if self.allow_skipping and batch_counter > batch_limit:
                current_render_time = time.time() - start_time
                if current_render_time > self.skip_threshold:
                    log_debug(f"Skipping remaining sprites ({len(sprites) - batch_counter}) for performance")
                    break
                    
            batch_counter += 1
                
            # Store previous position for next frame's cleanup
            if not hasattr(sprite, 'prev_rect') or sprite.prev_rect is None:
                sprite.prev_rect = pygame.Rect(sprite.rect)
            else:
                sprite.prev_rect.x = sprite.rect.x
                sprite.prev_rect.y = sprite.rect.y
                sprite.prev_rect.width = sprite.rect.width
                sprite.prev_rect.height = sprite.rect.height
                
            # Only draw if visible (intersects with screen)
            if sprite.rect.colliderect(screen_rect):
                # Draw the sprite
                if hasattr(sprite, 'image') and sprite.image is not None:
                    self.screen.blit(sprite.image, sprite.rect)
                    # Add to dirty rectangles for updating - with a small padding
                    padded_rect = pygame.Rect(sprite.rect).inflate(2, 2)
                    self.dirty_rects.append(padded_rect)
                    visible_sprites.append(sprite)

        # Update only the dirty portions of the screen
        if self.dirty_rects:
            # Merge overlapping rectangles to reduce update calls
            optimized_rects = self._optimize_rects(self.dirty_rects)
            pygame.display.update(optimized_rects)
            self.rect_count += len(optimized_rects)
            
            # Visualize dirty rects if debug enabled
            if self.show_dirty_rects:
                for rect in optimized_rects:
                    pygame.draw.rect(self.screen, (255, 0, 0), rect, 1)
                pygame.display.update(optimized_rects)
                
        # Performance tracking
        end_time = time.time()
        render_time = end_time - start_time
        self.total_render_time += render_time
        self.render_count += 1
        
        # End performance monitoring
        if self.performance_monitor:
            self.performance_monitor.end_section("render")
            
        # Report metrics periodically
        current_time = time.time()
        if current_time - self.last_update_time >= self.report_interval:
            avg_render_time = self.total_render_time / max(1, self.render_count)
            avg_rects = self.rect_count / max(1, self.render_count)
            log_performance("Render time", avg_render_time)
            log_performance("Dirty rects/frame", avg_rects)
            
            # Reset counters
            self.total_render_time = 0
            self.render_count = 0
            self.rect_count = 0
            self.last_update_time = current_time
            
        # Clear dirty rects for next frame
        self.dirty_rects = []
        
        return visible_sprites

    def _optimize_rects(self, rects):
        """Optimize dirty rectangles by merging overlapping ones."""
        if not rects:
            return []
            
        if len(rects) <= 1:
            return rects
            
        # Sort rects by area for better merging
        sorted_rects = sorted(rects, key=lambda r: r.width * r.height)
        
        # If too many small rects, consider a full screen update
        if len(sorted_rects) > 20:
            total_area = sum(r.width * r.height for r in sorted_rects)
            screen_area = self.screen_width * self.screen_height
            if total_area > 0.5 * screen_area:  # If dirty area > 50% of screen
                return [pygame.Rect(0, 0, self.screen_width, self.screen_height)]
        
        # Simple implementation: merge overlapping rects
        result = []
        while sorted_rects:
            rect = sorted_rects.pop(0)
            
            # Check for intersections with existing rects
            merged = False
            for i, existing in enumerate(result):
                if rect.colliderect(existing):
                    # Merge the rects
                    result[i] = existing.union(rect)
                    merged = True
                    break
                    
            if not merged:
                result.append(rect)
                
        # Repeat until no more merges can be done (limit iterations for performance)
        if len(result) < len(rects) and len(result) > 1:
            # One more pass should be sufficient
            result = self._optimize_rects(result)
            
        return result

    def draw_text(self, text, x, y, color=(255, 255, 255), font=None, centered=False):
        """Draw text efficiently with caching."""
        if font is None:
            font = pygame.font.Font(None, 36)
            
        # Create cache key
        cache_key = f"{text}_{color}_{font.get_height()}"
        
        # Check if we have it cached
        if cache_key in self.text_surfaces:
            text_surface = self.text_surfaces[cache_key]
        else:
            text_surface = font.render(text, True, color)
            # Cache the surface
            self.text_surfaces[cache_key] = text_surface
            
            # Limit cache size
            if len(self.text_surfaces) > 100:
                # Remove oldest item (first key)
                self.text_surfaces.pop(next(iter(self.text_surfaces)))
        
        text_rect = text_surface.get_rect()
        if centered:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
            
        # Clear previous position if text changed
        if hasattr(self, f'prev_text_rect_{cache_key}') and getattr(self, f'prev_text_rect_{cache_key}'):
            prev_rect = getattr(self, f'prev_text_rect_{cache_key}')
            # Add padding to ensure complete clearing
            prev_rect_padded = prev_rect.inflate(6, 6)
            self.screen.blit(self.background_buffer, prev_rect_padded, prev_rect_padded)
            self.dirty_rects.append(prev_rect_padded)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
        # Add padding to text rect to ensure complete update
        padded_text_rect = text_rect.inflate(6, 6)
        self.dirty_rects.append(padded_text_rect)
        
        # Store rect for next frame with unique key for different text positions
        setattr(self, f'prev_text_rect_{cache_key}', text_rect.copy())
        
        return text_rect

    def force_full_redraw(self):
        """Force a complete redraw of the screen."""
        self.dirty_rects = [pygame.Rect(0, 0, self.screen_width, self.screen_height)]
        self.screen.blit(self.background_buffer, (0, 0))
        pygame.display.flip()
        self.last_full_redraw = time.time()

    def toggle_performance_display(self):
        """Toggle display of performance metrics."""
        self.show_performance = not self.show_performance
        return self.show_performance
        
    def toggle_dirty_rects_display(self):
        """Toggle display of dirty rectangles for debugging."""
        self.show_dirty_rects = not self.show_dirty_rects
        return self.show_dirty_rects
        
    def get_screen(self):
        """Get the screen surface."""
        return self.screen 