#!/usr/bin/env python3
"""
Session Statistics Tracker for Linux Armoury
Tracks system metrics over time for analysis
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass, asdict


@dataclass
class MetricSample:
    """A single metric sample with timestamp"""
    timestamp: str
    cpu_temp: Optional[float] = None
    gpu_temp: Optional[float] = None
    battery_level: Optional[int] = None
    on_ac: Optional[bool] = None
    power_profile: Optional[str] = None


class SessionStatistics:
    """Track and store session statistics"""
    
    # Keep last 30 minutes of samples (at 2 second intervals = 900 samples)
    MAX_SAMPLES = 900
    STATS_DIR = os.path.expanduser("~/.local/share/linux-armoury/stats")
    
    def __init__(self):
        self.samples: deque = deque(maxlen=self.MAX_SAMPLES)
        self.session_start = datetime.now()
        
        # Session stats
        self.max_cpu_temp = 0.0
        self.max_gpu_temp = 0.0
        self.avg_cpu_temp = 0.0
        self.avg_gpu_temp = 0.0
        self.total_samples = 0
        
        # Battery tracking
        self.initial_battery: Optional[int] = None
        self.time_on_battery = 0
        self.time_on_ac = 0
        self.last_update: Optional[datetime] = None
        
        # Profile usage tracking
        self.profile_time: Dict[str, int] = {}
        self.current_profile: Optional[str] = None
        
        # Ensure stats directory exists
        os.makedirs(self.STATS_DIR, exist_ok=True)
    
    def add_sample(self, cpu_temp: Optional[float], gpu_temp: Optional[float],
                   battery: Optional[int], on_ac: bool, profile: Optional[str] = None):
        """Add a new metric sample"""
        now = datetime.now()
        
        sample = MetricSample(
            timestamp=now.isoformat(),
            cpu_temp=cpu_temp,
            gpu_temp=gpu_temp,
            battery_level=battery,
            on_ac=on_ac,
            power_profile=profile
        )
        self.samples.append(sample)
        
        # Update statistics
        if cpu_temp is not None:
            self.max_cpu_temp = max(self.max_cpu_temp, cpu_temp)
            # Running average
            self.avg_cpu_temp = (
                (self.avg_cpu_temp * self.total_samples + cpu_temp) / 
                (self.total_samples + 1)
            )
        
        if gpu_temp is not None:
            self.max_gpu_temp = max(self.max_gpu_temp, gpu_temp)
            self.avg_gpu_temp = (
                (self.avg_gpu_temp * self.total_samples + gpu_temp) / 
                (self.total_samples + 1)
            )
        
        self.total_samples += 1
        
        # Track initial battery
        if self.initial_battery is None and battery is not None:
            self.initial_battery = battery
        
        # Track time on AC/battery
        if self.last_update is not None:
            delta = (now - self.last_update).total_seconds()
            if on_ac:
                self.time_on_ac += delta
            else:
                self.time_on_battery += delta
        
        self.last_update = now
        
        # Track profile usage
        if profile:
            if profile != self.current_profile:
                self.current_profile = profile
            
            if profile not in self.profile_time:
                self.profile_time[profile] = 0
            
            if self.last_update:
                self.profile_time[profile] += 2  # Approx 2 seconds per sample
    
    def get_session_duration(self) -> str:
        """Get human-readable session duration"""
        delta = datetime.now() - self.session_start
        total_seconds = int(delta.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_battery_drain(self) -> Optional[int]:
        """Get battery drain during session"""
        if self.initial_battery is None:
            return None
        
        current = None
        if self.samples:
            for sample in reversed(self.samples):
                if sample.battery_level is not None:
                    current = sample.battery_level
                    break
        
        if current is None:
            return None
        
        return self.initial_battery - current
    
    def get_summary(self) -> Dict:
        """Get session summary statistics"""
        battery_drain = self.get_battery_drain()
        
        return {
            'session_duration': self.get_session_duration(),
            'session_start': self.session_start.strftime("%H:%M:%S"),
            'total_samples': self.total_samples,
            'cpu': {
                'max_temp': round(self.max_cpu_temp, 1) if self.max_cpu_temp > 0 else None,
                'avg_temp': round(self.avg_cpu_temp, 1) if self.avg_cpu_temp > 0 else None,
            },
            'gpu': {
                'max_temp': round(self.max_gpu_temp, 1) if self.max_gpu_temp > 0 else None,
                'avg_temp': round(self.avg_gpu_temp, 1) if self.avg_gpu_temp > 0 else None,
            },
            'battery': {
                'initial': self.initial_battery,
                'drain': battery_drain,
                'time_on_battery_min': round(self.time_on_battery / 60, 1),
                'time_on_ac_min': round(self.time_on_ac / 60, 1),
            },
            'profiles': self.profile_time.copy(),
        }
    
    def get_temperature_history(self, limit: int = 60) -> Dict[str, List]:
        """Get recent temperature history for graphing
        
        Args:
            limit: Number of samples to return (default 60 = ~2 minutes)
            
        Returns:
            Dict with 'cpu' and 'gpu' lists of temperatures
        """
        recent = list(self.samples)[-limit:] if self.samples else []
        
        return {
            'timestamps': [s.timestamp for s in recent],
            'cpu': [s.cpu_temp for s in recent],
            'gpu': [s.gpu_temp for s in recent],
            'battery': [s.battery_level for s in recent],
        }
    
    def save_session(self):
        """Save session statistics to file"""
        filename = self.session_start.strftime("session_%Y%m%d_%H%M%S.json")
        filepath = os.path.join(self.STATS_DIR, filename)
        
        data = {
            'summary': self.get_summary(),
            'samples': [asdict(s) for s in list(self.samples)[-100:]]  # Last 100 samples
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return filepath
        except Exception as e:
            print(f"Error saving session: {e}")
            return None
    
    def load_historical_stats(self) -> List[Dict]:
        """Load historical session summaries"""
        sessions = []
        
        try:
            if os.path.exists(self.STATS_DIR):
                for filename in sorted(os.listdir(self.STATS_DIR), reverse=True)[:10]:
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.STATS_DIR, filename)
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            if 'summary' in data:
                                data['summary']['filename'] = filename
                                sessions.append(data['summary'])
        except Exception as e:
            print(f"Error loading historical stats: {e}")
        
        return sessions


# Global instance
_session_stats: Optional[SessionStatistics] = None


def get_session_stats() -> SessionStatistics:
    """Get or create the global session statistics instance"""
    global _session_stats
    if _session_stats is None:
        _session_stats = SessionStatistics()
    return _session_stats
