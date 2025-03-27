class GameError(Exception):
    """Base exception class for the game."""
    pass

class AssetLoadError(GameError):
    """Raised when a game asset fails to load."""
    pass

class ConfigurationError(GameError):
    """Raised when there's an error in game configuration."""
    pass

class ResourceError(GameError):
    """Raised when a required resource is missing or invalid."""
    pass

class GameStateError(GameError):
    """Raised when an invalid game state transition is attempted."""
    pass

class CollisionError(GameError):
    """Raised when there's an error in collision detection."""
    pass

class RenderError(GameError):
    """Raised when there's an error rendering game elements."""
    pass

class AudioError(GameError):
    """Raised when there's an error with audio playback."""
    pass

class InputError(GameError):
    """Raised when there's an error processing user input."""
    pass

class NetworkError(GameError):
    """Raised when there's an error with network operations."""
    pass

class SaveGameError(GameError):
    """Raised when there's an error saving or loading game state."""
    pass 