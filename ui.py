import tkinter
import tkinter.messagebox
import customtkinter
import ikpy.chain
import ikpy.utils.plot as plot_utils
import numpy as np
import math
import serial
import time
# matplotlib widget
import matplotlib.pyplot as plt
import uuid
import threading
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2 as cv
from PIL import Image,ImageTk



customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.index = 1
        self.robot_axis_positions = [ 0.0, -55.0, -87.0, 0.0, 0.0, 0.0 ]
        self.current_speed = 30.0
        self.gripper_current_steps = 0.0
        self.gripper_reset_steps = 0.0
        self.commands = []
        self.controlIds = []
        self.command_index_textbox = []
        self.command_command_textbox = []
        self.command_init_speed_textbox = []
        self.command_init_speed_textbox = []
        self.command_final_speed_textbox = []
        self.command_execute_button = []
        self.command_copy_button = []
        self.command_replace_button = []
        self.command_delete_button = []
        self.stop = False
        self.start = False
        self.vision_capture = None
        self.vision_aruco_dict = None
        self.vision_aruco_params = None
        self.vision_aruco_detector = None
        self.vision_current_frame = None
        self.vision_preprocess_frame = None
        self.vision_output = []
        self.vision_start = False
        self.vision_zoom_value = 50
        self.vision_start_calibrate = False
        self.vision_calibrate_xy = [0, 0, 0 ,0] # (x1, y1, x2, y2)
        self.vision_pixel_to_cm_ratio = 1
        self.vision_robot_calibrate_xyz = [0, 0, 0, 0, 0] # (x1, y1, x2, y2, z)
        self.vision_brightness_value = 255
        self.vision_contrast_value = 127
        self.vision_width = 640
        self.vision_height = 480
        self.vision_mask_temp_value = [[0,0], [0,0]]
        self.vision_mask_value = [[0, 0], [self.vision_width, self.vision_height]]
        self.vision_mask_drawing = False
        self.vision_mask_frame = None
        self.vision_min_contour_area = 500
        self.vision_max_contour_area = 100000
        self.vision_objects = []
        self.gripper_steps_to_mm = 30 # steps per MM

        
        self.title("Robot Arm Controller")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        
        # configure grid layout (4x4)
        # self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=0)
        # self.grid_rowconfigure((0, 1, 2), weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tabView = customtkinter.CTkTabview(self)
        self.tabView.grid(row=0, padx=10, pady=10, sticky="nsew")
        self.controller_tab = self.tabView.add("Controller")
        
        
        self.vision_tab = self.tabView.add("Vision")


        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self.controller_tab, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        
    
        #connect robot input and button
        self.connect_label = customtkinter.CTkLabel(self.sidebar_frame, text="Robot port:", anchor="w") #font=customtkinter.CTkFont(size=12, weight="bold")
        self.connect_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.connect_status_label = customtkinter.CTkLabel(self.sidebar_frame, text="NOT CONNECTED", anchor="w") #font=customtkinter.CTkFont(size=12, weight="bold")
        self.connect_status_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.port_textbox = customtkinter.CTkEntry(self.sidebar_frame)
        self.port_textbox.grid(row=2, column=0, padx=20, pady=(10, 0),sticky="nsew")
        self.connect_button = customtkinter.CTkButton(self.sidebar_frame, text="Connect",  command=self.connect_robot)
        self.connect_button.grid(row=3, column=0, padx=20, pady=10)
        
        
        #save/open file input and button
        self.connect_label = customtkinter.CTkLabel(self.sidebar_frame, text="File:", anchor="w") #font=customtkinter.CTkFont(size=12, weight="bold")
        self.connect_label.grid(row=4, column=0, padx=20, pady=(10, 0))
        self.textbox_file = customtkinter.CTkEntry(self.sidebar_frame)
        self.textbox_file.grid(row=5, column=0, padx=20, pady=(10, 0),sticky="nsew")
        self.open_file_button = customtkinter.CTkButton(self.sidebar_frame, text="Open", command=self.load_commands)
        self.open_file_button.grid(row=6, column=0, padx=20, pady=10)
        self.save_file_button = customtkinter.CTkButton(self.sidebar_frame, text="Save", command=self.save_commands)
        self.save_file_button.grid(row=7, column=0, padx=20, pady=10)
        
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=11, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=12, column=0, padx=20, pady=(10, 20))

         # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self.controller_tab, width=800, label_text="Command")
        self.scrollable_frame.grid(row=0, column=1, rowspan=2,  padx=(5,5), pady=(5,5), sticky="nsew")
        # self.scrollable_frame.grid_columnconfigure((0, 1,2, 3), weight=1)

        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=3)
        self.scrollable_frame.grid_columnconfigure(2, weight=1)
        self.scrollable_frame.grid_columnconfigure(3, weight=1)
        self.scrollable_frame.grid_columnconfigure(4, weight=1)
        self.scrollable_frame.grid_columnconfigure(5, weight=1)
        self.scrollable_frame.grid_columnconfigure(6, weight=1)
        self.scrollable_frame.grid_columnconfigure(7, weight=1)
        
    
        self.scrollable_button_frame = customtkinter.CTkFrame(self.scrollable_frame, width=140, corner_radius=0)
        self.scrollable_button_frame.grid(row=0, column=0, columnspan=8,  padx=5, pady=5, sticky="nsew")

        self.execute_all_button = customtkinter.CTkButton(self.scrollable_button_frame, text="Execute All", command=self.start_execute_all)
        self.execute_all_button.grid(row=0, column=0,  padx=10, pady=10)
        self.execute_stop_button = customtkinter.CTkButton(self.scrollable_button_frame, text="STOP!!", command=self.command_stop_all)
        self.execute_stop_button.grid(row=0, column=1,  padx=10, pady=10)
        
        self.index_label = customtkinter.CTkLabel(self.scrollable_frame, width=50, text="Index")
        self.index_label.grid(row=1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.command_label = customtkinter.CTkLabel(self.scrollable_frame, text="Command")
        self.command_label.grid(row=1, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.init_speed = customtkinter.CTkLabel(self.scrollable_frame, text="Init Speed")
        self.init_speed.grid(row=1, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.final_speed = customtkinter.CTkLabel(self.scrollable_frame, text="Final Speed")
        self.final_speed.grid(row=1, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        self.plot_frame = customtkinter.CTkFrame(self.controller_tab, width=140, corner_radius=0)
        self.plot_frame.grid(row=2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, uniform=1)
 
        
        self.index = 2
        
    
        
        # for i in range(100):
        #     switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"CTkSwitch {i}")
        #     switch.grid(row=i, column=0, padx=10, pady=(0, 20))
        #     self.scrollable_frame_switches.append(switch)
        
        # job frame - buttons
        self.jog_frame = customtkinter.CTkFrame(self.controller_tab, corner_radius=0)
        self.jog_frame.grid(row=0, column=3, rowspan=6, padx=(10, 20), pady=(10, 20), sticky="nsew")
        self.jog_frame.grid_columnconfigure(4, weight=4)
        
 
        
        
        self.jog_frame_lable = customtkinter.CTkLabel(self.jog_frame, text="Robot Positions")
        self.jog_frame_lable.grid(row=0, column=0, columnspan=7, padx=20, pady=20, sticky="nsew")
        
        
        #axis 1:
        self.axis1_lable = customtkinter.CTkLabel(self.jog_frame, text="axis 1:")
        self.axis1_lable.grid(row=1, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axis1_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-", command=self.on_minus_axis1)
        self.axis1_minus_button.grid(row=1, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis1_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+", command=self.on_add_axis1)
        self.axis1_add_button.grid(row=1, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis1_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axis1_add_textbox.grid(row=1, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis1_add_textbox.insert(0, 10)
        self.axis1_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_axis1_changed)
        self.axis1_slider.grid(row=1, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        
        self.axis1_pos_lable = customtkinter.CTkLabel(self.jog_frame, text=self.axis1_slider.get())
        self.axis1_pos_lable.grid(row=1, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        
        
        #axis 2:
        self.axis2_lable = customtkinter.CTkLabel(self.jog_frame, text="axis 2:")
        self.axis2_lable.grid(row=2, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axis2_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_axis2)
        self.axis2_minus_button.grid(row=2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis2_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_axis2)
        self.axis2_add_button.grid(row=2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis2_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axis2_add_textbox.grid(row=2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis2_add_textbox.insert(0, 10)
        self.axis2_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180, to=180, command=self.on_axis2_changed)
        self.axis2_slider.grid(row=2, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axis2_pos_lable = customtkinter.CTkLabel(self.jog_frame, width=50, text="0.0")
        self.axis2_pos_lable.grid(row=2, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        #axis 3:
        self.axis3_lable = customtkinter.CTkLabel(self.jog_frame, text="axis 3:")
        self.axis3_lable.grid(row=3, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axis3_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_axis3)
        self.axis3_minus_button.grid(row=3, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis3_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_axis3)
        self.axis3_add_button.grid(row=3, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis3_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axis3_add_textbox.grid(row=3, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis3_add_textbox.insert(0, 10)
        self.axis3_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_axis3_changed)
        self.axis3_slider.grid(row=3, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axis3_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axis3_pos_lable.grid(row=3, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        #axis 4:
        self.axis4_lable = customtkinter.CTkLabel(self.jog_frame, text="axis 4:")
        self.axis4_lable.grid(row=4, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axis4_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_axis4)
        self.axis4_minus_button.grid(row=4, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis4_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_axis4)
        self.axis4_add_button.grid(row=4, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis4_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axis4_add_textbox.grid(row=4, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis4_add_textbox.insert(0, 10)
        self.axis4_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_axis4_changed)
        self.axis4_slider.grid(row=4, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axis4_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axis4_pos_lable.grid(row=4, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        #axis 5:
        self.axis5_lable = customtkinter.CTkLabel(self.jog_frame, text="axis 5:")
        self.axis5_lable.grid(row=5, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axis5_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_axis5)
        self.axis5_minus_button.grid(row=5, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis5_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_axis5)
        self.axis5_add_button.grid(row=5, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis5_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axis5_add_textbox.grid(row=5, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis5_add_textbox.insert(0, 10)
        self.axis5_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_axis5_changed)
        self.axis5_slider.grid(row=5, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axis5_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axis5_pos_lable.grid(row=5, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        #axis 6:
        self.axis6_lable = customtkinter.CTkLabel(self.jog_frame, text="axis 6:")
        self.axis6_lable.grid(row=6, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axis6_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_axis6)
        self.axis6_minus_button.grid(row=6, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis6_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_axis6)
        self.axis6_add_button.grid(row=6, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis6_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axis6_add_textbox.grid(row=6, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axis6_add_textbox.insert(0, 10)
        self.axis6_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_axis6_changed)
        self.axis6_slider.grid(row=6, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axis6_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axis6_pos_lable.grid(row=6, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        #X:
        self.axisX_lable = customtkinter.CTkLabel(self.jog_frame, text="X:")
        self.axisX_lable.grid(row=8, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axisX_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-", command=self.on_minus_x)
        self.axisX_minus_button.grid(row=8, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisX_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+", command=self.on_add_x)
        self.axisX_add_button.grid(row=8, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisX_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axisX_add_textbox.grid(row=8, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisX_add_textbox.insert(0, 10)
        self.axisX_slider = customtkinter.CTkSlider(self.jog_frame, from_=-800.0, to=800.0,command=self.on_x_changed)
        self.axisX_slider.grid(row=8, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axisX_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axisX_pos_lable.grid(row=8, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        #Y:
        self.axisY_lable = customtkinter.CTkLabel(self.jog_frame, text="Y:")
        self.axisY_lable.grid(row=9, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axisY_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-", command=self.on_minus_y)
        self.axisY_minus_button.grid(row=9, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.axisY_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_y)
        self.axisY_add_button.grid(row=9, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisY_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axisY_add_textbox.grid(row=9, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisY_add_textbox.insert(0, 10)
        self.axisY_slider = customtkinter.CTkSlider(self.jog_frame, from_=-800.0, to=800.0,command=self.on_y_changed)
        self.axisY_slider.grid(row=9, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axisY_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axisY_pos_lable.grid(row=9, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        
        #Z:
        self.axisZ_lable = customtkinter.CTkLabel(self.jog_frame, text="Z:")
        self.axisZ_lable.grid(row=10, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axisZ_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_z)
        self.axisZ_minus_button.grid(row=10, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisZ_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_z)
        self.axisZ_add_button.grid(row=10, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisZ_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axisZ_add_textbox.grid(row=10, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisZ_add_textbox.insert(0, 10)

        self.axisZ_slider = customtkinter.CTkSlider(self.jog_frame, from_=-800.0, to=800.0,command=self.on_z_changed)
        self.axisZ_slider.grid(row=10, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axisZ_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axisZ_pos_lable.grid(row=10, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        
        #RX:
        self.axisRX_lable = customtkinter.CTkLabel(self.jog_frame, text="RX:")
        self.axisRX_lable.grid(row=11, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axisRX_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_rx)
        self.axisRX_minus_button.grid(row=11, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.axisRX_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_rx)
        self.axisRX_add_button.grid(row=11, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisRX_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axisRX_add_textbox.grid(row=11, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisRX_add_textbox.insert(0, 10)
        self.axisRX_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_rx_changed)
        self.axisRX_slider.grid(row=11, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axisRX_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axisRX_pos_lable.grid(row=11, column=5, padx=(5,5), pady=(5,5), sticky="nsew")

        
        
        #PY:
        self.axisPY_lable = customtkinter.CTkLabel(self.jog_frame, text="PY:")
        self.axisPY_lable.grid(row=12, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axisPY_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-", command=self.on_minus_py)
        self.axisPY_minus_button.grid(row=12, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.axisPY_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+", command=self.on_add_py)
        self.axisPY_add_button.grid(row=12, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisPY_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axisPY_add_textbox.grid(row=12, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisPY_add_textbox.insert(0, 10)
        self.axisPY_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_py_changed)
        self.axisPY_slider.grid(row=12, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axisPY_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axisPY_pos_lable.grid(row=12, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        
        #YZ:
        self.axisYZ_lable = customtkinter.CTkLabel(self.jog_frame, text="YZ:")
        self.axisYZ_lable.grid(row=13, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        self.axisYZ_minus_button = customtkinter.CTkButton(self.jog_frame, width=50, text="-",command=self.on_minus_yz)
        self.axisYZ_minus_button.grid(row=13, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.axisYZ_add_button = customtkinter.CTkButton(self.jog_frame,  width=50, text="+",command=self.on_add_yz)
        self.axisYZ_add_button.grid(row=13, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisYZ_add_textbox = customtkinter.CTkEntry(self.jog_frame,width=40)
        self.axisYZ_add_textbox.grid(row=13, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.axisYZ_add_textbox.insert(0, 10)
        self.axisYZ_slider = customtkinter.CTkSlider(self.jog_frame, from_=-180.0, to=180.0, command=self.on_yz_changed)
        self.axisYZ_slider.grid(row=13, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.axisYZ_pos_lable = customtkinter.CTkLabel(self.jog_frame, text="0.0")
        self.axisYZ_pos_lable.grid(row=13, column=5, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        #init frame
        self.init_frame = customtkinter.CTkFrame(self.jog_frame, corner_radius=0, bg_color="transparent")
        self.init_frame.grid(row=14, column=0, columnspan=6, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.go_init_button = customtkinter.CTkButton(self.init_frame,   text="GO INIT", command=self.on_init)
        self.go_init_button.grid(row=0, column=0,  padx=5, pady=5, sticky="nsew")
    
    
        self.go_home_button = customtkinter.CTkButton(self.init_frame,   text="GO HOME", command=self.on_home)
        self.go_home_button.grid(row=0, column=1,  padx=5, pady=5, sticky="nsew")
        
        self.show_plot_checkbox = customtkinter.CTkCheckBox(self.init_frame,   text="Show Plot")
        self.show_plot_checkbox.grid(row=0, column=2,  padx=5, pady=5, sticky="nsew")
        self.show_plot_checkbox.select()
        
        self.send_to_robot_checkbox = customtkinter.CTkCheckBox(self.init_frame,   text="Send to Robot")
        self.send_to_robot_checkbox.grid(row=0, column=3,  padx=5, pady=5, sticky="nsew")
        self.send_to_robot_checkbox.select()
        
        
        #command tab
        self.commandsTabView = customtkinter.CTkTabview(self.init_frame)
        self.commandsTabView.grid(row=1, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.command_robot_tab = self.commandsTabView.add("Robot Commands")
        self.command_vision_tab = self.commandsTabView.add("Vision Commands")



        
        self.speed_label = customtkinter.CTkLabel(self.command_robot_tab, text="Speed")
        self.speed_label.grid(row=0, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.speed_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.speed_textbox.grid(row=1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.speed_textbox.insert(0, self.current_speed)
        
        self.speed_button = customtkinter.CTkButton(self.command_robot_tab,  width=50, text="SET SPEED" , command=self.set_speed)
        self.speed_button.grid(row=1, column=1,  padx=5, pady=5, sticky="nsew")
        
        
        # gripper frame
        # self.gripper_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        # self.gripper_frame.grid(row=4, column=1,  sticky="nsew")
        
        self.gripper_step_label = customtkinter.CTkLabel(self.command_robot_tab, text="Steps")
        self.gripper_step_label.grid(row=2, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.gripper_step_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.gripper_step_textbox.grid(row=3, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.gripper_step_textbox.insert(0, self.gripper_current_steps)
        
        self.gripper_step_button = customtkinter.CTkButton(self.command_robot_tab,  width=50, text="SET GRIPPER" , command=self.set_gripper)
        self.gripper_step_button.grid(row=3, column=1,  padx=5, pady=5, sticky="nsew")
        
        self.gripper_reset_label = customtkinter.CTkLabel(self.command_robot_tab, text="Reset Steps")
        self.gripper_reset_label.grid(row=2, column=2, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.gripper_reset_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.gripper_reset_textbox.grid(row=3, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.gripper_reset_textbox.insert(0, self.gripper_reset_steps)
        
        self.gripper_reset_button = customtkinter.CTkButton(self.command_robot_tab,  width=50, text="RESET GRIPPER" , command=self.reset_gripper)
        self.gripper_reset_button.grid(row=3, column=3,  padx=5, pady=5, sticky="nsew")
        
        
        
        self.add_command_index_label = customtkinter.CTkLabel(self.command_robot_tab, text="Index")
        self.add_command_index_label.grid(row=4, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.add_command_initspeed_label = customtkinter.CTkLabel(self.command_robot_tab, text="Init Speed")
        self.add_command_initspeed_label.grid(row=4, column=1, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.add_command_finspeed_label = customtkinter.CTkLabel(self.command_robot_tab, text="Finish Speed")
        self.add_command_finspeed_label.grid(row=4, column=2, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.add_command_index_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.add_command_index_textbox.grid(row=5, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.add_command_index_textbox.insert(0, 0)
        self.add_command_initspeed_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.add_command_initspeed_textbox.grid(row=5, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.add_command_initspeed_textbox.insert(0, 0.0)
        self.add_command_finspeed_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.add_command_finspeed_textbox.grid(row=5, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.add_command_finspeed_textbox.insert(0, 0.0)
        self.add_command_button = customtkinter.CTkButton(self.command_robot_tab,  width=50, text="ADD COMMAND" , command=self.add_command)
        self.add_command_button.grid(row=5, column=3,  padx=5, pady=5, sticky="nsew")
        
        
        
        # gripper command frame
        # self.gripper_command_frame = customtkinter.CTkFrame(self, corner_radius=0, bg_color="transparent")
        # self.gripper_command_frame.grid(row=6, column=1,  sticky="nsew")
        # self.add_command_frame.grid_rowconfigure(7, weight=1)
        
        
        self.gripper_command_index_label = customtkinter.CTkLabel(self.command_robot_tab, text="Index")
        self.gripper_command_index_label.grid(row=6, column=0, padx=(5,5), pady=(5,5), sticky="nsew")
        
        self.gripper_command_steps_label = customtkinter.CTkLabel(self.command_robot_tab, text="Steps")
        self.gripper_command_steps_label.grid(row=6, column=1, padx=(5,5), pady=(5,5), sticky="nsew")
        
        
        self.gripper_command_index_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.gripper_command_index_textbox.grid(row=7, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.gripper_command_index_textbox.insert(0, 0)
        
        self.gripper_command_steps_textbox = customtkinter.CTkEntry(self.command_robot_tab,width=40)
        self.gripper_command_steps_textbox.grid(row=7, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.gripper_command_steps_textbox.insert(0, 0.0)
        self.gripper_command_button = customtkinter.CTkButton(self.command_robot_tab,  width=50, text="ADD GRIPPER COMMAND" , command=self.add_gripper_command)
        self.gripper_command_button.grid(row=7, column=2,  padx=5, pady=5, sticky="nsew")
        
        #vision command tab

        self.command_vision_capture_index_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_capture_index_textbox.grid(row=0, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_capture_index_textbox.insert(0, 0)
        self.command_vision_capture = customtkinter.CTkButton(self.command_vision_tab,  width=50, text="VISION CAPTURE" , command=self.add_vision_capture_command)
        self.command_vision_capture.grid(row=0, column=1,  padx=5, pady=5, sticky="nsew")


        self.command_vision_movetoxypos_index_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_movetoxypos_index_textbox.grid(row=1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_movetoxypos_index_textbox.insert(0, 0)
        self.command_vision_movetoxypos = customtkinter.CTkButton(self.command_vision_tab,  width=50, text="MOVE TO XY" , command=self.add_vision_moveto_xy)
        self.command_vision_movetoxypos.grid(row=1, column=1,  padx=5, pady=5, sticky="nsew")


        self.command_vision_movetozpos_index_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_movetozpos_index_textbox.grid(row=2, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_movetozpos_index_textbox.insert(0, 0)
        self.command_vision_movetozpos = customtkinter.CTkButton(self.command_vision_tab,  width=50, text="MOVE TO Z" , command=self.add_vision_moveto_z)
        self.command_vision_movetozpos.grid(row=2, column=1,  padx=5, pady=5, sticky="nsew")

        self.command_vision_gripperclose_index_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_gripperclose_index_textbox.grid(row=3, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_gripperclose_index_textbox.insert(0, 0)
        self.command_vision_gripperclose = customtkinter.CTkButton(self.command_vision_tab,  width=50, text="GRIPPER CLOSE" , command=self.add_vision_gripper_close)
        self.command_vision_gripperclose.grid(row=3, column=1,  padx=5, pady=5, sticky="nsew")

        self.command_vision_movebackzpos_index_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_movebackzpos_index_textbox.grid(row=4, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_movebackzpos_index_textbox.insert(0, 0)
        self.command_vision_movebackzpos_mm_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_movebackzpos_mm_textbox.grid(row=4, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_movebackzpos_mm_textbox.insert(0, 100)
        self.command_vision_movebackzpos = customtkinter.CTkButton(self.command_vision_tab,  width=50, text="MOVE BACK Z" , command=self.add_vision_moveback_z)
        self.command_vision_movebackzpos.grid(row=4, column=2,  padx=5, pady=5, sticky="nsew")


        self.command_vision_loop_index_textbox = customtkinter.CTkEntry(self.command_vision_tab,width=40)
        self.command_vision_loop_index_textbox.grid(row=5, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_vision_loop_index_textbox.insert(0, 0)
        self.command_vision_loop = customtkinter.CTkButton(self.command_vision_tab,  width=50, text="LOOP OBJECT" , command=self.add_vision_loop_object)
        self.command_vision_loop.grid(row=5, column=1,  padx=5, pady=5, sticky="nsew")


        img = Image.new('RGB', (self.vision_width, self.vision_height), color = (0,0,0))
        photo_image = ImageTk.PhotoImage(image=img)

        self.vision_tab_frame = customtkinter.CTkFrame(self.vision_tab, corner_radius=0, bg_color="transparent")
        self.vision_tab_frame.grid(row=0, column=0, sticky="nsew")


        self.vision_commands = customtkinter.CTkFrame(self.vision_tab_frame, corner_radius=0)
        self.vision_commands.grid(row=0, column=0, padx=5, pady=5,  sticky="nsew")
        self.vision_commands.columnconfigure(0, weight=1)
        self.vision_commands.columnconfigure(1, weight=2)
        self.vision_commands.columnconfigure(2, weight=1)

        #Camera URL
        self.vision_commands_camera_url_label = customtkinter.CTkLabel(self.vision_commands, text="Camera URL")
        self.vision_commands_camera_url_label.grid(row=0, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_commands_camera_url_textbox = customtkinter.CTkEntry(self.vision_commands)
        self.vision_commands_camera_url_textbox.insert(0, "http://192.168.43.1:8080/video")
        self.vision_commands_camera_url_textbox.grid(row=0, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_commands_camera_url_button = customtkinter.CTkButton(self.vision_commands,   text="CONNECT", command=self.connect_camera)
        self.vision_commands_camera_url_button.grid(row=0, column=2,  padx=5, pady=5, sticky="nsew")

        self.vision_commands_current_frame_button = customtkinter.CTkButton(self.vision_commands,   text="Capture Current Frame", command=self.capture_current_frame)
        self.vision_commands_current_frame_button.grid(row=1, column=0,  padx=5, pady=5, sticky="nsew")

        self.vision_commands_mask_button = customtkinter.CTkButton(self.vision_commands,   text="Start Mask", command=self.vision_mask)
        self.vision_commands_mask_button.grid(row=1, column=1,  padx=5, pady=5, sticky="nsew")

        self.vision_commands_calibrate_button = customtkinter.CTkButton(self.vision_commands,   text="Vision Calibrate", command=self.visual_calibrate)
        self.vision_commands_calibrate_button.grid(row=1, column=2,  padx=5, pady=5, sticky="nsew")

        self.vision_commands_zoom_label = customtkinter.CTkLabel(self.vision_commands, text="Zoom")
        self.vision_commands_zoom_label.grid(row=2, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_commands_zoom_slider = customtkinter.CTkSlider(self.vision_commands, from_=1, to=50, command=self.vision_adjust_zoom)
        self.vision_commands_zoom_slider.set(50)
        self.vision_commands_zoom_slider.grid(row=2, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")

        self.vision_commands_contrast_label = customtkinter.CTkLabel(self.vision_commands, text="Contrast")
        self.vision_commands_contrast_label.grid(row=3, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_commands_contrast_slider = customtkinter.CTkSlider(self.vision_commands, from_=0, to=2 * 127, command=self.vision_adjust_contrast)
        self.vision_commands_contrast_slider.set(50)
        self.vision_commands_contrast_slider.grid(row=3, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")


        self.vision_commands_bright_label = customtkinter.CTkLabel(self.vision_commands, text="Brightness")
        self.vision_commands_bright_label.grid(row=4, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_commands_bright_slider = customtkinter.CTkSlider(self.vision_commands, from_=0, to=2 * 255, command=self.vision_adjust_brightness)
        self.vision_commands_bright_slider.set(127)
        self.vision_commands_bright_slider.grid(row=4, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")


        #Calibration Frame
        self.vision_calibrate_frame = customtkinter.CTkFrame(self.vision_tab_frame, corner_radius=0)
        self.vision_calibrate_frame.grid(row=0, column=1, padx=5, pady=5,  sticky="nsew")
        self.vision_calibrate_frame.columnconfigure(0, weight=1)
        self.vision_calibrate_frame.columnconfigure(1, weight=2)
        self.vision_calibrate_frame.columnconfigure(2, weight=1)
        self.vision_calibrate_frame.columnconfigure(3, weight=2)

        self.vision_calibrate_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Position calibration")
        self.vision_calibrate_label.grid(row=0, column=0, columnspan=4, padx=(5, 5), pady=(5,5), sticky="nsew")


        #Vision
        self.vision_calibrate_vx1_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Vision X1")
        self.vision_calibrate_vx1_label.grid(row=1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_calibrate_vx1_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_vx1_textbox.insert(0, str(self.vision_calibrate_xy[0]))
        self.vision_calibrate_vx1_textbox.grid(row=1, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")

    
        self.vision_calibrate_vy1_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Vision Y1")
        self.vision_calibrate_vy1_label.grid(row=2, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_vy1_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_vy1_textbox.insert(0, str(self.vision_calibrate_xy[1]))
        self.vision_calibrate_vy1_textbox.grid(row=2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")



        self.vision_calibrate_vx2_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Vision X2")
        self.vision_calibrate_vx2_label.grid(row=3, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_vx2_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_vx2_textbox.insert(0, str(self.vision_calibrate_xy[2]))
        self.vision_calibrate_vx2_textbox.grid(row=3, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")


        self.vision_calibrate_vy2_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Vision Y2")
        self.vision_calibrate_vy2_label.grid(row=4, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_vy2_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_vy2_textbox.insert(0, str(self.vision_calibrate_xy[3]))
        self.vision_calibrate_vy2_textbox.grid(row=4, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_calibrate_pcm_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Px To CM Ratio")
        self.vision_calibrate_pcm_label.grid(row=5, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_pcm_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_pcm_textbox.insert(0, str(self.vision_pixel_to_cm_ratio))
        self.vision_calibrate_pcm_textbox.grid(row=5, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_min_contour_area_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Min Contour Are")
        self.vision_min_contour_area_label.grid(row=6, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_min_contour_area_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_min_contour_area_textbox.insert(0, str(self.vision_min_contour_area))
        self.vision_min_contour_area_textbox.grid(row=6, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_max_contour_area_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Max Contour Are")
        self.vision_max_contour_area_label.grid(row=7, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_max_contour_area_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_max_contour_area_textbox.insert(0, str(self.vision_max_contour_area))
        self.vision_max_contour_area_textbox.grid(row=7, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")


        #Robot
        self.vision_calibrate_rx1_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Robot X1")
        self.vision_calibrate_rx1_label.grid(row=1, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_calibrate_rx1_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_rx1_textbox.insert(0, str(self.vision_robot_calibrate_xyz[0]))
        self.vision_calibrate_rx1_textbox.grid(row=1, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")

    
        self.vision_calibrate_ry1_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Robot Y1")
        self.vision_calibrate_ry1_label.grid(row=2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_ry1_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_ry1_textbox.insert(0, str(self.vision_robot_calibrate_xyz[1]))
        self.vision_calibrate_ry1_textbox.grid(row=2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")



        self.vision_calibrate_rx2_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Robot X2")
        self.vision_calibrate_rx2_label.grid(row=3, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_rx2_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_rx2_textbox.insert(0, str(self.vision_robot_calibrate_xyz[2]))
        self.vision_calibrate_rx2_textbox.grid(row=3, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")


        self.vision_calibrate_ry2_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Robot Y2")
        self.vision_calibrate_ry2_label.grid(row=4, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_ry2_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_ry2_textbox.insert(0, str(self.vision_robot_calibrate_xyz[3]))
        self.vision_calibrate_ry2_textbox.grid(row=4, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")


        self.vision_calibrate_rz_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Robot Z")
        self.vision_calibrate_rz_label.grid(row=5, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_rz_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_rz_textbox.insert(0, str(self.vision_robot_calibrate_xyz[4]))
        self.vision_calibrate_rz_textbox.grid(row=5, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")


        self.vision_calibrate_grpper_ratio_label = customtkinter.CTkLabel(self.vision_calibrate_frame, text="Gripper MM Ratio")
        self.vision_calibrate_grpper_ratio_label.grid(row=6, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_calibrate_grpper_ratio_textbox = customtkinter.CTkEntry(self.vision_calibrate_frame)
        self.vision_calibrate_grpper_ratio_textbox.insert(0, str(self.gripper_steps_to_mm))
        self.vision_calibrate_grpper_ratio_textbox.grid(row=6, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_calibrate_robot_button = customtkinter.CTkButton(self.vision_calibrate_frame,   text="Robot Calibrate", command=self.vision_robot_calibrate)
        self.vision_calibrate_robot_button.grid(row=7, column=3,  padx=5, pady=5, sticky="nsew")

        self.vision_calibrate_robot_test_button = customtkinter.CTkButton(self.vision_calibrate_frame,   text="Test Robot", command=self.vision_robot_test)
        self.vision_calibrate_robot_test_button.grid(row=8, column=3,  padx=5, pady=5, sticky="nsew")

        #Camera Output Video
        self.vision_output = customtkinter.CTkFrame(self.vision_tab_frame, corner_radius=0)
        self.vision_output.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")


        self.vision_output_label = customtkinter.CTkLabel(self.vision_output, text="Output")
        self.vision_output_label.grid(row=0, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_output_image = customtkinter.CTkLabel(self.vision_output, text="")
        self.vision_output_image.grid(row=1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_output_image.configure(image=photo_image)
        # self.vision_output_image.bind('<Button-1>', self.visual_calibrate_mouse_event)

        #Camera Live Video
        self.vision_live = customtkinter.CTkFrame(self.vision_tab_frame, corner_radius=0)
        self.vision_live.grid(row=1, column=1,padx=5, pady=5,  sticky="nsew")
        
        self.vision_live_label = customtkinter.CTkLabel(self.vision_live, text="Live")
        self.vision_live_label.grid(row=0, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.vision_live_image = customtkinter.CTkLabel(self.vision_live, text="")
        self.vision_live_image.grid(row=1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.vision_live_image.configure(image=photo_image)

        self.robot = ikpy.chain.Chain.from_urdf_file("/home/maven/robot_arm_ws/src/robot_arm_description/urdf/temp.urdf", active_links_mask=[False, True, True, True, True, True, True])
        
        # print(self.robot.links)
        
        self.doFK()
        self.update_ui()
        self.show_plot()
        
    
    def connect_camera(self):

        if self.vision_start == False:
            self.vision_start = True
            self.vision_commands_camera_url_button.configure(text="STOP")

            self.vision_aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_50)
            self.vision_aruco_params = cv.aruco.DetectorParameters()

            self.vision_aruco_detector = cv.aruco.ArucoDetector(self.vision_aruco_dict, self.vision_aruco_params)

            self.vision_capture = cv.VideoCapture(self.vision_commands_camera_url_textbox.get())
            self.display_live_camera()
        else:
            self.vision_start = False
            self.vision_capture.release()
            self.vision_commands_camera_url_button.configure(text="CONNECT")

    def display_live_camera(self):
        _, self.vision_current_frame = self.vision_capture.read()

        if self.vision_current_frame is not None and self.vision_current_frame.size != 0:

            self.vision_height, self.vision_width, _ = self.vision_current_frame.shape

            converted_img = cv.cvtColor(self.vision_current_frame, cv.COLOR_BGR2RGB)

            img = Image.fromarray(converted_img)
            live_image = ImageTk.PhotoImage(image=img)
            self.vision_live_image.configure(image=live_image)

            if self.vision_start == True:
                self.after(10, self.display_live_camera)

    
    def capture_current_frame(self):
        if self.vision_current_frame is not None and self.vision_current_frame.size != 0:
            self.vision_objects.clear()


            current = self.vision_adjust_brightness_contrast(self.vision_current_frame, self.vision_brightness_value, self.vision_contrast_value)
            gray = cv.cvtColor(current,  cv.COLOR_BGR2GRAY)

            height, width = gray.shape
            centerX, centerY = int(height/2), int(width/2)
            radiusX, radiusY = int(self.vision_zoom_value*height/100), int(self.vision_zoom_value*width/100)

            minX,maxX=centerX-radiusX,centerX+radiusX
            minY,maxY=centerY-radiusY,centerY+radiusY


            
            cropped  = gray[minX:maxX, minY:maxY]
            self.vision_preprocess_frame = cv.resize(cropped, (width, height))

            (corners, ids, rejected)= self.vision_aruco_detector.detectMarkers(self.vision_preprocess_frame)

            if len(corners) > 0:
                # int_corners = np.int0(corners)
                aruco_perimeter = cv.arcLength(corners[0], True)
                self.vision_pixel_to_cm_ratio = aruco_perimeter / 20
                self.vision_calibrate_pcm_textbox.delete(0, len(self.vision_calibrate_pcm_textbox.get()))
                self.vision_calibrate_pcm_textbox.insert(0, self.vision_pixel_to_cm_ratio)

            
            
            

            frame = self.vision_preprocess_frame.copy()

            if self.vision_mask_value is not None and self.vision_mask_value[0][0] > 0 and self.vision_mask_value[0][1] > 0:
                mask = np.zeros_like(frame)
                color = (255, 255, 255)
                mask = cv.rectangle(mask, 
                                    (self.vision_mask_value[0][0], self.vision_mask_value[0][1]), 
                                    (self.vision_mask_value[1][0], self.vision_mask_value[1][1]), color, -1)
                
                frame = cv.bitwise_and(frame, mask)

            blur = cv.GaussianBlur(frame, (5,5), 0)
            _, threshold = cv.threshold(blur, 100, 255, cv.THRESH_BINARY | cv.THRESH_OTSU) 
            # canny = cv.Canny(threshold, 100, 255, 4)
            # kernel = np.ones((5,5), np.uint8)
            # closing = cv.erode(canny, kernel)
            # closing = cv.dilate(closing, kernel)
            # output = cv.morphologyEx(canny, cv.MORPH_OPEN, kernel,iterations=3)            
            contours, _ = cv.findContours(threshold, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
            for i, c in enumerate(contours):
                # Calculate the area of each contour
                area = cv.contourArea(c)
                # print(area)
                # # Ignore contours that are too small or too large
                min_area = int(self.vision_min_contour_area_textbox.get())
                max_area = int(self.vision_max_contour_area_textbox.get())

                if area < min_area and max_area > area:
                    continue
 
                # cv.minAreaRect returns:
                # (center(x, y), (width, height), angle of rotation) = cv2.minAreaRect(c)
                rect = cv.minAreaRect(c)
                rect_fit = cv.fitEllipse(c)
                box = cv.boxPoints(rect)
                box = np.int0(box)

                angle = self.calAngle(box)
 
                pixel_to_cm_ratio = float(self.vision_calibrate_pcm_textbox.get())
                # Retrieve the key parameters of the rotated bounding box
                center = (int(rect[0][0]),int(rect[0][1])) 
                width = round(rect[1][0] / pixel_to_cm_ratio, 1)
                height = round(rect[1][1] / pixel_to_cm_ratio, 1)
                # angle = int(rect_fit[2])
                # deg = int(rect[2])
                # m = cv.moments(c)

                # if (angle > 90):
                #     angle = angle - 90

                vision_object = {
                    "x": center[0],
                    "y": center[1],
                    "height": height,
                    "width": width,
                    "angle": angle
                }
        
                print(vision_object)

                self.vision_objects.append(vision_object);
                # if width < height:
                #     angle = 90 - angle
                # else:
                #     angle = -angle
                label = "H: " + str(height) + "cm, W " + str(width) + "cm, D: " + str(angle)
                cv.putText(frame, label, (center[0]-50, center[1]), 
                cv.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1, cv.LINE_AA)
                cv.circle(frame, center, 3, (255, 0, 255), 2)
                cv.drawContours(frame,[box],0,(0,0,255),2)

            img = Image.fromarray(frame)
            processed_image = ImageTk.PhotoImage(image=img)
            self.vision_output_image.configure(image=processed_image)


    def vision_mask(self):
        try:
            if self.vision_preprocess_frame is not None and self.vision_preprocess_frame.size > 0:
                name = "Mask"
                cv.namedWindow(name)
                cv.setMouseCallback(name, self.vision_mouse_callback)
                cv.imshow(name, self.vision_preprocess_frame)
                cv.waitKey(0)
                cv.destroyAllWindows()
                self.capture_current_frame()

        
        except Exception as error:
            print (error)

    def vision_mouse_callback(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.vision_mask_temp_value[0][0] = x
            self.vision_mask_temp_value[0][1] = y
            self.vision_mask_drawing = True
            
        
        elif event == cv.EVENT_MOUSEMOVE:
            if self.vision_mask_drawing == True:
                img = self.vision_preprocess_frame.copy()
                self.vision_mask_temp_value[1][0] = x
                self.vision_mask_temp_value[1][1] = y
                cv.rectangle(img, (self.vision_mask_temp_value[0][0], self.vision_mask_temp_value[0][1]), 
                            (self.vision_mask_temp_value[1][0], self.vision_mask_temp_value[1][1]), (0, 255, 0), 2)
                
                cv.imshow("Mask", img)
        elif event == cv.EVENT_LBUTTONUP:
            self.vision_mask_drawing = False;
            self.vision_mask_value = self.vision_mask_temp_value.copy()



        # elif event == cv.EVENT_LBUTTONUP:

        #     # cv.destroyWindow("Mask")


    def vision_adjust_zoom(self,value):
        self.vision_zoom_value = int(value)
        self.capture_current_frame()


    def vision_adjust_brightness(self, value):
        self.vision_brightness_value = int(value)
        self.capture_current_frame()

    def vision_adjust_contrast(self, value):
        self.vision_contrast_value = int(value)
        self.capture_current_frame()

    def vision_adjust_brightness_contrast(self, img, brightness=255, contrast=127):
        brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))

        contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))

        if brightness != 0:

            if brightness > 0:

                shadow = brightness

                max = 255

            else:

                shadow = 0
                max = 255 + brightness

            al_pha = (max - shadow) / 255
            ga_mma = shadow

            # The function addWeighted calculates
            # the weighted sum of two arrays
            cal = cv.addWeighted(img, al_pha,
                                img, 0, ga_mma)

        else:
            cal = img

        if contrast != 0:
            Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            Gamma = 127 * (1 - Alpha)

            # The function addWeighted calculates
            # the weighted sum of two arrays
            cal = cv.addWeighted(cal, Alpha,
                                cal, 0, Gamma)


        return cal


    def visual_calibrate(self):
        try:
            if self.vision_preprocess_frame is not None and self.vision_preprocess_frame.size > 0:
                name = "Calibrate"
                cv.namedWindow(name)
                cv.setMouseCallback(name, self.vision_mouse_calibrate_callback)
                cv.imshow(name, self.vision_preprocess_frame)
                cv.waitKey(0)
                cv.destroyAllWindows()
                

        
        except Exception as error:
            print (error)


    def vision_robot_calibrate(self):
        x = self.axisX_slider.get()
        y = self.axisY_slider.get()
        z = self.axisZ_slider.get()


        self.vision_calibrate_rx1_textbox.delete(0, len(self.vision_calibrate_rx1_textbox.get()))
        self.vision_calibrate_rx1_textbox.insert(0, x)

        self.vision_calibrate_ry1_textbox.delete(0, len(self.vision_calibrate_ry1_textbox.get()))
        self.vision_calibrate_ry1_textbox.insert(0, y)

        self.vision_calibrate_rz_textbox.delete(0, len(self.vision_calibrate_rz_textbox.get()))
        self.vision_calibrate_rz_textbox.insert(0, z)


    def vision_mouse_calibrate_callback(self, event, x, y, flags, param):
        
        if event == cv.EVENT_LBUTTONDOWN:
            
            # if x < 100 and y < 100:
        #     print(x,y)    
            self.vision_calibrate_vx1_textbox.delete(0, len(self.vision_calibrate_vx1_textbox.get()))
            self.vision_calibrate_vx1_textbox.insert(0, str(x))

            self.vision_calibrate_vy1_textbox.delete(0, len(self.vision_calibrate_vy1_textbox.get()))
            self.vision_calibrate_vy1_textbox.insert(0, str(y))
            # elif x > 100:
            #     self.vision_calibrate_vx2_textbox.delete(0, len(self.vision_calibrate_vx2_textbox.get()))
            #     self.vision_calibrate_vx2_textbox.insert(0, str(x))
            # elif y > 100:
            #     self.vision_calibrate_vy2_textbox.delete(0, len(self.vision_calibrate_vy2_textbox.get()))
            #     self.vision_calibrate_vy2_textbox.insert(0, str(y))

    def vision_to_robot_xy(self, x, y):
        pxCmRatio = self.vision_pixel_to_cm_ratio
        visionX = float(self.vision_calibrate_vx1_textbox.get())
        visionY = float(self.vision_calibrate_vy1_textbox.get())
        robotX = float(self.vision_calibrate_rx1_textbox.get())
        robotY = float(self.vision_calibrate_ry1_textbox.get())

        deltaX = abs(float(x - visionX)) / pxCmRatio
        deltaY =  abs(float(y - visionY)) / pxCmRatio

        robotNewX = robotX + (deltaX * 10.0)
        robotNewY = robotY + (deltaY * 10.0) 

 

        return (robotNewX, robotNewY)


    def vision_robot_test(self):
        self.capture_current_frame()

        for obj in self.vision_objects:
            robotX, robotY = self.vision_to_robot_xy(obj["x"], obj["y"])

            self.axisX_pos_lable.configure(text=round(robotX, 2))
            self.end_effector_positionX = round(robotX, 4) / 1000.0
            self.end_effector_position[0] = round(robotX, 4) / 1000.0

            self.axisY_pos_lable.configure(text=round(robotY, 2))
            self.end_effector_positionY = round(robotY, 4) / 1000.0
            self.end_effector_position[1] = round(robotY, 4) / 1000.0

            print( self.end_effector_position[0], self.end_effector_position[1])

            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()

    def add_command(self):
        controlid = str(uuid.uuid4())
        index = int(self.add_command_index_textbox.get())
        initSpeed = float(self.add_command_initspeed_textbox.get())
        finalSpeed = float(self.add_command_finspeed_textbox.get())
        
        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True
        
        axis_command =  'A:{:.4f}, B:{:.4f}, C:{:.4f}, D:{:.4f}, E:{:.4f}, F:{:.4f}'.format(
            self.robot_axis_positions[0],
            self.robot_axis_positions[1],
            self.robot_axis_positions[2],
            self.robot_axis_positions[3],
            self.robot_axis_positions[4],
            self.robot_axis_positions[5])
        
        
        command = {
            "id": controlid,
            "type": "joint",
            "axis1": round(self.robot_axis_positions[0], 4),
            "axis2": round(self.robot_axis_positions[1], 4),
            "axis3": round(self.robot_axis_positions[2], 4),
            "axis4": round(self.robot_axis_positions[3], 4),
            "axis5": round(self.robot_axis_positions[4], 4),
            "axis6": round(self.robot_axis_positions[5], 4),
            "initSpeed": initSpeed,
            "finalSpeed": finalSpeed
        }
        
        
        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)
        
        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, axis_command)
        
        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, initSpeed)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)
        
        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, finalSpeed)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame, width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50, text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1
        self.add_command_index_textbox.delete(0, len(self.add_command_index_textbox.get()))
        self.add_command_index_textbox.insert(0, self.index -1)
        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)
        
        
    def add_gripper_command(self):
        controlid = str(uuid.uuid4())
        index = int(self.gripper_command_index_textbox.get())
        
        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True
        
        axis_command =  'G:{:.2f}'.format(
            float(self.gripper_command_steps_textbox.get()))
        
        
        command = {
            "id": controlid,
            "type": "gripper",
            "steps": round(float(self.gripper_command_steps_textbox.get()), 2),
        }
        
        
        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)
        
        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, axis_command)
        
        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)
        
        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1
        # self.add_command_index_textbox.delete(0, len(self.add_command_index_textbox.get()))
        # self.add_command_index_textbox.insert(0, self.index -1)
        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)


    def add_vision_capture_command(self):
        controlid = str(uuid.uuid4())
        index = int(self.command_vision_capture_index_textbox.get())

        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True

        vision_capture_command = "Vision Capture"

        command = {
            "id": controlid,
            "type": "vision_capture"
        }

        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)

        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, vision_capture_command)

        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)


        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1

        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)

    def add_vision_moveto_xy(self):
        controlid = str(uuid.uuid4())
        index = int(self.command_vision_movetoxypos_index_textbox.get())
        initSpeed = float(self.add_command_initspeed_textbox.get())
        finalSpeed = float(self.add_command_finspeed_textbox.get())


        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True

        vision_capture_command = "Move to Vision XY"

        command = {
            "id": controlid,
            "type": "vision_moveto_xy"
        }

        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)

        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, vision_capture_command)

        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, initSpeed)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)


        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, finalSpeed)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1

        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)


    def add_vision_moveto_z(self):
        controlid = str(uuid.uuid4())
        index = int(self.command_vision_movetozpos_index_textbox.get())
        initSpeed = float(self.add_command_initspeed_textbox.get())
        finalSpeed = float(self.add_command_finspeed_textbox.get())


        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True

        vision_capture_command = "Move to Vision Z"

        command = {
            "id": controlid,
            "type": "vision_moveto_z"
        }

        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)

        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, vision_capture_command)

        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, initSpeed)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)


        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, finalSpeed)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1

        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)

    def add_vision_moveback_z(self):
        controlid = str(uuid.uuid4())
        index = int(self.command_vision_movebackzpos_index_textbox.get())
        initSpeed = float(self.add_command_initspeed_textbox.get())
        finalSpeed = float(self.add_command_finspeed_textbox.get())
        backMM = float(self.command_vision_movebackzpos_mm_textbox.get())

        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True

        vision_capture_command = "Move Back Vision Z"

        command = {
            "id": controlid,
            "type": "vision_moveback_z",
            "moveBackMM": backMM
        }

        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)

        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, vision_capture_command)

        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, initSpeed)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)


        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, finalSpeed)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1

        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)

    def add_vision_gripper_close(self):
        controlid = str(uuid.uuid4())
        index = int(self.command_vision_gripperclose_index_textbox.get())


        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True

        vision_capture_command = "Vision Close Gripper"

        command = {
            "id": controlid,
            "type": "vision_gripper_close"
        }

        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)

        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, vision_capture_command)

        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)


        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1

        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)

    def add_vision_loop_object(self):
        controlid = str(uuid.uuid4())
        index = int(self.command_vision_loop_index_textbox.get())


        if (index  < len(self.command_index_textbox) -1):
            append = False
        else:
            append = True

        vision_capture_command = "Loop Vision Object"

        command = {
            "id": controlid,
            "type": "vision_loop_object"
        }

        command_index_textbox = customtkinter.CTkEntry(self.scrollable_frame,  width=50)
        command_index_textbox.grid(row=index + 1, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_index_textbox.insert(0, index)

        if append == True:
            self.command_index_textbox.append(command_index_textbox)
        else:
            self.command_index_textbox.insert(index, command_index_textbox)
        
        command_command_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_command_textbox.grid(row=index +2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_command_textbox.insert(0, vision_capture_command)

        if append == True:
            self.command_command_textbox.append(command_command_textbox)
        else:
            self.command_command_textbox.insert(index, command_command_textbox)
        
        command_init_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_init_speed_textbox.grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_init_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_init_speed_textbox.append(command_init_speed_textbox)
        else:
            self.command_init_speed_textbox.insert(index, command_init_speed_textbox)


        command_final_speed_textbox = customtkinter.CTkEntry(self.scrollable_frame)
        command_final_speed_textbox.grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        command_final_speed_textbox.insert(0, 0.0)
        
        if append == True:
            self.command_final_speed_textbox.append(command_final_speed_textbox)
        else:
            self.command_final_speed_textbox.insert(index, command_final_speed_textbox)
        
        
        command_execute_button = customtkinter.CTkButton(self.scrollable_frame,width=50, text="execute", command=lambda:self.command_execute_command(command))
        command_execute_button.grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_execute_button.append(command_execute_button)
        else:
            self.command_execute_button.insert(index, command_execute_button)
        
        
        command_copy_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command))
        command_copy_button.grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_copy_button.append(command_copy_button)
        else:
            self.command_copy_button.insert(index, command_copy_button)
        
        
        command_replace_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid))
        command_replace_button.grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
        if append == True:
            self.command_replace_button.append(command_replace_button)
        else:
            self.command_replace_button.insert(index, command_replace_button)
        
        command_delete_button = customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid))
        command_delete_button.grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        if append == True:
            self.command_delete_button.append(command_delete_button)
        else:
            self.command_delete_button.insert(index, command_delete_button)
        
        
        self.index = self.index + 1

        
        self.reset_command_index()
            
        if append == True:
            self.controlIds.append(controlid)
            self.commands.append(command)
        else:
            self.commands.insert(index, command)
            self.controlIds.insert(index, controlid)
        
        print(self.commands)

    def reset_command_index(self):
        for i in range(len(self.command_index_textbox)):
            self.command_index_textbox[i].grid(row=i+2)
            self.command_index_textbox[i].delete(0, len(self.command_index_textbox[i].get()))
            self.command_index_textbox[i].insert(0, i)
            self.command_command_textbox[i].grid(row=i+2)
            self.command_init_speed_textbox[i].grid(row=i+2)
            self.command_final_speed_textbox[i].grid(row=i+2)
            self.command_execute_button[i].grid(row=i+2)
            self.command_copy_button[i].grid(row=i+2)
            self.command_replace_button[i].grid(row=i+2)
            self.command_delete_button[i].grid(row=i+2)
            self.add_command_index_textbox.delete(0, len(self.add_command_index_textbox.get()))
            self.add_command_index_textbox.insert(0, i)
            
            self.gripper_command_index_textbox.delete(0, len(self.gripper_command_index_textbox.get()))
            self.gripper_command_index_textbox.insert(0, i)
            
            self.command_vision_capture_index_textbox.delete(0, len(self.command_vision_capture_index_textbox.get()))
            self.command_vision_capture_index_textbox.insert(0, i)

            self.command_vision_movetoxypos_index_textbox.delete(0, len(self.command_vision_movetoxypos_index_textbox.get()))
            self.command_vision_movetoxypos_index_textbox.insert(0, i)

            self.command_vision_movetozpos_index_textbox.delete(0, len(self.command_vision_movetozpos_index_textbox.get()))
            self.command_vision_movetozpos_index_textbox.insert(0, i)

            self.command_vision_gripperclose_index_textbox.delete(0, len(self.command_vision_gripperclose_index_textbox.get()))
            self.command_vision_gripperclose_index_textbox.insert(0, i)

            self.command_vision_loop_index_textbox.delete(0, len(self.command_vision_loop_index_textbox.get()))
            self.command_vision_loop_index_textbox.insert(0, i)



    def command_execute_command(self, command):
        
        if command["type"] == "joint":
            
            self.robot_axis_positions[0] = command["axis1"]
            self.robot_axis_positions[1] = command["axis2"]
            self.robot_axis_positions[2] = command["axis3"]
            self.robot_axis_positions[3] = command["axis4"]
            self.robot_axis_positions[4] = command["axis5"]
            self.robot_axis_positions[5] = command["axis6"]
            
            self.doFK()
            self.update_ui()
            
            self.send_join_command_v2(
                command["axis1"],
                command["axis2"],
                command["axis3"],
                command["axis4"],
                command["axis5"],
                command["axis6"],
                command["initSpeed"],
                command["finalSpeed"]
            )
        elif command["type"] == "gripper":
            self.set_gripper_v2(command["steps"])
        elif command["type"] == "vision_capture":
            self.capture_current_frame()
        elif command["type"] == "vision_moveto_xy":

            if len(self.vision_objects) > 0:
                obj = self.vision_objects[0]
                robotX, robotY = self.vision_to_robot_xy(obj["x"], obj["y"])
                self.axisX_pos_lable.configure(text=round(robotX, 2))
                self.end_effector_positionX = round(robotX, 4) / 1000.0
                self.end_effector_position[0] = round(robotX, 4) / 1000.0

                self.axisY_pos_lable.configure(text=round(robotY, 2))
                self.end_effector_positionY = round(robotY, 4) / 1000.0
                self.end_effector_position[1] = round(robotY, 4) / 1000.0
                self.end_effector_euler[0] = -90.0
                self.end_effector_euler[1] = obj["angle"]

                self.doIK()
                self.update_ui()
                self.send_join_command()
                # self.show_plot()
                
        elif command["type"] == "vision_moveto_z":

            if len(self.vision_objects) > 0:
                obj = self.vision_objects[0]
                robotX, robotY = self.vision_to_robot_xy(obj["x"], obj["y"])
                self.axisX_pos_lable.configure(text=round(robotX, 2))
                self.end_effector_positionX = round(robotX, 4) / 1000.0
                self.end_effector_position[0] = round(robotX, 4) / 1000.0

                self.axisY_pos_lable.configure(text=round(robotY, 2))
                self.end_effector_positionY = round(robotY, 4) / 1000.0
                self.end_effector_position[1] = round(robotY, 4) / 1000.0

                self.end_effector_euler[0] = -90.0
                self.end_effector_euler[1] = obj["angle"]


                robotZ = float(self.vision_calibrate_rz_textbox.get())
                self.axisZ_pos_lable.configure(text=round(robotZ, 2))
                self.end_effector_positionZ = round(robotZ, 4) / 1000.0
                self.end_effector_position[2] = round(robotZ, 4) / 1000.0

                self.doIK()
                self.update_ui()
                self.send_join_command()
                self.show_plot()
            
        elif command["type"] == "vision_moveback_z":
            robotZ = float(self.vision_calibrate_rz_textbox.get())
            backMM = command["moveBackMM"]
            robotZ = robotZ + backMM
            self.axisZ_pos_lable.configure(text=round(robotZ, 2))
            self.end_effector_euler[0] = -90.0
            # self.end_effector_euler[1] = 0.0
            self.end_effector_positionZ = round(robotZ, 4) / 1000.0
            self.end_effector_position[2] = round(robotZ, 4) / 1000.0

            self.doIK()
            self.update_ui()
            self.send_join_command()
            

            # self.show_plot()
        elif command["type"] == "vision_gripper_close":
            if len(self.vision_objects) > 0:
                obj = self.vision_objects[0]
                ratio = float(self.vision_calibrate_grpper_ratio_textbox.get())
                width = obj["width"]
                height = obj["height"]
                if width > height:
                    width = height

                steps = round(width * ratio, 0)
                self.set_gripper_v2(steps)

        elif command["type"] == "vision_loop_object":
            self.capture_current_frame()

            return len(self.vision_objects) > 0 
        

        return False
        
    def command_delete_command(self, controlid):
        print(controlid)
        for i in range(len(self.command_index_textbox)):
            if self.controlIds[i] == controlid:
                self.command_index_textbox[i].destroy()
                self.command_command_textbox[i].destroy()
                self.command_init_speed_textbox[i].destroy()
                self.command_final_speed_textbox[i].destroy()
                self.command_execute_button[i].destroy()
                self.command_copy_button[i].destroy()
                self.command_replace_button[i].destroy()
                self.command_delete_button[i].destroy()
                
                del self.command_index_textbox[i]
                del self.command_command_textbox[i]
                del self.command_init_speed_textbox[i]
                del self.command_final_speed_textbox[i]
                del self.command_execute_button[i]
                del self.command_copy_button[i]
                del self.command_replace_button[i]
                del self.command_delete_button[i]
                del self.controlIds[i]
                del self.commands[i]
                self.reset_command_index()
                
                return
    
    
    def load_from_commands(self):
        for i in range(len(self.command_index_textbox)):
            self.command_index_textbox[0].destroy()
            self.command_command_textbox[0].destroy()
            self.command_init_speed_textbox[0].destroy()
            self.command_final_speed_textbox[0].destroy()
            self.command_execute_button[0].destroy()
            self.command_copy_button[0].destroy()
            self.command_replace_button[0].destroy()
            self.command_delete_button[0].destroy()
            

            del self.command_index_textbox[0]
            del self.command_command_textbox[0]
            del self.command_init_speed_textbox[0]
            del self.command_final_speed_textbox[0]
            del self.command_execute_button[0]
            del self.command_copy_button[0]
            del self.command_replace_button[0]
            del self.command_delete_button[0]
            del self.controlIds[0]
            
            
        for i in range(len(self.commands)):
            controlid = self.commands[i]["id"]
            self.create_commands_elements(i, self.commands[i])
        
            self.controlIds.append(controlid)
        
        
        self.reset_command_index()
            
        print(len(self.command_index_textbox))
        
    def command_copy_command(self, command):
        index = len(self.command_index_textbox)
        command["id"] = str(uuid.uuid4())
        
        self.commands.append(command)
        self.controlIds.append(command["id"])
        self.create_commands_elements(index, command)
        self.reset_command_index()
        
    def command_replace_command(self, controlid):
        
        print(controlid)
        for i in range(len(self.command_index_textbox)):
            if self.controlIds[i] == controlid:
                type = self.commands[i]["type"]
                
                if type == "joint":
                    self.commands[i]["axis1"] = self.robot_axis_positions[0]
                    self.commands[i]["axis2"] = self.robot_axis_positions[1]
                    self.commands[i]["axis3"] = self.robot_axis_positions[2]
                    self.commands[i]["axis4"] = self.robot_axis_positions[3]
                    self.commands[i]["axis5"] = self.robot_axis_positions[4]
                    self.commands[i]["axis6"] = self.robot_axis_positions[5]
                    self.commands[i]["initSpeed"] = float(self.add_command_initspeed_textbox.get())
                    self.commands[i]["finalSpeed"] = float(self.add_command_finspeed_textbox.get())
                    axis_command =  'A:{:.4f}, B:{:.4f}, C:{:.4f}, D:{:.4f}, E:{:.4f}, F:{:.4f}'.format(
                        self.robot_axis_positions[0],
                        self.robot_axis_positions[1],
                        self.robot_axis_positions[2],
                        self.robot_axis_positions[3],
                        self.robot_axis_positions[4],
                        self.robot_axis_positions[5])
                elif type == "gripper":
                    self.commands[i]["steps"] = self.robot_axis_positions[0]
                    
                    axis_command =  'G:{:.2f}'.format(
                    float(self.gripper_command_steps_textbox.get()))
                    self.commands[i]["steps"] = round(float(self.gripper_command_steps_textbox.get()), 2)
                elif type == "vision_capture":
                    axis_command =  "Move to Vision XY"
                
                elif type == "vision_moveto_xy":
                    axis_command =  "Move to Vision XY"
                elif type == "vision_moveto_z":
                    axis_command =  "Move to Vision Z"
                elif type == "vision_moveback_z":
                    axis_command =  "Move Back Vision Z"
                elif type == "vision_gripper_close":
                    axis_command =  "Vision Gripper Close"
                elif type == "vision_loop_object":
                    axis_command =  "Vision Loop Object"
                
                
                self.command_command_textbox[i].delete(0, len(self.command_command_textbox[i].get()))
                self.command_command_textbox[i].insert(0, axis_command)
                
                self.command_init_speed_textbox[i].delete(0, len(self.command_init_speed_textbox[i].get()))
                self.command_init_speed_textbox[i].insert(0, self.commands[i]["initSpeed"])
                
                self.command_final_speed_textbox[i].delete(0, len(self.command_final_speed_textbox[i].get()))
                self.command_final_speed_textbox[i].insert(0, self.commands[i]["finalSpeed"])
            
                
                self.command_execute_button[i].configure(command=lambda:self.command_execute_command(self.commands[i]))
                self.command_copy_button[i].configure(command=lambda:self.command_copy_command(self.commands[i]))
                print(self.commands[i])                                         
                return
        
    def create_commands_elements(self,index, command):
        controlid = command["id"]
        controltype = command["type"]

        if controltype == "joint":
            axis_command =  'A:{:.4f}, B:{:.4f}, C:{:.4f}, D:{:.4f}, E:{:.4f}, F:{:.4f}'.format(
                command["axis1"],
                command["axis2"],
                command["axis3"],
                command["axis4"],
                command["axis5"],
                command["axis6"])
        elif controltype == "gripper":
            axis_command =  'G:{:.2f}'.format(command["steps"])
        elif controltype == "vision_capture":
            axis_command =  "Visio Capture"

        elif controltype == "vision_moveto_xy":
            axis_command =  "Move to Vision XY"
        elif controltype == "vision_moveto_z":
            axis_command =  "Move to Vision Z"
        elif controltype == "vision_moveback_z":
            axis_command =  "Move Back Vision Z"
        elif controltype == "vision_gripper_close":
            axis_command =  "Vision Gripper Close"
        elif controltype == "vision_loop_object":
            axis_command =  "Vision Loop Object"


        self.command_index_textbox.append(customtkinter.CTkEntry(self.scrollable_frame,  width=50))
        self.command_index_textbox[index].grid(row=index + 2, column=0, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_index_textbox[index].insert(0, index)


        self.command_command_textbox.append(customtkinter.CTkEntry(self.scrollable_frame))
        self.command_command_textbox[index].grid(row=index + 2, column=1, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_command_textbox[index].insert(0, axis_command)


        self.command_init_speed_textbox.append(customtkinter.CTkEntry(self.scrollable_frame))
        self.command_init_speed_textbox[index].grid(row=index +2, column=2, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_init_speed_textbox[index].insert(0, 0.0)

        self.command_final_speed_textbox.append(customtkinter.CTkEntry(self.scrollable_frame))
        self.command_final_speed_textbox[index].grid(row=index +2, column=3, padx=(5, 5), pady=(5,5), sticky="nsew")
        self.command_final_speed_textbox[index].insert(0, 0.0)

        self.command_execute_button.append(customtkinter.CTkButton(self.scrollable_frame, width=50,text="execute", command=lambda:self.command_execute_command(command)))
        self.command_execute_button[index].grid(row=index +2, column=4, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.command_copy_button.append(customtkinter.CTkButton(self.scrollable_frame, width=50,text="copy", command=lambda:self.command_copy_command(command)))
        self.command_copy_button[index].grid(row=index +2, column=5, padx=(5, 5), pady=(5,5), sticky="nsew")

        self.command_replace_button.append(customtkinter.CTkButton(self.scrollable_frame, width=50,text="replace", command=lambda:self.command_replace_command(controlid)))
        self.command_replace_button[index].grid(row=index +2, column=6, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        self.command_delete_button.append(customtkinter.CTkButton(self.scrollable_frame, width=50,text="delete", command=lambda:self.command_delete_command(controlid)))
        self.command_delete_button[index].grid(row=index +2, column=7, padx=(5, 5), pady=(5,5), sticky="nsew")
        
        
    def start_execute_all(self):
        if self.start == False:
            t = threading.Thread(target=self.command_execute_all)
            t.start()
    
    def command_execute_all(self):
        

        cond = True

        while cond:
            self.start = True
            self.reset_command_index()    
            for i in range(len(self.commands)):
                if self.stop == True:
                    self.start = False
                    self.stop = False
                    return
                self.command_index_textbox[i].insert(0, "**")        
                self.update()
                cond = self.command_execute_command(self.commands[i])
                
            self.start = False
            self.stop = False
        
    def command_stop_all(self):
        if self.start == True:
            self.stop = True
        
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")
        
    def connect_robot(self):
        try:
            self.arduino  = serial.Serial(port=self.port_textbox.get(), baudrate=115200, timeout=None)
            self.connect_status_label.configure(text="CONNECTED")
        except Exception as error:
            self.connect_status_label.configure(text="FAIL TO CONNECT")
            print(error)
            
    def doFK(self):
        target_angles = [math.radians(0.0), 
                         math.radians(self.robot_axis_positions[0]),
                         math.radians(self.robot_axis_positions[1]),
                         math.radians(self.robot_axis_positions[2]),
                         math.radians(self.robot_axis_positions[3]),
                         math.radians(self.robot_axis_positions[4]),
                         math.radians(self.robot_axis_positions[5])]
        # print(["%.4f" % elem for elem in target_angles])
        
        print (target_angles)
        fk=self.robot.forward_kinematics(target_angles)
        # print(fk[:3,3])
        # print(fk[:3,0])
        # print(fk[:3,:3])
        # print(fk)
        self.end_effector_position = fk[:3,3]
        self.end_effector_orientation = fk[:3,:3]
        x,y,z = self.rotation_angles()
        self.end_effector_euler = [x,y,z]
        print(self.end_effector_position)
        print(self.end_effector_orientation)
        print(self.end_effector_euler)
        
        
        self.ik=self.robot.inverse_kinematics(target_position=self.end_effector_position, target_orientation=self.end_effector_orientation, orientation_mode="all")
        # # angles = list(map(lambda r:math.degrees(r), ik.tolist()))
        
        # self.robot_axis_positions[0] = math.degrees(self.ik[1].item())
        # self.robot_axis_positions[1] = math.degrees(self.ik[2].item())
        # self.robot_axis_positions[2] = math.degrees(self.ik[3].item())
        # self.robot_axis_positions[3] = math.degrees(self.ik[4].item())
        # self.robot_axis_positions[4] = math.degrees(self.ik[5].item())
        # self.robot_axis_positions[5] = math.degrees(self.ik[6].item())
        
        # fig, ax = plot_utils.init_3d_figure()
        # self.robot.plot(ik, ax, target=self.end_effector_position, show=True)
        # fig.set_figheight(9)
        # fig.set_figwidth(13)
        # plt.xlim(-0.5, 0.5)
        # plt.ylim(-0.5, 0.5)
        # ax.set_zlim(0.0, 0.6)
        # plt.ion()
        # ax.legend()
        
    def doIK(self):
        self.end_effector_orientation = self.rotation_matrix(self.end_effector_euler[0], self.end_effector_euler[1],self.end_effector_euler[2])
        
        x, y, z= self.end_effector_position
        self.ik=self.robot.inverse_kinematics(target_position=[x,y,z], target_orientation=self.end_effector_orientation, orientation_mode="all")
        
        self.robot_axis_positions[0] = math.degrees(self.ik[1].item())
        self.robot_axis_positions[1] = math.degrees(self.ik[2].item())
        self.robot_axis_positions[2] = math.degrees(self.ik[3].item())
        self.robot_axis_positions[3] = math.degrees(self.ik[4].item())
        self.robot_axis_positions[4] = math.degrees(self.ik[5].item())
        self.robot_axis_positions[5] = math.degrees(self.ik[6].item())
        
        # self.show_plot()
        # self.doFK()
    
    
    def update_ui(self):
        self.onchanged = True
        self.axis1_slider.set(round(self.robot_axis_positions[0],2))
        self.axis1_pos_lable.configure(text=round(self.robot_axis_positions[0], 2))
        
        self.axis2_slider.set(round(self.robot_axis_positions[1],2))
        self.axis2_pos_lable.configure(text=round(self.robot_axis_positions[1], 2))
        
        self.axis3_slider.set(round(self.robot_axis_positions[2],2))
        self.axis3_pos_lable.configure(text=round(self.robot_axis_positions[2], 2))
        
        self.axis4_slider.set(round(self.robot_axis_positions[3],2))
        self.axis4_pos_lable.configure(text=round(self.robot_axis_positions[3], 2))
        
        self.axis5_slider.set(round(self.robot_axis_positions[4],2))
        self.axis5_pos_lable.configure(text=round(self.robot_axis_positions[4], 2))
        
        self.axis6_slider.set(round(self.robot_axis_positions[5],2))
        self.axis6_pos_lable.configure(text=round(self.robot_axis_positions[5], 2))
        
        self.axisX_slider.set(round(self.end_effector_position[0], 3) * 1000)
        self.axisX_pos_lable.configure(text=round(self.end_effector_position[0], 3) * 1000)
        
        self.axisY_slider.set(round(self.end_effector_position[1], 3) * 1000)
        self.axisY_pos_lable.configure(text=round(self.end_effector_position[1], 3) * 1000)
        
        self.axisZ_slider.set(round(self.end_effector_position[2], 3) * 1000)
        self.axisZ_pos_lable.configure(text=round(self.end_effector_position[2], 3) * 1000)
        
        
        
        self.axisRX_slider.set(round(self.end_effector_euler[0], 3))
        self.axisRX_pos_lable.configure(text=round(self.end_effector_euler[0], 3))
        
        self.axisPY_slider.set(round(self.end_effector_euler[1], 3))
        self.axisPY_pos_lable.configure(text=round(self.end_effector_euler[1], 3))
        
        self.axisYZ_slider.set(round(self.end_effector_euler[2], 3))
        self.axisYZ_pos_lable.configure(text=round(self.end_effector_euler[2], 3))
        self.onchanged = False
        


    def rotation_matrix(self, theta1, theta2, theta3, order='xyz'):
        """
        input
            theta1, theta2, theta3 = rotation angles in rotation order (degrees)
            oreder = rotation order of x,y,z　e.g. XZY rotation -- 'xzy'
        output
            3x3 rotation matrix (numpy array)
        """
        c1 = np.cos(theta1 * np.pi / 180)
        s1 = np.sin(theta1 * np.pi / 180)
        c2 = np.cos(theta2 * np.pi / 180)
        s2 = np.sin(theta2 * np.pi / 180)
        c3 = np.cos(theta3 * np.pi / 180)
        s3 = np.sin(theta3 * np.pi / 180)

        if order == 'xzx':
            matrix=np.array([[c2, -c3*s2, s2*s3],
                             [c1*s2, c1*c2*c3-s1*s3, -c3*s1-c1*c2*s3],
                             [s1*s2, c1*s3+c2*c3*s1, c1*c3-c2*s1*s3]])
        elif order=='xyx':
            matrix=np.array([[c2, s2*s3, c3*s2],
                             [s1*s2, c1*c3-c2*s1*s3, -c1*s3-c2*c3*s1],
                             [-c1*s2, c3*s1+c1*c2*s3, c1*c2*c3-s1*s3]])
        elif order=='yxy':
            matrix=np.array([[c1*c3-c2*s1*s3, s1*s2, c1*s3+c2*c3*s1],
                             [s2*s3, c2, -c3*s2],
                             [-c3*s1-c1*c2*s3, c1*s2, c1*c2*c3-s1*s3]])
        elif order=='yzy':
            matrix=np.array([[c1*c2*c3-s1*s3, -c1*s2, c3*s1+c1*c2*s3],
                             [c3*s2, c2, s2*s3],
                             [-c1*s3-c2*c3*s1, s1*s2, c1*c3-c2*s1*s3]])
        elif order=='zyz':
            matrix=np.array([[c1*c2*c3-s1*s3, -c3*s1-c1*c2*s3, c1*s2],
                             [c1*s3+c2*c3*s1, c1*c3-c2*s1*s3, s1*s2],
                             [-c3*s2, s2*s3, c2]])
        elif order=='zxz':
            matrix=np.array([[c1*c3-c2*s1*s3, -c1*s3-c2*c3*s1, s1*s2],
                             [c3*s1+c1*c2*s3, c1*c2*c3-s1*s3, -c1*s2],
                             [s2*s3, c3*s2, c2]])
        elif order=='xyz':
            matrix=np.array([[c2*c3, -c2*s3, s2],
                             [c1*s3+c3*s1*s2, c1*c3-s1*s2*s3, -c2*s1],
                             [s1*s3-c1*c3*s2, c3*s1+c1*s2*s3, c1*c2]])
        elif order=='xzy':
            matrix=np.array([[c2*c3, -s2, c2*s3],
                             [s1*s3+c1*c3*s2, c1*c2, c1*s2*s3-c3*s1],
                             [c3*s1*s2-c1*s3, c2*s1, c1*c3+s1*s2*s3]])
        elif order=='yxz':
            matrix=np.array([[c1*c3+s1*s2*s3, c3*s1*s2-c1*s3, c2*s1],
                             [c2*s3, c2*c3, -s2],
                             [c1*s2*s3-c3*s1, c1*c3*s2+s1*s3, c1*c2]])
        elif order=='yzx':
            matrix=np.array([[c1*c2, s1*s3-c1*c3*s2, c3*s1+c1*s2*s3],
                             [s2, c2*c3, -c2*s3],
                             [-c2*s1, c1*s3+c3*s1*s2, c1*c3-s1*s2*s3]])
        elif order=='zyx':
            matrix=np.array([[c1*c2, c1*s2*s3-c3*s1, s1*s3+c1*c3*s2],
                             [c2*s1, c1*c3+s1*s2*s3, c3*s1*s2-c1*s3],
                             [-s2, c2*s3, c2*c3]])
        elif order=='zxy':
            matrix=np.array([[c1*c3-s1*s2*s3, -c2*s1, c1*s3+c3*s1*s2],
                             [c3*s1+c1*s2*s3, c1*c2, s1*s3-c1*c3*s2],
                             [-c2*s3, s2, c2*c3]])

        return matrix
        
    def rotation_angles(self,  order="xyz"):
        """
        input
            matrix = 3x3 rotation matrix (numpy array)
            oreder(str) = rotation order of x, y, z : e.g, rotation XZY -- 'xzy'
        output
            theta1, theta2, theta3 = rotation angles in rotation order
        """
        r11, r12, r13 = self.end_effector_orientation[0]
        r21, r22, r23 = self.end_effector_orientation[1]
        r31, r32, r33 = self.end_effector_orientation[2]

        if order == 'xzx':
            theta1 = np.arctan(r31 / r21)
            theta2 = np.arctan(r21 / (r11 * np.cos(theta1)))
            theta3 = np.arctan(-r13 / r12)

        elif order == 'xyx':
            theta1 = np.arctan(-r21 / r31)
            theta2 = np.arctan(-r31 / (r11 *np.cos(theta1)))
            theta3 = np.arctan(r12 / r13)

        elif order == 'yxy':
            theta1 = np.arctan(r12 / r32)
            theta2 = np.arctan(r32 / (r22 *np.cos(theta1)))
            theta3 = np.arctan(-r21 / r23)

        elif order == 'yzy':
            theta1 = np.arctan(-r32 / r12)
            theta2 = np.arctan(-r12 / (r22 *np.cos(theta1)))
            theta3 = np.arctan(r23 / r21)

        elif order == 'zyz':
            theta1 = np.arctan(r23 / r13)
            theta2 = np.arctan(r13 / (r33 *np.cos(theta1)))
            theta3 = np.arctan(-r32 / r31)

        elif order == 'zxz':
            theta1 = np.arctan(-r13 / r23)
            theta2 = np.arctan(-r23 / (r33 *np.cos(theta1)))
            theta3 = np.arctan(r31 / r32)

        elif order == 'xzy':
            theta1 = np.arctan(r32 / r22)
            theta2 = np.arctan(-r12 * np.cos(theta1) / r22)
            theta3 = np.arctan(r13 / r11)

        elif order == 'xyz':
            theta1 = np.arctan(-r23 / r33)
            theta2 = np.arctan(r13 * np.cos(theta1) / r33)
            theta3 = np.arctan(-r12 / r11)

        elif order == 'yxz':
            theta1 = np.arctan(r13 / r33)
            theta2 = np.arctan(-r23 * np.cos(theta1) / r33)
            theta3 = np.arctan(r21 / r22)

        elif order == 'yzx':
            theta1 = np.arctan(-r31 / r11)
            theta2 = np.arctan(r21 * np.cos(theta1) / r11)
            theta3 = np.arctan(-r23 / r22)

        elif order == 'zyx':
            theta1 = np.arctan(r21 / r11)
            theta2 = np.arctan(-r31 * np.cos(theta1) / r11)
            theta3 = np.arctan(r32 / r33)

        elif order == 'zxy':
            theta1 = np.arctan(-r12 / r22)
            theta2 = np.arctan(r32 * np.cos(theta1) / r22)
            theta3 = np.arctan(-r31 / r33)

        theta1 = theta1 * 180 / np.pi
        theta2 = theta2 * 180 / np.pi
        theta3 = theta3 * 180 / np.pi

        return (theta1, theta2, theta3)
    
    def on_axis1_changed(self, value):
        if (self.onchanged == False):
            self.axis1_pos_lable.configure(text=round(value, 2))
            self.robot_axis_positions[0] = round(value, 4)
            self.doFK()
            self.update_ui()
            self.send_join_command()
            
    def on_axis2_changed(self, value):
        if (self.onchanged == False):
            self.axis2_pos_lable.configure(text=round(value, 2))
            self.robot_axis_positions[1] = round(value, 4)
            self.doFK()
            self.update_ui()
            self.send_join_command()
    
    def on_axis3_changed(self, value):
        if (self.onchanged == False):
            self.axis3_pos_lable.configure(text=round(value, 2))
            self.robot_axis_positions[2] = round(value, 4)
            self.doFK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
    
    def on_axis4_changed(self, value):
        if (self.onchanged == False):
            self.axis4_pos_lable.configure(text=round(value, 2))
            self.robot_axis_positions[3] = round(value, 4)
            self.doFK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
            
    def on_axis5_changed(self, value):
        if (self.onchanged == False):
            self.axis5_pos_lable.configure(text=round(value, 2))
            self.robot_axis_positions[4] = round(value, 4)
            self.doFK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
    
    def on_axis6_changed(self, value):
        if (self.onchanged == False):
            self.axis6_pos_lable.configure(text=round(value, 2))
            self.robot_axis_positions[5] = round(value, 4)
            self.doFK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
    
    def on_x_changed(self, value):
        if (self.onchanged == False):
            self.axisX_pos_lable.configure(text=round(value, 2))
            self.end_effector_positionX = round(value, 4) / 1000.0
            self.end_effector_position[0] = round(value, 4) / 1000.0
            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
            
    def on_y_changed(self, value):
        if (self.onchanged == False):
            self.axisY_pos_lable.configure(text=round(value, 2))
            self.end_effector_positionY = round(value, 4) / 1000.0
            self.end_effector_position[1] = round(value, 4) / 1000.0
            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
            
    def on_z_changed(self, value):
        if (self.onchanged == False):
            self.axisZ_pos_lable.configure(text=round(value, 2))
            self.end_effector_positionZ = round(value, 4) / 1000.0
            self.end_effector_position[2] = round(value, 4) / 1000.0
            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
            
    def on_py_changed(self, value):
        if (self.onchanged == False):
            self.axisPY_pos_lable.configure(text=round(value, 2))
            self.end_effector_euler[1] = round(value, 4)
            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
            
    def on_rx_changed(self, value):
        if (self.onchanged == False):
            self.axisRX_pos_lable.configure(text=round(value, 2))
            self.end_effector_euler[0] = round(value, 4)
            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
    
    
    def on_yz_changed(self, value):
        if (self.onchanged == False):
            self.axisYZ_pos_lable.configure(text=round(value, 2))
            self.end_effector_euler[2] = round(value, 4)
            self.doIK()
            self.update_ui()
            self.send_join_command()
            self.show_plot()
            

    def on_add_axis1(self):
        value = self.axis1_add_textbox.get()
        current = self.axis1_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axis1_slider.set(newvalue) 
        self.on_axis1_changed(newvalue)
        # self.send_join_command()
        
    def on_minus_axis1(self):
        value = self.axis1_add_textbox.get()
        current = self.axis1_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axis1_slider.set(newvalue) 
        self.on_axis1_changed(newvalue)
        # self.send_join_command()
        
        
    def on_add_axis2(self):
        value = self.axis2_add_textbox.get()
        current = self.axis2_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axis2_slider.set(newvalue) 
        self.on_axis2_changed(newvalue)
        # self.send_join_command()
        
    def on_minus_axis2(self):
        value = self.axis2_add_textbox.get()
        current = self.axis2_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axis2_slider.set(newvalue) 
        self.on_axis2_changed(newvalue)
        # self.send_join_command()
        
    def on_add_axis3(self):
        value = self.axis3_add_textbox.get()
        current = self.axis3_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axis3_slider.set(newvalue) 
        self.on_axis3_changed(newvalue)
        # self.send_join_command()
        
    def on_minus_axis3(self):
        value = self.axis3_add_textbox.get()
        current = self.axis3_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axis3_slider.set(newvalue) 
        self.on_axis3_changed(newvalue)
        # self.send_join_command()
        
    def on_add_axis4(self):
        value = self.axis4_add_textbox.get()
        current = self.axis4_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axis4_slider.set(newvalue) 
        self.on_axis4_changed(newvalue)
        # self.send_join_command()
        
    def on_minus_axis4(self):
        value = self.axis4_add_textbox.get()
        current = self.axis4_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axis4_slider.set(newvalue) 
        self.on_axis4_changed(newvalue)
        # self.send_join_command()
    
    def on_add_axis5(self):
        value = self.axis5_add_textbox.get()
        current = self.axis5_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axis5_slider.set(newvalue) 
        self.on_axis5_changed(newvalue)
        # self.send_join_command()
        
    def on_minus_axis5(self):
        value = self.axis5_add_textbox.get()
        current = self.axis5_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axis5_slider.set(newvalue) 
        self.on_axis5_changed(newvalue)
        # self.send_join_command()
        
    def on_add_axis6(self):
        value = self.axis6_add_textbox.get()
        current = self.axis6_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axis6_slider.set(newvalue) 
        self.on_axis6_changed(newvalue)
        # self.send_join_command()
        
    def on_minus_axis6(self):
        value = self.axis6_add_textbox.get()
        current = self.axis6_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axis6_slider.set(newvalue) 
        self.on_axis6_changed(newvalue)
        # self.send_join_command()
        
    
    
    def on_add_x(self):
        value = self.axisX_add_textbox.get()
        current = self.axisX_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 800.0:
            newvalue = 800.0
        self.axisX_slider.set(newvalue) 
        self.on_x_changed(newvalue)
        # self.send_join_command()
    
    def on_minus_x(self):
        value = self.axisX_add_textbox.get()
        current = self.axisX_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -800.0:
            newvalue = -800.0
        self.axisX_slider.set(newvalue) 
        self.on_x_changed(newvalue)
        # self.send_join_command()

    def on_add_y(self):
        value = self.axisY_add_textbox.get()
        current = self.axisY_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 800.0:
            newvalue = 800.0
        self.axisY_slider.set(newvalue) 
        self.on_y_changed(newvalue)
        # self.send_join_command()
    
    def on_minus_y(self):
        value = self.axisY_add_textbox.get()
        current = self.axisY_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -800.0:
            newvalue = -800.0
        self.axisY_slider.set(newvalue) 
        self.on_y_changed(newvalue)
        # self.send_join_command()
    
    def on_add_z(self):
        value = self.axisZ_add_textbox.get()
        current = self.axisZ_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 800.0:
            newvalue = 800.0
        self.axisZ_slider.set(newvalue) 
        self.on_z_changed(newvalue)
        # self.send_join_command()
    
    def on_minus_z(self):
        value = self.axisZ_add_textbox.get()
        current = self.axisZ_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -800.0:
            newvalue = -800.0
        self.axisZ_slider.set(newvalue) 
        self.on_z_changed(newvalue)
        # self.send_join_command()
        
    def on_add_rx(self):
        value = self.axisRX_add_textbox.get()
        current = self.axisRX_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axisRX_slider.set(newvalue) 
        self.on_rx_changed(newvalue)
        # self.send_join_command()
    
    def on_minus_rx(self):
        value = self.axisRX_add_textbox.get()
        current = self.axisRX_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axisRX_slider.set(newvalue) 
        self.on_rx_changed(newvalue)
        # self.send_join_command()
        
    def on_add_py(self):
        value = self.axisPY_add_textbox.get()
        current = self.axisPY_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axisPY_slider.set(newvalue) 
        self.on_py_changed(newvalue)
        # self.send_join_command()
    
    def on_minus_py(self):
        value = self.axisPY_add_textbox.get()
        current = self.axisPY_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axisPY_slider.set(newvalue) 
        self.on_py_changed(newvalue)
        # self.send_join_command()
        
    def on_add_yz(self):
        value = self.axisYZ_add_textbox.get()
        current = self.axisYZ_slider.get()
        newvalue = float(current) + float(value)
        
        if newvalue > 180.0:
            newvalue = 180.0
        self.axisYZ_slider.set(newvalue) 
        self.on_yz_changed(newvalue)
        # self.send_join_command()
    
    def on_minus_yz(self):
        value = self.axisYZ_add_textbox.get()
        current = self.axisYZ_slider.get()
        newvalue = float(current) - float(value)
        
        if newvalue < -180.0:
            newvalue = -180.0
        self.axisYZ_slider.set(newvalue) 
        self.on_yz_changed(newvalue)
        # self.send_join_command()
        
    def on_init(self):
        self.robot_axis_positions[0] = 0.0
        self.robot_axis_positions[1] = -55.0
        self.robot_axis_positions[2] = -87.0
        self.robot_axis_positions[3] = 0.0
        self.robot_axis_positions[4] = 0.0
        self.robot_axis_positions[5] = 0.0
        self.doFK()
        self.update_ui()
        self.send_join_command()
        self.show_plot()
        
    def on_home(self):
        self.robot_axis_positions[0] = 0.0
        self.robot_axis_positions[1] = 0.0
        self.robot_axis_positions[2] = 0.0
        self.robot_axis_positions[3] = 0.0
        self.robot_axis_positions[4] = 0.0
        self.robot_axis_positions[5] = 0.0
        self.doFK()
        self.update_ui()
        self.send_join_command()
        self.show_plot()
    
    
    def save_commands(self):
        file = self.textbox_file.get()
        json_objects = json.dumps(self.commands, indent=4)
        
        with open(file, "w") as outfile:
            outfile.write(json_objects)
        
    
    def load_commands(self):
        file = self.textbox_file.get()
        
        with open(file, "r") as infile:
            self.commands = json.load(infile)
    
        self.load_from_commands()
    
    def set_speed(self):
        speed = float(self.speed_textbox.get())
        command = 'SP{0}\n'.format(speed)
        self.send_command(command)
        
    def reset_gripper(self):
        steps = float(self.gripper_reset_textbox.get())
        command = 'RS{0}\r\n'.format(steps)
        self.send_command(command)
        
    def set_gripper(self):
        steps = float(self.gripper_step_textbox.get())
        command = 'GR{0}\n'.format(steps)
        self.send_command(command)
                
    def set_gripper_v2(self, steps):
        command = 'GR{0}\n'.format(steps)
        self.send_command(command)
        
    def send_join_command(self, initSpeed=0.0, finalSpeed=0.0):
        command = '{}{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.2f},{:.2f}\n'.format("MN",
                                                                                                 self.robot_axis_positions[0],
                                                                                                 self.robot_axis_positions[1],
                                                                                                 self.robot_axis_positions[2],
                                                                                                 self.robot_axis_positions[3],
                                                                                                 self.robot_axis_positions[4],
                                                                                                 self.robot_axis_positions[5],
                                                                                                 initSpeed, finalSpeed)
        self.send_command(command)
    
    def send_join_command_v2(self,a,b,c,d,e,f, initSpeed=0.0, finalSpeed=0.0):
        command = '{}{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{:.2f},{:.2f}\n'.format("MN",a,b,c,d,e,f,initSpeed, finalSpeed)
        self.send_command(command)
        
        
    def send_command(self, command):
        if self.is_send_to_robot() == True:
            self.arduino.write(command.encode('ascii'))
            print("Command Send")
            print(command)
            print(self.arduino.readline())
            print("Command Read")
        
    
    def show_plot(self):
        if self.is_show_plot() == True:
            fig, ax = plot_utils.init_3d_figure()
            self.robot.plot(self.ik, ax, target=self.end_effector_position, show=False)

            # plt.xlim(-0.5, 0.5)
            # plt.ylim(-0.5, 0.5)
            ax.set_zlim(0.0, 0.6)
            # plt.ion()
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=8,  sticky="nsew")
            # canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)
            
            canvas.draw();
            self.update()
    
    def is_show_plot(self):
        return bool(self.show_plot_checkbox.get())
    
    def is_send_to_robot(self):
        return bool(self.send_to_robot_checkbox.get())
    

    def gradient(self, pt1, pt2):
        diff1 = 0
        diff2 = 0

        diff1 = pt2[1] - pt1[1]
        diff2 = pt2[0] - pt1[0]

        return (diff1) / (diff2)



    def getAngle(self, pt1, pt2, pt3):
        m1 = self.gradient(pt1, pt2)
        m2 = self.gradient(pt1, pt3)
            
        ang = math.atan((m2-m1)/ (1 + (m2*m1)))

        ang = math.degrees(ang)
        
        return ang


    def calAngle(self, box):
        point1 = np.array((int((box[0][0] + box[1][0]) * .5), int((box[0][1] + box[1][1]) * .5)))
        point2 = np.array((int((box[2][0] + box[3][0]) * .5), int((box[2][1] + box[3][1]) * .5)))
        point3 = np.array((int((box[1][0] + box[2][0]) * .5), int((box[1][1] + box[2][1]) * .5)))
        point4 = np.array((int((box[0][0] + box[3][0]) * .5), int((box[0][1] + box[3][1]) * .5)))

        dist1 = np.linalg.norm( point1 - point2 )
        dist2 = np.linalg.norm(point3 - point4)
        workPoint1 = point1 
        workPoint2 = point2

        if dist2 > dist1:
            workPoint1 = point3
            workPoint2 = point4	

        basePoint = np.array((0,0))
        targetPoint = np.array((0,0))
        if workPoint1[0] <= workPoint2[0]: # X1 < X2
            if workPoint1[1] >= workPoint2[1]: #y1 > y2 = "/" direction
                basePoint = workPoint1
                targetPoint = workPoint2
            else: # "\"
                basePoint = workPoint2
                targetPoint = workPoint1
        else: #X1 > X2
            if workPoint1[1] <= workPoint2[1]: #y1 < y2 "/"
                basePoint = workPoint2
                targetPoint = workPoint1
            else: # "\"
                basePoint = workPoint1
                targetPoint = workPoint2

        basePointTan = np.array((basePoint[0]-1, basePoint[1] - 100))
        angle = self.getAngle(basePoint,  basePointTan, targetPoint)

        ##add additional 1 degree
        if angle < 0:
            angle = angle -1
        else:
            angle = angle + 1
        return angle
        
app = App()
app.mainloop()