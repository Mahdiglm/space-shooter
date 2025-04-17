"""
Space Shooter Game - Version Information
"""

VERSION = "0.6.0"
VERSION_NAME = "Asset Management"
RELEASE_DATE = "2024-01-15"

VERSION_INFO = {
    "major": 0,
    "minor": 6,
    "patch": 0,
    "status": "stable",
    "features": [
        "Comprehensive asset preloading system",
        "Memory usage monitoring and leak detection",
        "Sprite batch rendering system",
        "Dirty rectangle rendering optimization",
        "Spatial partitioning for collision detection",
        "Performance monitoring system",
        "Enhanced UI elements",
        "Cached asset loading",
        "Improved visual effects"
    ],
    "credits": {
        "lead_developer": "Mineser Team",
        "graphics": "Placeholder assets",
        "sound": "Placeholder sounds"
    }
}

def show_version_info():
    """Return formatted version information string."""
    return f"""
Space Shooter v{VERSION} - {VERSION_NAME}
Released: {RELEASE_DATE}
Status: {VERSION_INFO['status']}

Key Features:
{chr(10).join('- ' + feature for feature in VERSION_INFO['features'])}
"""

if __name__ == "__main__":
    print(show_version_info()) 