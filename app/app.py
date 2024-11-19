import serial
import json
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import tkinter as tk
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Set up the serial connection (change COM3 to your Arduino's port)
SERIAL_PORT = '/dev/ttyUSB0'  # Use '/dev/ttyUSB0' for Linux or '/dev/ttyACM0' for Mac
BAUD_RATE = 9600

# Initialize the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)  # Wait for the connection to establish

# Lists to store data
gyro_x_data = []
gyro_y_data = []
gyro_z_data = []
time_data = []

class GyroscopeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Gyroscope Data")

        # Create the figure and subplot
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(121, projection='3d')
        self.plot_ax = self.fig.add_subplot(122)

        # Set up the 3D plot
        self.rocket = self.ax.plot([0], [0], [0], 'ro-', markersize=10, linewidth=2)[0]
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Rocket Animation')

        # Set up the plots
        self.plot_ax.set_title('Gyroscope Data')
        self.plot_ax.set_xlabel('Time (s)')
        self.plot_ax.set_ylabel('Gyro (degrees/s)')
        self.line_x, = self.plot_ax.plot([], [], 'r-', label='Gyro X')
        self.line_y, = self.plot_ax.plot([], [], 'g-', label='Gyro Y')
        self.line_z, = self.plot_ax.plot([], [], 'b-', label='Gyro Z')
        self.plot_ax.legend()

        # Create the Tkinter canvas and add the figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # Create the start and stop buttons
        self.start_button = tk.Button(master, text="Start", command=self.start_program)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_program)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.listen_button = tk.Button(master, text="Listen to Arduino", command=self.listen_to_arduino)
        self.listen_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.is_running = False
        self.ani = None

    def start_program(self):
        self.is_running = True
        self.start_time = time.time()
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100, blit=False)
        self.update_plot()

    def stop_program(self):
        self.is_running = False
        self.ani.event_source.stop()
        ser.close()  # Close the serial connection
        self.master.quit()

    def listen_to_arduino(self):
        if not self.is_running:
            self.start_program()

    def update_plot(self, frame=None):
        if self.is_running:
            try:
                # Read a line from the serial port
                line = ser.readline().decode('utf-8').strip()
                try:
                    # Parse the JSON data
                    data = json.loads(line)
                    gyro_x = data["gyro"]["x"]
                    gyro_y = data["gyro"]["y"]
                    gyro_z = data["gyro"]["z"]
                    current_time = time.time() - self.start_time

                    # Append data to lists
                    gyro_x_data.append(gyro_x)
                    gyro_y_data.append(gyro_y)
                    gyro_z_data.append(gyro_z)
                    time_data.append(current_time)

                    # Update the plots
                    self.plot_ax.set_xlim(0, max(10, current_time))  # Keep the x-axis fixed to the last 10 seconds
                    self.plot_ax.set_ylim(min(-20, min(gyro_x_data + gyro_y_data + gyro_z_data)) - 10, 
                                         max(20, max(gyro_x_data + gyro_y_data + gyro_z_data)) + 10)  # Adjust y-axis limits
                    self.line_x.set_data(time_data, gyro_x_data)
                    self.line_y.set_data(time_data, gyro_y_data)
                    self.line_z.set_data(time_data, gyro_z_data)

                    # Update the 3D rocket animation
                    self.rocket.set_data([gyro_x / 10, gyro_y / 10], [gyro_y / 10, -gyro_x / 10])
                    self.rocket.set_3d_properties(gyro_z / 10)

                    self.canvas.draw()

                except json.JSONDecodeError:
                    # Handle JSON parsing errors
                    print("Failed to decode JSON:", line)

            except KeyboardInterrupt:
                print("Exiting...")
                self.ani.event_source.stop()
                ser.close()  # Close the serial connection
                self.master.quit()

        return self.line_x, self.line_y, self.line_z, self.rocket

root = tk.Tk()
app = GyroscopeGUI(root)
root.mainloop()