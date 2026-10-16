#!/usr/bin/env python3
"""Read-only memory/pressure check and conservative cover generation concurrency hint."""
import json
import os
import platform
import subprocess
import sys


def run(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def memory_bytes():
    system = platform.system()
    if system == "Darwin":
        output = run(["sysctl", "-n", "hw.memsize"]).strip()
        try:
            total = int(output)
        except ValueError:
            try:
                total = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
            except (ValueError, OSError, AttributeError):
                return None, None
        pressure = run(["memory_pressure"])
        free_pct = None
        for line in pressure.splitlines():
            if "System-wide memory free percentage:" in line:
                try:
                    free_pct = int(line.split(":", 1)[1].strip().rstrip("%"))
                except ValueError:
                    pass
        return total, (free_pct * total // 100 if free_pct is not None else None)
    if system == "Linux":
        try:
            data = {}
            for line in open("/proc/meminfo", encoding="ascii"):
                key, value = line.split(":", 1)
                data[key] = int(value.split()[0]) * 1024
            return data["MemTotal"], data.get("MemAvailable")
        except (OSError, KeyError, ValueError):
            return None, None
    if system == "Windows":
        try:
            import ctypes
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong), ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong), ("total_page", ctypes.c_ulonglong), ("avail_page", ctypes.c_ulonglong), ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong), ("avail_extended", ctypes.c_ulonglong)]
            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return status.total_phys, status.avail_phys
        except Exception:
            pass
    return None, None


def main():
    total, available = memory_bytes()
    gb = total / (1024 ** 3) if total else None
    free = available / total if available is not None and total else None
    reasons = []
    if total is None or available is None:
        recommended = 1
        reasons.append("memory could not be reliably detected")
    elif gb <= 8:
        recommended = 1
        reasons.append("total memory is 8 GB or less")
    else:
        # The native APIs expose free/available memory, not a portable pressure color.
        healthy = free >= 0.25
        if not healthy:
            recommended = 1
            reasons.append("available memory is below 25%; treat pressure as non-green")
        else:
            recommended = 2 if gb < 24 else 3 if gb < 48 else 4
            reasons.append("memory is available; macOS free percentage is an approximation, not the pressure color")
    print(json.dumps({"os": platform.platform(), "total_gib": round(gb, 2) if gb is not None else None, "available_gib": round(available / (1024 ** 3), 2) if available is not None else None, "available_fraction": round(free, 3) if free is not None else None, "recommended_parallelism": recommended, "reason": "; ".join(reasons), "read_only": True}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
