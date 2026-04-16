#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
import subprocess
import re

# Attempt to import gputil for NVIDIA support
try:
    import gputil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

class MaxelOSMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("MAXEL Resource Monitor")
        self.root.geometry("450x500")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        # Style Configuration
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar", 
                        troughcolor='#313244', 
                        background='#89b4fa', 
                        thickness=20)

        # Header
        tk.Label(self.root, text="System Performance", font=("Arial", 18, "bold"), 
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=25)

        # CPU Section
        self.cpu_label = self.create_label("CPU Usage: 0%")
        self.cpu_bar = self.create_bar()

        # RAM Section (With Clear Cache Button)
        ram_frame = tk.Frame(self.root, bg="#1e1e2e")
        ram_frame.pack(fill="x", padx=35, pady=5)
        
        self.ram_label = tk.Label(ram_frame, text="RAM Usage: 0%", font=("Arial", 12), 
                                 bg="#1e1e2e", fg="#bac2de")
        self.ram_label.pack(side="left")
        
        self.clear_btn = tk.Button(ram_frame, text="Clear Cache", command=self.clear_cache,
                                  font=("Arial", 9, "bold"), bg="#f38ba8", fg="#1e1e2e", 
                                  activebackground="#eba0ac", relief="flat", padx=10, cursor="hand2")
        self.clear_btn.pack(side="right")
        
        self.ram_bar = self.create_bar()

        # GPU Section (Universal Support)
        self.gpu_label = self.create_label("GPU Usage: Initializing...")
        self.gpu_bar = self.create_bar()

        self.update_all_stats()

    def create_label(self, text):
        label = tk.Label(self.root, text=text, font=("Arial", 12), 
                        bg="#1e1e2e", fg="#bac2de")
        label.pack(pady=5, anchor="w", padx=35)
        return label

    def create_bar(self):
        bar = ttk.Progressbar(self.root, length=380, mode='determinate', 
                             style="Custom.Horizontal.TProgressbar")
        bar.pack(pady=5, padx=35)
        return bar

    def clear_cache(self):
        try:
            subprocess.run("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches", 
                           shell=True, check=True)
            messagebox.showinfo("Success", "System Cache Cleared Successfully!")
        except Exception:
            messagebox.showwarning("Permission Denied", "Root privileges (sudo) required to clear cache.")

    def get_gpu_usage(self):
        # 1. Check for NVIDIA using gputil
        if HAS_GPUTIL:
            try:
                gpus = gputil.getGPUs()
                if gpus:
                    return gpus[0].load * 100
            except:
                pass

        # 2. Check for Intel/AMD via Sysfs (Linux standard)
        # Search for usage percentage in common system paths
        paths = [
            "/sys/class/drm/card0/device/gpu_busy_percent", # Common for AMD
            "/sys/class/drm/card1/device/gpu_busy_percent",
            "/sys/kernel/debug/dri/0/i915_drpc_info"        # Intel specific (sometimes requires root)
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        content = f.read()
                        # Extract number if file contains text
                        match = re.search(r"(\d+)", content)
                        if match:
                            return float(match.group(1))
                except:
                    continue
        
        # 3. Last resort: Try to use 'intel_gpu_top' or similar if installed (optional)
        return 0.0

    def update_all_stats(self):
        # CPU & RAM
        cpu_val = psutil.cpu_percent()
        ram_val = psutil.virtual_memory().percent
        
        self.cpu_bar['value'] = cpu_val
        self.cpu_label.config(text=f"CPU Usage: {cpu_val}%")
        
        self.ram_bar['value'] = ram_val
        self.ram_label.config(text=f"RAM Usage: {ram_val}%")

        # GPU
        gpu_val = self.get_gpu_usage()
        self.gpu_bar['value'] = gpu_val
        self.gpu_label.config(text=f"GPU Usage: {gpu_val:.1f}%")

        self.root.after(1000, self.update_all_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = MaxelOSMonitor(root)
    root.mainloop()
