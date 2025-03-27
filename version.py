"""
Space Shooter Game - Version Information
"""

VERSION = "0.3.9"
VERSION_NAME = "Performance Optimized"
RELEASE_DATE = "2023-10-25"

VERSION_INFO = {
    "major": 0,
    "minor": 3,
    "patch": 9,
    "status": "stable",
    "features": [
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