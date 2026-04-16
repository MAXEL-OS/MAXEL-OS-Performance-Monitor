# --------------------------------------------------------
# PROJECT: MAXEL-OS
# AUTHOR: MAXEL-OS 
# COPYRIGHT: (C) 2026 MAXEL-OS. ALL RIGHTS RESERVED.
# --------------------------------------------------------

#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import os
import subprocess
import re

try:
    import gputil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

class MaxelMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("MAXEL-OS Resource Monitor")
        self.root.geometry("450x500")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar", 
                        troughcolor='#313244', 
                        background='#89b4fa', 
                        thickness=20)

        tk.Label(self.root, text="MAXEL-OS Performance", font=("Arial", 18, "bold"), 
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=25)

        # CPU Section
        self.cpu_label = self.create_label("CPU Usage: 0%")
        self.cpu_bar = self.create_bar()

        # RAM Section with Clear Cache Button
        ram_frame = tk.Frame(self.root, bg="#1e1e2e")
        ram_frame.pack(fill="x", padx=35, pady=5)
        self.ram_label = tk.Label(ram_frame, text="RAM Usage: 0%", font=("Arial", 12), 
                                 bg="#1e1e2e", fg="#bac2de")
        self.ram_label.pack(side="left")
        
        self.clear_btn = tk.Button(ram_frame, text="Clear Cache", command=self.clear_cache,
                                  font=("Arial", 9, "bold"), bg="#f38ba8", fg="#1e1e2e", 
                                  relief="flat", padx=10, cursor="hand2")
        self.clear_btn.pack(side="right")
        self.ram_bar = self.create_bar()

        # GPU Section
        self.gpu_label = self.create_label("GPU Usage: Detecting...")
        self.gpu_bar = self.create_bar()

        self.refresh_stats()

    def create_label(self, text):
        label = tk.Label(self.root, text=text, font=("Arial", 12), bg="#1e1e2e", fg="#bac2de")
        label.pack(pady=5, anchor="w", padx=35)
        return label

    def create_bar(self):
        bar = ttk.Progressbar(self.root, length=380, mode='determinate', style="Custom.Horizontal.TProgressbar")
        bar.pack(pady=5, padx=35)
        return bar

    def clear_cache(self):
        try:
            # Running with NOPASSWD support
            subprocess.run(["sudo", "sh", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"], check=True)
            messagebox.showinfo("MAXEL-OS", "Cache cleared successfully!")
        except:
            messagebox.showwarning("Permission Error", "Please configure sudoers for passwordless clearing.")

    def get_gpu_usage(self):
        if HAS_GPUTIL:
            try:
                gpus = gputil.getGPUs()
                if gpus: return gpus[0].load * 100
            except: pass
        
        for i in range(2):
            path = f"/sys/class/drm/card{i}/device/gpu_busy_percent"
            if os.path.exists(path):
                try:
                    with open(path, "r") as f: return float(f.read().strip())
                except: continue
        return 0.0

    def refresh_stats(self):
        c, r = psutil.cpu_percent(), psutil.virtual_memory().percent
        g = self.get_gpu_usage()
        self.cpu_bar['value'], self.ram_bar['value'], self.gpu_bar['value'] = c, r, g
        self.cpu_label.config(text=f"CPU Usage: {c}%")
        self.ram_label.config(text=f"RAM Usage: {r}%")
        self.gpu_label.config(text=f"GPU Usage: {g:.1f}%")
        self.root.after(1000, self.refresh_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = MaxelMonitor(root)
    root.mainloop()
