import os
import pygame
import time
from collections import defaultdict
from game_logger import log_info, log_warning, log_error, log_debug, log_performance

class AssetLoader:
    """
    Centralized asset loading system that preloads all game assets at startup
    to prevent lag spikes during gameplay. Implements caching and fallback
    mechanisms for improved performance and stability.
    """
    def __init__(self, asset_dir="assets"):
        # Base directories
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.asset_dir = os.path.join(self.base_dir, asset_dir)
        self.img_dir = os.path.join(self.asset_dir, "images")
        self.sound_dir = os.path.join(self.asset_dir, "sounds")
        
        # Cached assets
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.animations = {}
        
        # Default images for fallbacks
        self.default_images = {}
        
        # Asset loading stats
        self.loading_stats = {
            "total_assets": 0,
            "loaded_assets": 0,
            "failed_assets": 0,
            "loading_time": 0
        }
        
        # Manifest of all assets in the game
        self.asset_manifest = {
            "images": [
                # Player
                {"key": "player", "file": "player.png", "scale": (50, 40), "convert_alpha": True},
                
                # Enemies
                {"key": "enemy", "file": "enemy.png", "scale": (30, 30), "convert_alpha": True},
                {"key": "fast_enemy", "file": "fast_enemy.png", "scale": (30, 30), "convert_alpha": True},
                {"key": "tank_enemy", "file": "tank_enemy.png", "scale": (30, 30), "convert_alpha": True},
                {"key": "boss_enemy", "file": "boss_enemy.png", "scale": (60, 60), "convert_alpha": True},
                
                # Projectiles
                {"key": "bullet", "file": "bullet.png", "scale": (5, 10), "convert_alpha": True},
                
                # Power-ups
                {"key": "health_powerup", "file": "health_powerup.png", "scale": (25, 25), "convert_alpha": True},
                {"key": "power_powerup", "file": "power_powerup.png", "scale": (25, 25), "convert_alpha": True},
                {"key": "shield_powerup", "file": "shield_powerup.png", "scale": (25, 25), "convert_alpha": True},
                
                # Environment
                {"key": "background", "file": "background.jpg", "scale": "fullscreen", "convert": True},
            ],
            "animations": [
                # Explosions
                {"key": "explosion", "base_file": "explosion", "count": 9, "extension": ".png", 
                 "convert_alpha": True, "scale": (50, 50)}
            ],
            "sounds": [
                {"key": "shoot", "file": "shoot.wav", "volume": 0.4},
                {"key": "explosion", "file": "explosion.wav", "volume": 0.6},
                {"key": "powerup", "file": "powerup.wav", "volume": 0.5},
                {"key": "game_over", "file": "game_over.wav", "volume": 0.7},
                {"key": "background_music", "file": "background_music.mp3", "volume": 0.3, "is_music": True}
            ],
            "fonts": [
                {"key": "main", "size": 36, "system_font": True},
                {"key": "small", "size": 24, "system_font": True},
                {"key": "large", "size": 48, "system_font": True}
            ]
        }
        
    def preload_all_assets(self, screen_width=800, screen_height=600):
        """
        Preload all game assets at startup to prevent lag spikes.
        
        Args:
            screen_width: Width of the game screen for scaling
            screen_height: Height of the game screen for scaling
            
        Returns:
            dict: Loading statistics
        """
        start_time = time.time()
        log_info("Preloading all game assets...")
        
        # Count total assets
        total_images = len(self.asset_manifest["images"]) + len(self.asset_manifest["animations"]) * 9
        total_sounds = len(self.asset_manifest["sounds"])
        total_fonts = len(self.asset_manifest["fonts"])
        self.loading_stats["total_assets"] = total_images + total_sounds + total_fonts
        
        # Create default fallback assets first
        self._create_default_assets()
        
        # Load all assets by type
        self._preload_images(screen_width, screen_height)
        self._preload_animations()
        self._preload_sounds()
        self._preload_fonts()
        
        # Calculate loading time
        self.loading_stats["loading_time"] = time.time() - start_time
        
        # Log results
        success_rate = (self.loading_stats["loaded_assets"] / self.loading_stats["total_assets"]) * 100
        log_info(f"Asset preloading complete: {self.loading_stats['loaded_assets']} of " + 
                 f"{self.loading_stats['total_assets']} assets loaded ({success_rate:.1f}%)")
        log_performance("Asset Preloading", self.loading_stats["loading_time"])
        
        return self.loading_stats
        
    def _create_default_assets(self):
        """Create basic colored rectangles as fallback for missing assets."""
        # Player (red rectangle)
        player_surf = pygame.Surface((50, 40), pygame.SRCALPHA)
        player_surf.fill((255, 0, 0))
        self.default_images["player"] = player_surf
        
        # Enemy (blue rectangle)
        enemy_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        enemy_surf.fill((0, 0, 255))
        self.default_images["enemy"] = enemy_surf
        self.default_images["fast_enemy"] = enemy_surf
        self.default_images["tank_enemy"] = enemy_surf
        
        # Boss (purple rectangle)
        boss_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        boss_surf.fill((128, 0, 128))
        self.default_images["boss_enemy"] = boss_surf
        
        # Bullet (white rectangle)
        bullet_surf = pygame.Surface((5, 10), pygame.SRCALPHA)
        bullet_surf.fill((255, 255, 255))
        self.default_images["bullet"] = bullet_surf
        
        # Power-ups (different colored circles)
        for key, color in [("health_powerup", (0, 255, 0)), 
                          ("power_powerup", (0, 0, 255)), 
                          ("shield_powerup", (255, 255, 0))]:
            powerup_surf = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(powerup_surf, color, (12, 12), 12)
            self.default_images[key] = powerup_surf
    
    def _preload_images(self, screen_width, screen_height):
        """Preload all images defined in the asset manifest."""
        for img_data in self.asset_manifest["images"]:
            key = img_data["key"]
            file_path = os.path.join(self.img_dir, img_data["file"])
            
            try:
                # Try to load the image file
                if os.path.exists(file_path):
                    # Load with the appropriate convert function
                    if img_data.get("convert_alpha", False):
                        image = pygame.image.load(file_path).convert_alpha()
                    else:
                        image = pygame.image.load(file_path).convert()
                    
                    # Scale if needed
                    if img_data.get("scale"):
                        if img_data["scale"] == "fullscreen":
                            image = pygame.transform.scale(image, (screen_width, screen_height))
                        else:
                            image = pygame.transform.scale(image, img_data["scale"])
                    
                    # Store in cache
                    self.images[key] = image
                    self.loading_stats["loaded_assets"] += 1
                    log_debug(f"Loaded image: {key}")
                else:
                    # File not found, use default
                    self.images[key] = self.default_images.get(key)
                    self.loading_stats["failed_assets"] += 1
                    log_warning(f"Image file not found: {img_data['file']}, using default")
            except Exception as e:
                # Loading error, use default
                self.images[key] = self.default_images.get(key)
                self.loading_stats["failed_assets"] += 1
                log_warning(f"Failed to load image {key}: {str(e)}")
    
    def _preload_animations(self):
        """Preload all animation frames defined in the asset manifest."""
        for anim_data in self.asset_manifest["animations"]:
            key = anim_data["key"]
            base_file = anim_data["base_file"]
            count = anim_data["count"]
            extension = anim_data.get("extension", ".png")
            frames = []
            
            for i in range(count):
                file_name = f"{base_file}{i}{extension}"
                file_path = os.path.join(self.img_dir, file_name)
                
                try:
                    # Try to load the animation frame
                    if os.path.exists(file_path):
                        # Load with the appropriate convert function
                        if anim_data.get("convert_alpha", False):
                            frame = pygame.image.load(file_path).convert_alpha()
                        else:
                            frame = pygame.image.load(file_path).convert()
                        
                        # Scale if needed
                        if anim_data.get("scale"):
                            frame = pygame.transform.scale(frame, anim_data["scale"])
                        
                        frames.append(frame)
                        self.loading_stats["loaded_assets"] += 1
                    else:
                        # Create a default frame if file not found
                        default_frame = pygame.Surface(anim_data.get("scale", (50, 50)), pygame.SRCALPHA)
                        default_frame.fill((255, 255, 0, 128))  # Yellow semi-transparent
                        frames.append(default_frame)
                        self.loading_stats["failed_assets"] += 1
                        log_warning(f"Animation frame not found: {file_name}, using default")
                except Exception as e:
                    # Create a default frame on error
                    default_frame = pygame.Surface(anim_data.get("scale", (50, 50)), pygame.SRCALPHA)
                    default_frame.fill((255, 0, 0, 128))  # Red semi-transparent
                    frames.append(default_frame)
                    self.loading_stats["failed_assets"] += 1
                    log_warning(f"Failed to load animation frame {file_name}: {str(e)}")
            
            # Store all frames
            if frames:
                self.animations[key] = frames
                log_debug(f"Loaded animation: {key} ({len(frames)} frames)")
            else:
                log_warning(f"No frames loaded for animation: {key}")
    
    def _preload_sounds(self):
        """Preload all sounds defined in the asset manifest."""
        for sound_data in self.asset_manifest["sounds"]:
            key = sound_data["key"]
            file_path = os.path.join(self.sound_dir, sound_data["file"])
            
            try:
                # Check if it's background music or a sound effect
                if sound_data.get("is_music", False):
                    # Just validate the file exists for music (loaded when played)
                    if os.path.exists(file_path):
                        self.sounds[key] = {"path": file_path, "is_music": True}
                        self.loading_stats["loaded_assets"] += 1
                        log_debug(f"Verified music file: {key}")
                    else:
                        self.sounds[key] = None
                        self.loading_stats["failed_assets"] += 1
                        log_warning(f"Music file not found: {sound_data['file']}")
                else:
                    # Load and cache sound effect
                    if os.path.exists(file_path):
                        sound = pygame.mixer.Sound(file_path)
                        volume = sound_data.get("volume", 1.0)
                        sound.set_volume(volume)
                        self.sounds[key] = sound
                        self.loading_stats["loaded_assets"] += 1
                        log_debug(f"Loaded sound: {key}")
                    else:
                        self.sounds[key] = None
                        self.loading_stats["failed_assets"] += 1
                        log_warning(f"Sound file not found: {sound_data['file']}")
            except Exception as e:
                self.sounds[key] = None
                self.loading_stats["failed_assets"] += 1
                log_warning(f"Failed to load sound {key}: {str(e)}")
    
    def _preload_fonts(self):
        """Preload and cache fonts used in the game."""
        for font_data in self.asset_manifest["fonts"]:
            key = font_data["key"]
            size = font_data["size"]
            
            try:
                # For system fonts
                if font_data.get("system_font", True):
                    font = pygame.font.Font(None, size)
                    self.fonts[key] = font
                    self.loading_stats["loaded_assets"] += 1
                    log_debug(f"Loaded system font: {key}")
                # For custom font files
                else:
                    font_path = os.path.join(self.asset_dir, "fonts", font_data["file"])
                    if os.path.exists(font_path):
                        font = pygame.font.Font(font_path, size)
                        self.fonts[key] = font
                        self.loading_stats["loaded_assets"] += 1
                        log_debug(f"Loaded font: {key}")
                    else:
                        # Fallback to system font
                        font = pygame.font.Font(None, size)
                        self.fonts[key] = font
                        self.loading_stats["failed_assets"] += 1
                        log_warning(f"Font file not found: {font_data.get('file', '')}, using system font")
            except Exception as e:
                # Fallback to system font on error
                try:
                    font = pygame.font.Font(None, size)
                    self.fonts[key] = font
                    self.loading_stats["failed_assets"] += 1
                    log_warning(f"Failed to load font {key}, using system font: {str(e)}")
                except:
                    self.fonts[key] = None
                    log_error(f"Could not load system font fallback for {key}")
    
    def get_image(self, key):
        """
        Get an image by key.
        
        Args:
            key (str): The image key
            
        Returns:
            Surface: The requested image or a default if not found
        """
        if key in self.images and self.images[key] is not None:
            return self.images[key]
        elif key in self.default_images:
            log_debug(f"Using default image for {key}")
            return self.default_images[key]
        else:
            log_warning(f"Image not found: {key}")
            # Return a small red square as a last resort
            fallback = pygame.Surface((30, 30), pygame.SRCALPHA)
            fallback.fill((255, 0, 0, 180))
            return fallback
    
    def get_animation(self, key):
        """
        Get an animation by key.
        
        Args:
            key (str): The animation key
            
        Returns:
            list: List of animation frames or None if not found
        """
        return self.animations.get(key, None)
    
    def get_sound(self, key):
        """
        Get a sound by key.
        
        Args:
            key (str): The sound key
            
        Returns:
            Sound: The requested sound or None if not found
        """
        return self.sounds.get(key, None)
        
    def get_font(self, key="main"):
        """
        Get a font by key.
        
        Args:
            key (str): The font key
            
        Returns:
            Font: The requested font or a default Font if not found
        """
        if key in self.fonts and self.fonts[key] is not None:
            return self.fonts[key]
        else:
            log_warning(f"Font not found: {key}, using default")
            return pygame.font.Font(None, 36)  # Default font
    
    def play_sound(self, key):
        """
        Play a sound by key.
        
        Args:
            key (str): The sound key
            
        Returns:
            bool: True if sound was played, False otherwise
        """
        sound = self.sounds.get(key)
        if sound is not None:
            # Handle background music
            if isinstance(sound, dict) and sound.get("is_music"):
                try:
                    pygame.mixer.music.load(sound["path"])
                    pygame.mixer.music.play(loops=-1)
                    return True
                except Exception as e:
                    log_warning(f"Could not play music {key}: {str(e)}")
                    return False
            # Handle regular sounds
            else:
                try:
                    sound.play()
                    return True
                except Exception as e:
                    log_warning(f"Could not play sound {key}: {str(e)}")
                    return False
        return False
    
    def get_loading_stats(self):
        """Get asset loading statistics."""
        return self.loading_stats 