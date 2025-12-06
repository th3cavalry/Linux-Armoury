#!/usr/bin/env python3
"""
System Monitor Module for Linux Armoury
Provides comprehensive system monitoring: CPU, RAM, Disk, Network, Processes
"""

import os
import re
import time
import subprocess
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from collections import deque


@dataclass
class CpuStats:
    """CPU statistics"""
    # Overall usage
    usage_percent: float = 0.0
    user_percent: float = 0.0
    system_percent: float = 0.0
    idle_percent: float = 0.0
    iowait_percent: float = 0.0
    
    # Per-core usage
    core_usage: List[float] = field(default_factory=list)
    core_count: int = 0
    thread_count: int = 0
    
    # Frequencies
    current_freq_mhz: float = 0.0
    min_freq_mhz: float = 0.0
    max_freq_mhz: float = 0.0
    per_core_freq: List[float] = field(default_factory=list)
    
    # CPU info
    model_name: str = "Unknown"
    architecture: str = "Unknown"
    vendor: str = "Unknown"
    
    # Load averages
    load_1min: float = 0.0
    load_5min: float = 0.0
    load_15min: float = 0.0
    
    # Context switches and interrupts
    context_switches: int = 0
    interrupts: int = 0


@dataclass
class MemoryStats:
    """Memory statistics"""
    # RAM
    total_mb: int = 0
    used_mb: int = 0
    free_mb: int = 0
    available_mb: int = 0
    cached_mb: int = 0
    buffers_mb: int = 0
    usage_percent: float = 0.0
    
    # Swap
    swap_total_mb: int = 0
    swap_used_mb: int = 0
    swap_free_mb: int = 0
    swap_usage_percent: float = 0.0


@dataclass
class DiskStats:
    """Disk statistics for a single partition"""
    device: str = ""
    mountpoint: str = ""
    filesystem: str = ""
    total_gb: float = 0.0
    used_gb: float = 0.0
    free_gb: float = 0.0
    usage_percent: float = 0.0
    
    # I/O stats (if available)
    read_bytes_sec: float = 0.0
    write_bytes_sec: float = 0.0
    read_count: int = 0
    write_count: int = 0


@dataclass
class NetworkStats:
    """Network statistics for a single interface"""
    interface: str = ""
    ip_address: str = ""
    mac_address: str = ""
    is_up: bool = False
    
    # Traffic (bytes)
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    
    # Rates (bytes per second)
    send_rate: float = 0.0
    recv_rate: float = 0.0
    
    # Errors
    errors_in: int = 0
    errors_out: int = 0
    drops_in: int = 0
    drops_out: int = 0


@dataclass
class ProcessInfo:
    """Information about a single process"""
    pid: int = 0
    name: str = ""
    user: str = ""
    cpu_percent: float = 0.0
    mem_percent: float = 0.0
    mem_mb: float = 0.0
    status: str = ""
    nice: int = 0
    threads: int = 0
    command: str = ""


@dataclass
class SystemOverview:
    """System overview statistics"""
    hostname: str = ""
    kernel: str = ""
    os_name: str = ""
    os_version: str = ""
    uptime_seconds: int = 0
    uptime_str: str = ""
    boot_time: str = ""
    logged_users: int = 0
    process_count: int = 0
    thread_count: int = 0


