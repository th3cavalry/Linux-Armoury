#!/usr/bin/env python3
"""
Configuration constants and settings for Linux Armoury
"""

class Config:
    """Application configuration constants"""
    
    # Application Info
    APP_ID = 'com.github.th3cavalry.linux-armoury'
    APP_NAME = 'Linux Armoury'
    VERSION = '1.1.0'
    AUTHOR = 'th3cavalry'
    WEBSITE = 'https://github.com/th3cavalry/Linux-Armoury'
    
    # Display Settings
    DEFAULT_RESOLUTION = '2560x1600'
    SUPPORTED_REFRESH_RATES = [30, 60, 90, 120, 180]
    
    # Power Settings
    MIN_TDP = 10
    MAX_TDP = 90
    
    # Power Profiles Configuration
    POWER_PROFILES = {
        'emergency': {
            'name': 'Emergency',
            'tdp': 10,
            'refresh': 30,
            'description': '10W @ 30Hz - Critical battery preservation'
        },
        'battery': {
            'name': 'Battery Saver',
            'tdp': 18,
            'refresh': 30,
            'description': '18W @ 30Hz - Maximum battery life'
        },
        'efficient': {
            'name': 'Efficient',
            'tdp': 30,
            'refresh': 60,
            'description': '30W @ 60Hz - Balanced efficiency'
        },
        'balanced': {
            'name': 'Balanced',
            'tdp': 40,
            'refresh': 90,
            'description': '40W @ 90Hz - Default balanced mode'
        },
        'performance': {
            'name': 'Performance',
            'tdp': 55,
            'refresh': 120,
            'description': '55W @ 120Hz - High performance'
        },
        'gaming': {
            'name': 'Gaming',
            'tdp': 70,
            'refresh': 180,
            'description': '70W @ 180Hz - Gaming optimized'
        },
        'maximum': {
            'name': 'Maximum',
            'tdp': 90,
            'refresh': 180,
            'description': '90W @ 180Hz - Absolute maximum'
        }
    }
    
    # Refresh Rate Profiles
    REFRESH_PROFILES = {
        '30': {'name': '30 Hz', 'description': 'Power saving mode'},
        '60': {'name': '60 Hz', 'description': 'Standard'},
        '90': {'name': '90 Hz', 'description': 'Smooth'},
        '120': {'name': '120 Hz', 'description': 'High refresh'},
        '180': {'name': '180 Hz', 'description': 'Maximum gaming'}
    }
    
    # Keyboard Shortcuts
    SHORTCUTS = {
        'quit': '<Control>q',
        'preferences': '<Control>comma',
        'refresh_status': 'F5',
        'about': 'F1',
        'profile_1': '<Control>1',
        'profile_2': '<Control>2',
        'profile_3': '<Control>3',
        'profile_4': '<Control>4',
        'profile_5': '<Control>5',
        'profile_6': '<Control>6',
        'profile_7': '<Control>7'
    }
    
    # Auto-switching settings
    AUTO_SWITCH_PROFILES = {
        'ac': 'performance',  # Default AC profile
        'battery': 'efficient'  # Default battery profile
    }
    
    # Temperature thresholds
    TEMP_WARNING = 85  # °C
    TEMP_CRITICAL = 95  # °C
    
    # Notification settings
    NOTIFY_PROFILE_CHANGE = True
    NOTIFY_TEMP_WARNING = True
    NOTIFY_AC_CHANGE = True
    
    # System commands
    CMD_PWRCFG = 'pwrcfg'
    CMD_XRANDR = 'xrandr'
    CMD_PKEXEC = 'pkexec'
    
    # Timeouts
    COMMAND_TIMEOUT = 10  # seconds
    MONITOR_INTERVAL = 2000  # milliseconds
    
    # Help URLs
    HELP_INSTALL_GZ302 = 'https://github.com/th3cavalry/GZ302-Linux-Setup'
    HELP_ISSUES = 'https://github.com/th3cavalry/Linux-Armoury/issues'
    HELP_DISCUSSIONS = 'https://github.com/th3cavalry/Linux-Armoury/discussions'
