# 🍎 Free Fall Experiment Module with Arduino & Python

![Project Status](https://img.shields.io/badge/Status-Complete-green)
![Platform](https://img.shields.io/badge/Platform-Arduino%20Nano-blue)
![Language](https://img.shields.io/badge/Language-C%2B%2B%20%7C%20Python-orange)

## 📖 Overview
This project is an automated system designed to calculate the gravitational acceleration constant ($g$) with high precision. It consists of an Embedded Firmware module (Arduino Nano) that controls an electromagnet and captures sensor timing, and a Desktop GUI(Python) that visualizes the drop data in real-time and performs curve fitting to determine gravity.

The system replaces manual stopwatches with microsecond-level timing using direct AVR Timer1 register manipulation.

## 🚀 Features
* **Precision Timing:** Uses ATmega328P **Timer1 (16-bit)** with direct register access (ISR) for microsecond accuracy.
* **Automated Control:** Electromagnet release is triggered via Serial command.
* **Real-time Dashboard:** Python (Tkinter) application displays sensor logs and plots Position vs. Time.
* **Data Analysis:** Automatic curve fitting using `scipy.optimize` to calculate $g$.
* **Simulation Ready:** Full support for Proteus simulation.

## 📸 Screenshots

Python Interface
![Python Interface](documentation/python_interface.png)

Proteus Simulation
![Proteus Simulation](documentation/proteus_simulation.png)

## 🛠️ Hardware & Pinout

**Microcontroller:** Arduino Nano (ATmega328P)

| Component | Pin Name | Arduino Pin | Description |
| :--- | :--- | :--- | :--- |
| **Magnet** | PD6 | D6 | Controls the electromagnet (Active LOW/HIGH configured in code) |
| **Sensors** | PD3 / INT1 | D3 | Connected to Sensor Array (Falling Edge Trigger) |
| **Serial RX** | PD0 | RX | USB Communication |
| **Serial TX** | PD1 | TX | USB Communication |

## 💻 Tech Stack
* **Firmware:** C++ (PlatformIO / AVR-GCC)
* **Desktop App:** Python 3.10+
    * `tkinter` (UI)
    * `matplotlib` (Graphing)
    * `scipy` & `numpy` (Physics Math)
    * `pyserial` (Communication)
* **Simulation:** Proteus 8 Professional

## ⚙️ Installation & Usage

### 1. Firmware (PlatformIO)
1.  Open the project folder in **VS Code**.
2.  Ensure **PlatformIO** extension is installed.
3.  Connect your Arduino Nano.
4.  Click the **PlatformIO: Upload** button (Arrow icon).

### 2. Python Application
Ensure you have Python installed, then install the dependencies:
```bash
pip install numpy matplotlib scipy pyserial
```
After all library installed, you can run the python interface file and connect the port used for simulation and run the simulation.

### 3. Proteus Simulation Setup
1.  Open the `.pdsprj` file in the `proteus/` folder.
2.  Double-click the Arduino component.
3.  **Load Firmware:** Browse to `.pio/build/nanoatmega328/firmware.hex`.
4.  **CRITICAL SETTINGS:**
    * Set **CKSEL Fuses** to: `(1111) Ext. Crystal 8.0- MHz`
    * Set **Clock Frequency** to: `16MHz`
5.  Run the simulation.
6.  If you want to connect the proteus simulation with the python interface serial, add compim components for virtual communication.

## 🐛 Troubleshooting
* **Garbage Data in Serial?** Ensure both the code and the Serial Monitor/Proteus Terminal are set to **57600 baud**.
* **Simulation Too Slow?** Check that the Proteus processor clock frequency is manually typed as `16MHz` (default is often 1MHz).
* **Python Can't Connect?** Close any other software (like Arduino IDE Serial Monitor) that might be using the COM port.

---
*Created by Steven Wijaya*