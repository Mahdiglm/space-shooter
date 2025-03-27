import pygame
import math
from collections import defaultdict
from game_logger import log_debug, log_performance

class CollisionSystem:
    """
    Optimized collision detection system using spatial partitioning
    to reduce the number of collision checks.
    """
    def __init__(self, screen_width, screen_height, cell_size=100, performance_monitor=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.grid_width = math.ceil(screen_width / cell_size)
        self.grid_height = math.ceil(screen_height / cell_size)
        
        # Spatial partitioning grid
        self.grid = defaultdict(list)
        
        # Performance monitoring
        self.performance_monitor = performance_monitor
        self.last_update_time = 0
        self.collision_count = 0
        self.check_count = 0
        self.update_count = 0
        
        # Collision pair tracking to avoid duplicate checks
        self.checked_pairs = set()
        
        # Optimizations
        self.cached_cells = {}  # Cache grid cells for objects
        self.static_objects = set()  # Objects that don't move frequently
        
        # Debug flags
        self.debug_mode = False
        self.debug_surface = None
        
        # Frame skipping for less important collision groups
        self.frame_counter = 0
        self.low_priority_interval = 2  # Check every 2 frames
        
        log_debug(f"CollisionSystem initialized with grid {self.grid_width}x{self.grid_height}, cell size {cell_size}")

    def clear(self):
        """Clear the spatial grid for a new frame."""
        self.grid.clear()
        self.checked_pairs.clear()
        self.frame_counter += 1
        
    def _get_cell_coords(self, rect):
        """Get the grid cells that an object occupies."""
        # Use cached cell coordinates if available
        obj_id = id(rect)
        if obj_id in self.cached_cells:
            prev_rect, cells = self.cached_cells[obj_id]
            # Only recalculate if the rect has moved significantly
            if (abs(rect.x - prev_rect.x) < 5 and 
                abs(rect.y - prev_rect.y) < 5 and
                rect.width == prev_rect.width and
                rect.height == prev_rect.height):
                return cells
        
        # Calculate the grid cells the object occupies
        min_x = max(0, rect.left // self.cell_size)
        max_x = min(self.grid_width - 1, rect.right // self.cell_size)
        min_y = max(0, rect.top // self.cell_size)
        max_y = min(self.grid_height - 1, rect.bottom // self.cell_size)
        
        cells = [(x, y) for x in range(min_x, max_x + 1) 
                         for y in range(min_y, max_y + 1)]
        
        # Cache the result
        self.cached_cells[obj_id] = (rect.copy(), cells)
        
        return cells

    def add_object(self, obj, group):
        """Add an object to the spatial grid."""
        if not hasattr(obj, 'rect') or not obj.rect:
            return
            
        # Skip static objects every few frames if they were added before
        if obj in self.static_objects and self.frame_counter % 3 != 0:
            return
            
        # Get the grid cells this object occupies
        cells = self._get_cell_coords(obj.rect)
        
        # Add to all relevant cells
        for cell in cells:
            self.grid[cell].append((obj, group))

    def register_static_object(self, obj):
        """Register an object as static (doesn't move often)."""
        self.static_objects.add(obj)

    def check_collisions(self, group1, group2, callback, use_distance=False, priority="high"):
        """
        Check for collisions between two groups and call the callback for each collision.
        
        Args:
            group1: First collision group
            group2: Second collision group
            callback: Function to call when collision occurs
            use_distance: Use distance-based collision instead of rect
            priority: "high" for every frame, "medium" for every other frame, "low" for less frequent
        """
        if self.performance_monitor:
            self.performance_monitor.start_section("collision")
            
        # Skip lower priority checks based on frame counter
        if (priority == "medium" and self.frame_counter % 2 != 0) or \
           (priority == "low" and self.frame_counter % self.low_priority_interval != 0):
            if self.performance_monitor:
                self.performance_monitor.end_section("collision")
            return
        
        active_cells = set()
        group1_objects = {}
        
        # Find active cells for the first group
        for obj in group1:
            if not hasattr(obj, 'rect') or not obj.rect:
                continue
                
            cells = self._get_cell_coords(obj.rect)
            for cell in cells:
                active_cells.add(cell)
                if cell not in group1_objects:
                    group1_objects[cell] = []
                group1_objects[cell].append(obj)
        
        collisions_found = 0
        checks_performed = 0
        
        # For each active cell, check collisions
        for cell in active_cells:
            # Objects from group1 in this cell
            if cell not in group1_objects:
                continue
                
            objects1 = group1_objects[cell]
            
            # Get potential collision candidates from group2 in this cell
            objects2 = [obj for obj, grp in self.grid[cell] if grp == group2]
            
            # Check for collisions
            for obj1 in objects1:
                for obj2 in objects2:
                    # Skip if already checked this pair
                    if id(obj1) > id(obj2):  # Ensure consistent ordering
                        pair = (id(obj2), id(obj1))
                    else:
                        pair = (id(obj1), id(obj2))
                        
                    if pair in self.checked_pairs:
                        continue
                        
                    self.checked_pairs.add(pair)
                    checks_performed += 1
                    
                    # Perform collision detection
                    collision = False
                    if use_distance:
                        # Circular collision detection
                        if hasattr(obj1, 'radius') and hasattr(obj2, 'radius'):
                            dx = obj1.rect.centerx - obj2.rect.centerx
                            dy = obj1.rect.centery - obj2.rect.centery
                            distance = math.sqrt(dx*dx + dy*dy)
                            collision = distance < (obj1.radius + obj2.radius)
                        else:
                            # Fallback to rect collision
                            collision = obj1.rect.colliderect(obj2.rect)
                    else:
                        # Rectangle collision detection
                        collision = obj1.rect.colliderect(obj2.rect)
                    
                    if collision:
                        collisions_found += 1
                        callback(obj1, obj2)
        
        # Track performance metrics
        self.collision_count += collisions_found
        self.check_count += checks_performed
        self.update_count += 1
        
        # Log performance every 300 updates
        if self.update_count >= 300:
            avg_checks = self.check_count / self.update_count
            avg_collisions = self.collision_count / self.update_count
            log_performance("Collision checks/frame", avg_checks)
            log_performance("Collisions/frame", avg_collisions)
            log_performance("Collision efficiency", 
                           0 if avg_checks == 0 else avg_collisions / avg_checks)
            
            # Reset counters
            self.collision_count = 0
            self.check_count = 0
            self.update_count = 0
            
        if self.performance_monitor:
            self.performance_monitor.end_section("collision")

    def draw_debug(self, surface):
        """Draw the spatial grid for debugging."""
        if not self.debug_mode:
            return
            
        # Create debug surface if not exists
        if not self.debug_surface:
            self.debug_surface = pygame.Surface((surface.get_width(), surface.get_height()), 
                                              pygame.SRCALPHA)
        
        # Clear the debug surface
        self.debug_surface.fill((0, 0, 0, 0))
        
        # Draw grid
        for x in range(0, self.screen_width, self.cell_size):
            pygame.draw.line(self.debug_surface, (50, 50, 50, 100), 
                            (x, 0), (x, self.screen_height))
                            
        for y in range(0, self.screen_height, self.cell_size):
            pygame.draw.line(self.debug_surface, (50, 50, 50, 100), 
                            (0, y), (self.screen_width, y))
        
        # Draw active cells
        for cell, objects in self.grid.items():
            cell_x, cell_y = cell
            rect = pygame.Rect(cell_x * self.cell_size, cell_y * self.cell_size, 
                              self.cell_size, self.cell_size)
            
            # Color intensity based on number of objects
            intensity = min(255, 40 + 20 * len(objects))
            pygame.draw.rect(self.debug_surface, (0, intensity, 0, 100), rect)
            
            # Draw cell coordinates
            font = pygame.font.Font(None, 20)
            text = font.render(f"{cell_x},{cell_y}", True, (200, 200, 200))
            self.debug_surface.blit(text, (cell_x * self.cell_size + 5, cell_y * self.cell_size + 5))
        
        # Blit debug surface
        surface.blit(self.debug_surface, (0, 0))
        
    def toggle_debug(self):
        """Toggle debug visualization."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode
        
    def cleanup_cached_data(self):
        """Clean up cached data for objects that no longer exist."""
        # Periodically clean up cached cells for objects that might be gone
        if self.frame_counter % 100 == 0:
            # Find objects that still exist to avoid clearing their cache
            active_objects = set()
            for cell, objects in self.grid.items():
                for obj, _ in objects:
                    active_objects.add(id(obj))
            
            # Remove cached data for objects that don't exist anymore
            to_remove = [obj_id for obj_id in self.cached_cells if obj_id not in active_objects]
            for obj_id in to_remove:
                del self.cached_cells[obj_id]
                
    def optimize_partitioning(self):
        """Optimize the grid cell size based on object distribution."""
        # Called periodically to adjust the cell size for optimal performance
        if self.update_count >= 1000:
            total_objects = sum(len(objects) for objects in self.grid.values())
            cells_used = len(self.grid)
            
            if cells_used == 0 or total_objects == 0:
                return
                
            avg_objects_per_cell = total_objects / cells_used
            
            # If cells are too crowded or too empty, adjust cell size
            if avg_objects_per_cell > 10:
                # Cells too crowded, make them smaller
                self.cell_size = max(50, self.cell_size - 10)
                self.grid_width = math.ceil(self.screen_width / self.cell_size)
                self.grid_height = math.ceil(self.screen_height / self.cell_size)
                self.cached_cells.clear()  # Clear cache as cell coordinates will change
                log_debug(f"Decreased cell size to {self.cell_size} for better collision performance")
            elif avg_objects_per_cell < 2 and self.cell_size < 200:
                # Cells too empty, make them larger
                self.cell_size = min(200, self.cell_size + 10)
                self.grid_width = math.ceil(self.screen_width / self.cell_size)
                self.grid_height = math.ceil(self.screen_height / self.cell_size)
                self.cached_cells.clear()
                log_debug(f"Increased cell size to {self.cell_size} for better collision performance") 