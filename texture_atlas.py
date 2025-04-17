import pygame
import os
import math
from game_logger import log_info, log_warning, log_error, log_debug, log_performance

class TextureAtlas:
    """
    Combines multiple images into a single texture atlas to reduce
    texture switching during rendering, improving performance.
    """
    def __init__(self, name="atlas", padding=2):
        self.name = name
        self.padding = padding  # Padding between sprites to prevent bleeding
        self.surface = None
        self.regions = {}  # Dictionary mapping image keys to regions (rect, rotated)
        self.width = 0
        self.height = 0
        self.used_area = 0
        self.efficiency = 0.0
        
    def create_from_images(self, images_dict, max_width=2048, max_height=2048):
        """
        Create a texture atlas from a dictionary of images.
        
        Args:
            images_dict: Dictionary mapping keys to pygame Surface objects
            max_width: Maximum width of the atlas texture
            max_height: Maximum height of the atlas texture
            
        Returns:
            bool: Success or failure
        """
        if not images_dict:
            log_warning(f"No images provided for texture atlas '{self.name}'")
            return False
            
        # Calculate needed atlas size based on total area
        total_area = sum(img.get_width() * img.get_height() for img in images_dict.values())
        min_size = math.ceil(math.sqrt(total_area * 1.2))  # 20% extra for packing inefficiency
        
        # Ensure dimensions are powers of 2 for optimal GPU performance
        def next_power_of_2(x):
            return 2 ** math.ceil(math.log2(x))
        
        width = min(next_power_of_2(min_size), max_width)
        height = min(next_power_of_2(min_size), max_height)
        
        # Log the estimated atlas size
        log_info(f"Creating texture atlas '{self.name}' with dimensions {width}x{height} pixels")
        
        # Create the atlas surface
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        
        # Pack images using a simple bin-packing algorithm
        return self._pack_images(images_dict)
    
    def _pack_images(self, images_dict):
        """
        Pack images into the atlas using a simple bin-packing algorithm.
        Uses a binary tree packing approach.
        
        Args:
            images_dict: Dictionary mapping keys to pygame Surface objects
            
        Returns:
            bool: Success or failure
        """
        start_time = pygame.time.get_ticks()
        
        # We'll use a simple rectangle packing algorithm
        # First sort images by height (descending)
        sorted_items = sorted(
            [(key, img) for key, img in images_dict.items()],
            key=lambda item: item[1].get_height() * 10000 + item[1].get_width(),
            reverse=True
        )
        
        # Initialize free rectangles list with the entire atlas
        free_rects = [pygame.Rect(0, 0, self.width, self.height)]
        
        total_pixel_area = 0
        
        # Place each image
        for key, image in sorted_items:
            img_width = image.get_width() + self.padding * 2
            img_height = image.get_height() + self.padding * 2
            
            # Find best position (minimize wasted space)
            best_rect = None
            best_waste = float('inf')
            
            for rect in free_rects:
                # Check if image fits in this rect
                if rect.width >= img_width and rect.height >= img_height:
                    # Calculate waste
                    waste = rect.width * rect.height - img_width * img_height
                    if waste < best_waste:
                        best_waste = waste
                        best_rect = rect
            
            if best_rect is None:
                log_warning(f"Could not fit image '{key}' ({img_width}x{img_height}) in atlas")
                continue
                
            # Place image at the position
            x = best_rect.x + self.padding
            y = best_rect.y + self.padding
            
            # Blit the image onto the atlas
            self.surface.blit(image, (x, y))
            
            # Record the region
            region_rect = pygame.Rect(x, y, image.get_width(), image.get_height())
            self.regions[key] = region_rect
            
            # Update statistics
            total_pixel_area += image.get_width() * image.get_height()
            
            # Remove the used rectangle
            free_rects.remove(best_rect)
            
            # Add new free rectangles (split the space)
            if best_rect.width > img_width:
                # Add a free rectangle to the right
                free_rects.append(pygame.Rect(
                    best_rect.x + img_width,
                    best_rect.y,
                    best_rect.width - img_width,
                    best_rect.height
                ))
                
            if best_rect.height > img_height:
                # Add a free rectangle below
                free_rects.append(pygame.Rect(
                    best_rect.x,
                    best_rect.y + img_height,
                    min(best_rect.width, img_width),
                    best_rect.height - img_height
                ))
        
        # Calculate efficiency metrics
        self.used_area = total_pixel_area
        self.efficiency = total_pixel_area / (self.width * self.height) * 100
        
        end_time = pygame.time.get_ticks()
        packing_time = (end_time - start_time) / 1000.0
        
        # Log atlas creation statistics
        log_info(f"Texture atlas '{self.name}' created with {len(self.regions)} images")
        log_info(f"Atlas size: {self.width}x{self.height}, efficiency: {self.efficiency:.1f}%")
        log_performance(f"Texture Atlas Packing ({self.name})", packing_time)
        
        return len(self.regions) > 0
    
    def get_image(self, key):
        """
        Extract a specific image from the atlas.
        
        Args:
            key: The key of the image to extract
            
        Returns:
            pygame.Surface: The extracted image or None if not found
        """
        if key not in self.regions:
            return None
            
        region = self.regions[key]
        image = pygame.Surface((region.width, region.height), pygame.SRCALPHA)
        image.blit(self.surface, (0, 0), region)
        return image
    
    def get_region(self, key):
        """
        Get the region information for a specific image in the atlas.
        
        Args:
            key: The key of the image
            
        Returns:
            pygame.Rect: The region of the image in the atlas or None
        """
        return self.regions.get(key)
    
    def save(self, filepath):
        """
        Save the texture atlas to a file.
        
        Args:
            filepath: Path to save the texture atlas image
            
        Returns:
            bool: Success or failure
        """
        if self.surface is None:
            return False
            
        try:
            pygame.image.save(self.surface, filepath)
            log_info(f"Saved texture atlas to {filepath}")
            return True
        except Exception as e:
            log_error(f"Failed to save texture atlas: {str(e)}")
            return False
            
    def get_atlas_surface(self):
        """Get the texture atlas surface."""
        return self.surface
        
    def get_stats(self):
        """Get statistics about the texture atlas."""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "image_count": len(self.regions),
            "used_area": self.used_area,
            "efficiency": self.efficiency
        } 