class SystemMonitor:
    """Comprehensive system monitoring"""
    
    def __init__(self):
        # Previous values for rate calculations
        self._prev_cpu_times = None
        self._prev_per_core_times = None
        self._prev_net_stats = {}
        self._prev_disk_stats = {}
        self._prev_time = time.time()
        
        # History for graphs (last 60 samples)
        self.cpu_history = deque(maxlen=60)
        self.mem_history = deque(maxlen=60)
        self.net_send_history = deque(maxlen=60)
        self.net_recv_history = deque(maxlen=60)
        
        # Initialize
        self._init_cpu_info()
    
    def _init_cpu_info(self):
        """Initialize static CPU information"""
        self._cpu_model = "Unknown"
        self._cpu_vendor = "Unknown"
        self._cpu_arch = "Unknown"
        self._cpu_cores = 0
        self._cpu_threads = 0
        
        try:
            with open("/proc/cpuinfo") as f:
                cpuinfo = f.read()
                
            # Model name
            match = re.search(r"model name\s*:\s*(.+)", cpuinfo)
            if match:
                self._cpu_model = match.group(1).strip()
            
            # Vendor
            match = re.search(r"vendor_id\s*:\s*(.+)", cpuinfo)
            if match:
                self._cpu_vendor = match.group(1).strip()
            
            # Count cores and threads
            self._cpu_threads = len(re.findall(r"processor\s*:", cpuinfo))
            
            # Physical cores
            cores_set = set()
            for match in re.finditer(r"core id\s*:\s*(\d+)", cpuinfo):
                cores_set.add(int(match.group(1)))
            self._cpu_cores = len(cores_set) if cores_set else self._cpu_threads
            
        except Exception:
            pass
        
        try:
            result = subprocess.run(["uname", "-m"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self._cpu_arch = result.stdout.strip()
        except Exception:
            pass
    
    def _read_file(self, path: str) -> str:
        """Safely read a file"""
        try:
            with open(path) as f:
                return f.read()
        except Exception:
            return ""
    
    def _parse_meminfo(self) -> Dict[str, int]:
        """Parse /proc/meminfo"""
        result = {}
        content = self._read_file("/proc/meminfo")
        for line in content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                # Value is typically in kB
                match = re.search(r"(\d+)", value)
                if match:
                    result[key.strip()] = int(match.group(1))
        return result
    
    def _parse_cpu_stat(self) -> Tuple[List[int], List[List[int]]]:
        """Parse /proc/stat for CPU times"""
        content = self._read_file("/proc/stat")
        lines = content.split("\n")
        
        total_times = []
        per_core_times = []
        
        for line in lines:
            if line.startswith("cpu "):
                # Total CPU
                parts = line.split()[1:]
                total_times = [int(x) for x in parts[:7]]
            elif line.startswith("cpu") and line[3].isdigit():
                # Per-core
                parts = line.split()[1:]
                per_core_times.append([int(x) for x in parts[:7]])
        
        return total_times, per_core_times
    
    def get_cpu_stats(self) -> CpuStats:
        """Get current CPU statistics"""
        stats = CpuStats()
        
        # Static info
        stats.model_name = self._cpu_model
        stats.vendor = self._cpu_vendor
        stats.architecture = self._cpu_arch
        stats.core_count = self._cpu_cores
        stats.thread_count = self._cpu_threads
        
        # Parse CPU times
        current_times, per_core_times = self._parse_cpu_stat()
        current_time = time.time()
        
        if self._prev_cpu_times and len(current_times) >= 7:
            # Calculate deltas
            deltas = [curr - prev for curr, prev in zip(current_times, self._prev_cpu_times)]
            total = sum(deltas) or 1
            
            # user, nice, system, idle, iowait, irq, softirq
            stats.user_percent = ((deltas[0] + deltas[1]) / total) * 100
            stats.system_percent = ((deltas[2] + deltas[5] + deltas[6]) / total) * 100
            stats.idle_percent = (deltas[3] / total) * 100
            stats.iowait_percent = (deltas[4] / total) * 100
            stats.usage_percent = 100 - stats.idle_percent
        
        # Per-core usage
        if self._prev_per_core_times and per_core_times:
            for i, (curr, prev) in enumerate(zip(per_core_times, self._prev_per_core_times)):
                if len(curr) >= 4 and len(prev) >= 4:
                    deltas = [c - p for c, p in zip(curr, prev)]
                    total = sum(deltas) or 1
                    usage = 100 - (deltas[3] / total * 100)  # 100 - idle
                    stats.core_usage.append(round(usage, 1))
        
        # Store for next calculation
        self._prev_cpu_times = current_times
        self._prev_per_core_times = per_core_times
        self._prev_time = current_time
        
        # Frequencies
        try:
            # Try cpufreq first
            freq_path = "/sys/devices/system/cpu/cpu0/cpufreq"
            if os.path.exists(freq_path):
                cur_freq = self._read_file(f"{freq_path}/scaling_cur_freq")
                min_freq = self._read_file(f"{freq_path}/scaling_min_freq")
                max_freq = self._read_file(f"{freq_path}/scaling_max_freq")
                
                if cur_freq:
                    stats.current_freq_mhz = int(cur_freq) / 1000
                if min_freq:
                    stats.min_freq_mhz = int(min_freq) / 1000
                if max_freq:
                    stats.max_freq_mhz = int(max_freq) / 1000
                
                # Per-core frequencies
                for i in range(stats.thread_count):
                    core_freq = self._read_file(f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq")
                    if core_freq:
                        stats.per_core_freq.append(int(core_freq) / 1000)
        except Exception:
            pass
        
        # Load averages
        loadavg = self._read_file("/proc/loadavg")
        if loadavg:
            parts = loadavg.split()
            if len(parts) >= 3:
                stats.load_1min = float(parts[0])
                stats.load_5min = float(parts[1])
                stats.load_15min = float(parts[2])
        
        # Context switches and interrupts
        stat_content = self._read_file("/proc/stat")
        for line in stat_content.split("\n"):
            if line.startswith("ctxt"):
                stats.context_switches = int(line.split()[1])
            elif line.startswith("intr"):
                stats.interrupts = int(line.split()[1])
        
        # Add to history
        self.cpu_history.append(stats.usage_percent)
        
        return stats
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics"""
        stats = MemoryStats()
        meminfo = self._parse_meminfo()
        
        # RAM (values in kB, convert to MB)
        stats.total_mb = meminfo.get("MemTotal", 0) // 1024
        stats.free_mb = meminfo.get("MemFree", 0) // 1024
        stats.available_mb = meminfo.get("MemAvailable", 0) // 1024
        stats.cached_mb = meminfo.get("Cached", 0) // 1024
        stats.buffers_mb = meminfo.get("Buffers", 0) // 1024
        
        # Used = Total - Available (more accurate than Total - Free)
        stats.used_mb = stats.total_mb - stats.available_mb
        
        if stats.total_mb > 0:
            stats.usage_percent = (stats.used_mb / stats.total_mb) * 100
        
        # Swap
        stats.swap_total_mb = meminfo.get("SwapTotal", 0) // 1024
        stats.swap_free_mb = meminfo.get("SwapFree", 0) // 1024
        stats.swap_used_mb = stats.swap_total_mb - stats.swap_free_mb
        
        if stats.swap_total_mb > 0:
            stats.swap_usage_percent = (stats.swap_used_mb / stats.swap_total_mb) * 100
        
        # Add to history
        self.mem_history.append(stats.usage_percent)
        
        return stats
    
    def get_disk_stats(self) -> List[DiskStats]:
        """Get disk usage statistics for all mounted partitions"""
        disks = []
        
        # Read /proc/mounts for mounted filesystems
        mounts = self._read_file("/proc/mounts")
        seen_devices = set()
        
        for line in mounts.split("\n"):
            parts = line.split()
            if len(parts) < 3:
                continue
            
            device, mountpoint, fstype = parts[0], parts[1], parts[2]
            
            # Skip pseudo filesystems
            if fstype in ["sysfs", "proc", "devtmpfs", "devpts", "tmpfs", "securityfs",
                          "cgroup", "cgroup2", "pstore", "efivarfs", "bpf", "autofs",
                          "hugetlbfs", "mqueue", "debugfs", "tracefs", "fusectl",
                          "configfs", "ramfs", "fuse.portal", "fuse.gvfsd-fuse",
                          "overlay", "squashfs"]:
                continue
            
            # Skip if device already seen (like bind mounts)
            if device in seen_devices:
                continue
            seen_devices.add(device)
            
            # Skip snap mounts
            if "/snap/" in mountpoint:
                continue
            
            disk = DiskStats()
            disk.device = device
            disk.mountpoint = mountpoint
            disk.filesystem = fstype
            
            try:
                statvfs = os.statvfs(mountpoint)
                block_size = statvfs.f_frsize
                disk.total_gb = (statvfs.f_blocks * block_size) / (1024**3)
                disk.free_gb = (statvfs.f_bfree * block_size) / (1024**3)
                disk.used_gb = disk.total_gb - disk.free_gb
                
                if disk.total_gb > 0:
                    disk.usage_percent = (disk.used_gb / disk.total_gb) * 100
                
                disks.append(disk)
            except (PermissionError, OSError):
                continue
        
        # Get I/O stats from /proc/diskstats
        diskstats = self._read_file("/proc/diskstats")
        io_stats = {}
        for line in diskstats.split("\n"):
            parts = line.split()
            if len(parts) >= 14:
                dev_name = parts[2]
                io_stats[dev_name] = {
                    'reads': int(parts[3]),
                    'read_sectors': int(parts[5]),
                    'writes': int(parts[7]),
                    'write_sectors': int(parts[9])
                }
        
        # Match I/O stats to disks
        for disk in disks:
            dev_name = os.path.basename(disk.device)
            if dev_name in io_stats:
                disk.read_count = io_stats[dev_name]['reads']
                disk.write_count = io_stats[dev_name]['writes']
        
        return disks
    
    def get_network_stats(self) -> List[NetworkStats]:
        """Get network statistics for all interfaces"""
        interfaces = []
        
        # Read /proc/net/dev
        net_dev = self._read_file("/proc/net/dev")
        current_time = time.time()
        time_delta = current_time - self._prev_time if self._prev_time else 1
        
        for line in net_dev.split("\n")[2:]:  # Skip header lines
            if ":" not in line:
                continue
            
            parts = line.split(":")
            iface_name = parts[0].strip()
            
            # Skip loopback
            if iface_name == "lo":
                continue
            
            values = parts[1].split()
            if len(values) < 16:
                continue
            
            net = NetworkStats()
            net.interface = iface_name
            net.bytes_recv = int(values[0])
            net.packets_recv = int(values[1])
            net.errors_in = int(values[2])
            net.drops_in = int(values[3])
            net.bytes_sent = int(values[8])
            net.packets_sent = int(values[9])
            net.errors_out = int(values[10])
            net.drops_out = int(values[11])
            
            # Calculate rates
            if iface_name in self._prev_net_stats:
                prev = self._prev_net_stats[iface_name]
                net.recv_rate = (net.bytes_recv - prev['recv']) / time_delta
                net.send_rate = (net.bytes_sent - prev['sent']) / time_delta
            
            self._prev_net_stats[iface_name] = {
                'recv': net.bytes_recv,
                'sent': net.bytes_sent
            }
            
            # Get IP address
            try:
                result = subprocess.run(
                    ["ip", "-4", "addr", "show", iface_name],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", result.stdout)
                    if match:
                        net.ip_address = match.group(1)
            except Exception:
                pass
            
            # Check if interface is up
            try:
                operstate = self._read_file(f"/sys/class/net/{iface_name}/operstate")
                net.is_up = operstate.strip() == "up"
            except Exception:
                pass
            
            # Get MAC address
            try:
                mac = self._read_file(f"/sys/class/net/{iface_name}/address")
                net.mac_address = mac.strip()
            except Exception:
                pass
            
            interfaces.append(net)
        
        # Update history (total send/recv rate)
        total_send = sum(n.send_rate for n in interfaces)
        total_recv = sum(n.recv_rate for n in interfaces)
        self.net_send_history.append(total_send)
        self.net_recv_history.append(total_recv)
        
        return interfaces
    
    def get_top_processes(self, count: int = 10, sort_by: str = "cpu") -> List[ProcessInfo]:
        """Get top processes by CPU or memory usage"""
        processes = []
        
        try:
            # Use ps command for process info
            cmd = ["ps", "aux", "--sort", f"-{'%cpu' if sort_by == 'cpu' else '%mem'}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return processes
            
            lines = result.stdout.strip().split("\n")[1:count+1]  # Skip header, get top N
            
            for line in lines:
                parts = line.split(None, 10)  # Split max 11 parts
                if len(parts) < 11:
                    continue
                
                proc = ProcessInfo()
                proc.user = parts[0]
                proc.pid = int(parts[1])
                proc.cpu_percent = float(parts[2])
                proc.mem_percent = float(parts[3])
                proc.mem_mb = 0  # Would need to calculate from RSS
                proc.status = parts[7] if len(parts) > 7 else ""
                proc.command = parts[10] if len(parts) > 10 else ""
                proc.name = os.path.basename(proc.command.split()[0]) if proc.command else ""
                
                processes.append(proc)
        except Exception as e:
            print(f"Error getting processes: {e}")
        
        return processes
    
    def get_system_overview(self) -> SystemOverview:
        """Get system overview information"""
        info = SystemOverview()
        
        # Hostname
        try:
            info.hostname = os.uname().nodename
        except Exception:
            pass
        
        # Kernel
        try:
            info.kernel = os.uname().release
        except Exception:
            pass
        
        # OS info from /etc/os-release
        os_release = self._read_file("/etc/os-release")
        for line in os_release.split("\n"):
            if line.startswith("NAME="):
                info.os_name = line.split("=", 1)[1].strip('"')
            elif line.startswith("VERSION="):
                info.os_version = line.split("=", 1)[1].strip('"')
        
        # Uptime
        uptime_str = self._read_file("/proc/uptime")
        if uptime_str:
            info.uptime_seconds = int(float(uptime_str.split()[0]))
            
            # Format uptime
            days = info.uptime_seconds // 86400
            hours = (info.uptime_seconds % 86400) // 3600
            minutes = (info.uptime_seconds % 3600) // 60
            
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            parts.append(f"{minutes}m")
            info.uptime_str = " ".join(parts)
        
        # Boot time
        try:
            stat = self._read_file("/proc/stat")
            for line in stat.split("\n"):
                if line.startswith("btime"):
                    btime = int(line.split()[1])
                    info.boot_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(btime))
                    break
        except Exception:
            pass
        
        # Logged users
        try:
            result = subprocess.run(["who"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                info.logged_users = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        except Exception:
            pass
        
        # Process and thread count
        try:
            loadavg = self._read_file("/proc/loadavg")
            if loadavg:
                parts = loadavg.split()
                if len(parts) >= 4:
                    # Format: "running/total"
                    proc_info = parts[3].split("/")
                    if len(proc_info) == 2:
                        info.process_count = int(proc_info[1])
        except Exception:
            pass
        
        return info
    
    def format_bytes(self, bytes_val: float, precision: int = 1) -> str:
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(bytes_val) < 1024:
                return f"{bytes_val:.{precision}f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.{precision}f} PB"
    
    def format_bytes_rate(self, bytes_per_sec: float) -> str:
        """Format bytes per second to human readable string"""
        return f"{self.format_bytes(bytes_per_sec)}/s"


# Singleton instance
_monitor: Optional[SystemMonitor] = None

def get_monitor() -> SystemMonitor:
    """Get or create the system monitor singleton"""
    global _monitor
    if _monitor is None:
        _monitor = SystemMonitor()
    return _monitor


if __name__ == "__main__":
    # Test the module
    monitor = get_monitor()
    
    print("=== System Overview ===")
    overview = monitor.get_system_overview()
    print(f"  Hostname: {overview.hostname}")
    print(f"  OS: {overview.os_name} {overview.os_version}")
    print(f"  Kernel: {overview.kernel}")
    print(f"  Uptime: {overview.uptime_str}")
    print(f"  Processes: {overview.process_count}")
    
    print("\n=== CPU Stats ===")
    # Need two samples for accurate usage
    cpu = monitor.get_cpu_stats()
    time.sleep(0.5)
    cpu = monitor.get_cpu_stats()
    print(f"  Model: {cpu.model_name}")
    print(f"  Cores: {cpu.core_count} ({cpu.thread_count} threads)")
    print(f"  Usage: {cpu.usage_percent:.1f}%")
    print(f"  Freq: {cpu.current_freq_mhz:.0f} MHz ({cpu.min_freq_mhz:.0f}-{cpu.max_freq_mhz:.0f})")
    print(f"  Load: {cpu.load_1min:.2f}, {cpu.load_5min:.2f}, {cpu.load_15min:.2f}")
    
    print("\n=== Memory Stats ===")
    mem = monitor.get_memory_stats()
    print(f"  RAM: {mem.used_mb}/{mem.total_mb} MB ({mem.usage_percent:.1f}%)")
    print(f"  Available: {mem.available_mb} MB")
    print(f"  Cached: {mem.cached_mb} MB, Buffers: {mem.buffers_mb} MB")
    print(f"  Swap: {mem.swap_used_mb}/{mem.swap_total_mb} MB ({mem.swap_usage_percent:.1f}%)")
    
    print("\n=== Disk Stats ===")
    for disk in monitor.get_disk_stats():
        print(f"  {disk.mountpoint}: {disk.used_gb:.1f}/{disk.total_gb:.1f} GB ({disk.usage_percent:.1f}%) [{disk.filesystem}]")
    
    print("\n=== Network Stats ===")
    # Need two samples for accurate rates
    net = monitor.get_network_stats()
    time.sleep(0.5)
    net = monitor.get_network_stats()
    for n in net:
        status = "UP" if n.is_up else "DOWN"
        print(f"  {n.interface} ({status}): {n.ip_address or 'No IP'}")
        print(f"    TX: {monitor.format_bytes(n.bytes_sent)} ({monitor.format_bytes_rate(n.send_rate)})")
        print(f"    RX: {monitor.format_bytes(n.bytes_recv)} ({monitor.format_bytes_rate(n.recv_rate)})")
    
    print("\n=== Top Processes (by CPU) ===")
    for proc in monitor.get_top_processes(5, "cpu"):
        print(f"  {proc.pid:6d} {proc.name:20s} CPU: {proc.cpu_percent:5.1f}% MEM: {proc.mem_percent:5.1f}%")
