import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import curve_fit

SENSOR_SPACING = 0.10 

FONT_UI_MAIN = ("Segoe UI", 20)       
FONT_UI_BOLD = ("Segoe UI", 20, "bold") 
FONT_LOG_TEXT = ("Segoe UI", 20)      
FONT_RESULT   = ("Segoe UI", 24, "bold") 
GRAPH_TITLE_SIZE = 16
GRAPH_LABEL_SIZE = 14
GRAPH_TICK_SIZE  = 12

class FreeFallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Free Fall Experiment Interface")
        self.root.geometry("1200x850") 

        # --- FORCE BLACK TEXT STYLING ---
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam' allows us to override colors easier
        
        # 1. Force the global foreground (text color) to BLACK
        self.style.configure('.', font=FONT_UI_MAIN, foreground="black", background="#f0f0f0")
        
        # 2. Specifically force standard widgets to be black
        self.style.configure('TLabel', foreground="black", background="#f0f0f0")
        self.style.configure('TButton', foreground="black", background="#e1e1e1")
        self.style.configure('TCombobox', foreground="black", fieldbackground="white", selectbackground="#ccc")
        
        # 3. Force Group Box (LabelFrame) titles to be black
        self.style.configure('TLabelframe', foreground="black", background="#f0f0f0")
        self.style.configure('TLabelframe.Label', font=FONT_UI_BOLD, foreground="black", background="#f0f0f0")

        # Serial Variables
        self.ser = None
        self.is_connected = False
        self.serial_data = []
        self.sensor_positions = []
        
        # Build GUI
        self.create_widgets()
        self.refresh_ports()

    def create_widgets(self):
        # --- Control Panel (Top) ---
        control_frame = ttk.LabelFrame(self.root, text="Connection Settings", padding=15)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)

        # Top container
        top_container = ttk.Frame(control_frame)
        top_container.pack(fill=tk.X)

        ttk.Label(top_container, text="COM Port:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(top_container, textvariable=self.port_var, width=15, state="readonly", font=FONT_UI_MAIN)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        # Force option menu text color for the dropdown list
        self.root.option_add('*TCombobox*Listbox.foreground', 'black')
        # Use a proper tk Font object for the dropdown list to avoid option parsing issues
        combo_list_font = tkfont.Font(family=FONT_UI_MAIN[0], size=FONT_UI_MAIN[1])
        self.root.option_add('*TCombobox*Listbox.font', combo_list_font)
        
        ttk.Button(top_container, text="Refresh", command=self.refresh_ports).pack(side=tk.LEFT, padx=10)
        
        self.btn_connect = ttk.Button(top_container, text="Connect", command=self.toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(top_container, text="Reset / New Run", command=self.reset_data).pack(side=tk.LEFT, padx=30)

        # Status Label
        self.status_var = tk.StringVar(value="Status: Disconnected")
        self.lbl_status = ttk.Label(top_container, textvariable=self.status_var, font=FONT_UI_BOLD)
        self.lbl_status.pack(side=tk.RIGHT, padx=10)
        # Manually set red/black logic later, but start black-compatible

        # --- Main Content Area ---
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Left: Data Log
        log_frame = ttk.LabelFrame(content_frame, text="Sensor Log (µs)", width=300)
        log_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # FORCE Black text on the log box (fg="black")
        self.txt_log = tk.Text(log_frame, width=20, height=20, state='disabled', font=FONT_LOG_TEXT, fg="black", bg="white")
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Right: Graph
        graph_frame = ttk.LabelFrame(content_frame, text="Position vs Time Analysis")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.style_plot_initial()

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Results Label - FORCE Black
        self.result_var = tk.StringVar(value="Waiting for drop...")
        self.lbl_result = ttk.Label(graph_frame, textvariable=self.result_var, font=FONT_RESULT, foreground="black")
        self.lbl_result.pack(pady=15)

    def style_plot_initial(self):
        # Force Matplotlib text to be black
        self.ax.set_title("Waiting for Data...", fontsize=GRAPH_TITLE_SIZE, color='black')
        self.ax.set_xlabel("Time (s)", fontsize=GRAPH_LABEL_SIZE, color='black')
        self.ax.set_ylabel("Position (m)", fontsize=GRAPH_LABEL_SIZE, color='black')
        self.ax.tick_params(axis='both', which='major', labelsize=GRAPH_TICK_SIZE, labelcolor='black')
        self.ax.grid(True)
        self.figure.tight_layout()

    def update_plot(self):
        t_data = np.array(self.serial_data)
        y_data = np.array(self.sensor_positions)

        self.ax.clear()
        self.ax.grid(True)
        
        self.ax.scatter(t_data, y_data, color='blue', s=80, label='Sensor Data')

        def free_fall_model(t, y0, v0, g):
            return y0 + v0*t + 0.5 * g * t**2

        try:
            popt, _ = curve_fit(free_fall_model, t_data, y_data, p0=[0, 0, 9.8])
            y0_fit, v0_fit, g_fit = popt
            
            t_smooth = np.linspace(min(t_data), max(t_data), 100)
            y_smooth = free_fall_model(t_smooth, *popt)
            
            self.ax.plot(t_smooth, y_smooth, 'r--', linewidth=2.5, label=f'Fit: g={g_fit:.2f}')
            
            self.ax.set_title(f"Analysis (N={len(t_data)})", fontsize=GRAPH_TITLE_SIZE, color='black')
            self.result_var.set(f"Gravity (g): {g_fit:.3f} m/s²")
            
        except Exception as e:
            print(f"Fitting error: {e}")
            self.ax.set_title("Analysis (Insufficient Data)", fontsize=GRAPH_TITLE_SIZE, color='black')

        # Re-apply styling
        self.ax.set_xlabel("Time (s)", fontsize=GRAPH_LABEL_SIZE, color='black')
        self.ax.set_ylabel("Position (m)", fontsize=GRAPH_LABEL_SIZE, color='black')
        self.ax.tick_params(axis='both', which='major', labelsize=GRAPH_TICK_SIZE, labelcolor='black')
        
        # Legend text color
        legend = self.ax.legend(fontsize=GRAPH_TICK_SIZE)
        plt.setp(legend.get_texts(), color='black')
        
        self.canvas.draw()

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combo['values'] = [port.device for port in ports]
        if ports:
            self.port_combo.current(0)

    def toggle_connection(self):
        if not self.is_connected:
            try:
                port = self.port_var.get()
                self.ser = serial.Serial(port, 115200, timeout=1)
                self.is_connected = True
                self.btn_connect.config(text="Disconnect")
                self.status_var.set(f"Connected: {port}")
                self.lbl_status.config(foreground="green") # Green for connected
                
                self.thread = threading.Thread(target=self.read_serial)
                self.thread.daemon = True
                self.thread.start()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.is_connected = False
            if self.ser: self.ser.close()
            self.btn_connect.config(text="Connect")
            self.status_var.set("Disconnected")
            self.lbl_status.config(foreground="red") # Red for disconnected

    def reset_data(self):
        self.serial_data = []
        self.sensor_positions = []
        self.txt_log.config(state='normal')
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state='disabled')
        self.result_var.set("Ready for new drop...")
        
        self.ax.clear()
        self.style_plot_initial()
        self.canvas.draw()
        if self.is_connected:
            try: self.ser.write(b'R') 
            except: pass

    def read_serial(self):
        while self.is_connected:
            if self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.isdigit():
                        self.process_data(int(line))
                except Exception as e:
                    print(f"Serial Error: {e}")

    def process_data(self, micros_time):
        self.root.after(0, self._update_log, micros_time)

    def _update_log(self, micros_time):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, f"{micros_time} µs\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

        if not self.serial_data:
            self.start_time = micros_time
            t_seconds = 0.0
        else:
            t_seconds = (micros_time - self.start_time) / 1_000_000.0
        
        self.serial_data.append(t_seconds)
        current_pos = (len(self.serial_data) - 1) * SENSOR_SPACING
        self.sensor_positions.append(current_pos)

        if len(self.serial_data) >= 3:
            self.update_plot()

if __name__ == "__main__":
    root = tk.Tk()
    # High-DPI Fix
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = FreeFallApp(root)
    root.mainloop()