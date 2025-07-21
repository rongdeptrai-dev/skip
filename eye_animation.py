#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eye Animation Module - Realistic Eye Movement System
Tạo chuyển động mắt tự nhiên và chân thật cho background extension
"""

import tkinter as tk
from tkinter import Canvas
import math
import time
import random
import threading
from typing import Tuple, Optional

class RealisticEyeAnimator:
    """Class để tạo chuyển động mắt chân thật và mượt mà"""
    
    def __init__(self, canvas_width=400, canvas_height=300):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        # Cấu hình mắt
        self.eye_config = {
            "eye_width": 80,
            "eye_height": 50,
            "pupil_base_size": 20,
            "iris_size": 35,
            "eye_spacing": 100,
            "blink_duration": 0.15,
            "natural_blink_interval": (2, 8),  # 2-8 giây
        }
        
        # Vị trí mắt
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        spacing = self.eye_config["eye_spacing"]
        
        self.left_eye_center = (center_x - spacing//2, center_y)
        self.right_eye_center = (center_x + spacing//2, center_y)
        
        # Trạng thái hiện tại
        self.current_gaze = (0, 0)  # Hướng nhìn hiện tại (-1 đến 1)
        self.target_gaze = (0, 0)   # Hướng nhìn mục tiêu
        self.pupil_dilation = 1.0   # Độ giãn đồng tử (0.5 - 1.5)
        self.blink_state = 1.0      # Trạng thái nháy mắt (0 = đóng, 1 = mở)
        
        # Animation parameters
        self.movement_config = {
            "smooth_factor": 0.08,      # Tốc độ di chuyển mắt (thấp hơn = mượt hơn)
            "micro_movement_range": 0.1, # Phạm vi chuyển động nhỏ tự nhiên
            "saccade_speed": 0.3,       # Tốc độ di chuyển nhanh
            "drift_speed": 0.02,        # Tốc độ trôi chậm tự nhiên
        }
        
        # Timing controls
        self.last_micro_movement = time.time()
        self.last_natural_blink = time.time()
        self.last_gaze_change = time.time()
        
        # Animation state
        self.is_blinking = False
        self.animation_running = False
        
        # Tkinter setup
        self.root = None
        self.canvas = None
        self.setup_gui()
        
    def setup_gui(self):
        """Thiết lập giao diện Tkinter"""
        self.root = tk.Tk()
        self.root.title("Realistic Eye Animation - Background Extension")
        self.root.configure(bg='black')
        
        # Canvas cho animation
        self.canvas = Canvas(
            self.root, 
            width=self.canvas_width, 
            height=self.canvas_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='black')
        control_frame.pack(pady=10)
        
        # Buttons
        tk.Button(
            control_frame, 
            text="Start Animation", 
            command=self.start_animation,
            bg='green', 
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame, 
            text="Stop Animation", 
            command=self.stop_animation,
            bg='red', 
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame, 
            text="Random Gaze", 
            command=self.random_gaze,
            bg='blue', 
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame, 
            text="Blink", 
            command=self.trigger_blink,
            bg='purple', 
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Settings frame
        settings_frame = tk.Frame(self.root, bg='black')
        settings_frame.pack(pady=5)
        
        # Smoothness control
        tk.Label(settings_frame, text="Smoothness:", bg='black', fg='white').pack(side=tk.LEFT)
        self.smoothness_var = tk.DoubleVar(value=self.movement_config["smooth_factor"])
        smoothness_scale = tk.Scale(
            settings_frame, 
            from_=0.01, 
            to=0.5, 
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.smoothness_var,
            command=self.update_smoothness,
            bg='gray',
            fg='white'
        )
        smoothness_scale.pack(side=tk.LEFT, padx=5)
        
        # Pupil dilation control
        tk.Label(settings_frame, text="Pupil Size:", bg='black', fg='white').pack(side=tk.LEFT)
        self.pupil_var = tk.DoubleVar(value=1.0)
        pupil_scale = tk.Scale(
            settings_frame,
            from_=0.5,
            to=1.8,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.pupil_var,
            command=self.update_pupil_size,
            bg='gray',
            fg='white'
        )
        pupil_scale.pack(side=tk.LEFT, padx=5)
        
    def update_smoothness(self, value):
        """Cập nhật độ mượt của chuyển động"""
        self.movement_config["smooth_factor"] = float(value)
        
    def update_pupil_size(self, value):
        """Cập nhật kích thước đồng tử"""
        self.pupil_dilation = float(value)
        
    def calculate_eye_position(self, eye_center: Tuple[int, int], gaze: Tuple[float, float]) -> Tuple[int, int]:
        """Tính vị trí đồng tử dựa trên hướng nhìn"""
        center_x, center_y = eye_center
        gaze_x, gaze_y = gaze
        
        # Giới hạn chuyển động trong vùng mắt
        max_movement_x = self.eye_config["eye_width"] // 3
        max_movement_y = self.eye_config["eye_height"] // 3
        
        pupil_x = center_x + (gaze_x * max_movement_x)
        pupil_y = center_y + (gaze_y * max_movement_y)
        
        return (int(pupil_x), int(pupil_y))
        
    def draw_eye(self, center: Tuple[int, int], pupil_pos: Tuple[int, int]):
        """Vẽ một mắt với đồng tử ở vị trí cụ thể"""
        center_x, center_y = center
        pupil_x, pupil_y = pupil_pos
        
        # Kích thước mắt với hiệu ứng nháy mắt
        eye_width = self.eye_config["eye_width"]
        eye_height = int(self.eye_config["eye_height"] * self.blink_state)
        
        if eye_height < 5:  # Mắt gần như đóng
            # Vẽ đường kẻ thể hiện mắt đóng
            self.canvas.create_line(
                center_x - eye_width//2, center_y,
                center_x + eye_width//2, center_y,
                fill='white', width=2, tags='eyes'
            )
            return
            
        # Vẽ viền mắt (màu trắng)
        eye_outline = self.canvas.create_oval(
            center_x - eye_width//2, center_y - eye_height//2,
            center_x + eye_width//2, center_y + eye_height//2,
            fill='white', outline='gray', width=1, tags='eyes'
        )
        
        # Vẽ iris (màu xanh lá)
        iris_size = self.eye_config["iris_size"]
        iris = self.canvas.create_oval(
            pupil_x - iris_size//2, pupil_y - iris_size//2,
            pupil_x + iris_size//2, pupil_y + iris_size//2,
            fill='#4a7c59', outline='#2d4a35', width=1, tags='eyes'
        )
        
        # Vẽ đồng tử với kích thước thay đổi
        pupil_size = int(self.eye_config["pupil_base_size"] * self.pupil_dilation)
        pupil = self.canvas.create_oval(
            pupil_x - pupil_size//2, pupil_y - pupil_size//2,
            pupil_x + pupil_size//2, pupil_y + pupil_size//2,
            fill='black', tags='eyes'
        )
        
        # Vẽ ánh sáng phản chiếu trong đồng tử
        highlight_size = max(3, pupil_size // 4)
        highlight_x = pupil_x - pupil_size//4
        highlight_y = pupil_y - pupil_size//4
        
        highlight = self.canvas.create_oval(
            highlight_x - highlight_size//2, highlight_y - highlight_size//2,
            highlight_x + highlight_size//2, highlight_y + highlight_size//2,
            fill='white', tags='eyes'
        )
        
    def update_gaze_smooth(self):
        """Cập nhật hướng nhìn một cách mượt mà"""
        current_time = time.time()
        
        # Smooth interpolation đến target gaze
        smooth_factor = self.movement_config["smooth_factor"]
        
        # Tính khoảng cách đến target
        dx = self.target_gaze[0] - self.current_gaze[0]
        dy = self.target_gaze[1] - self.current_gaze[1]
        
        # Áp dụng smooth movement
        self.current_gaze = (
            self.current_gaze[0] + dx * smooth_factor,
            self.current_gaze[1] + dy * smooth_factor
        )
        
        # Thêm micro movements tự nhiên
        if current_time - self.last_micro_movement > 0.5:
            micro_range = self.movement_config["micro_movement_range"]
            micro_x = random.uniform(-micro_range, micro_range)
            micro_y = random.uniform(-micro_range, micro_range)
            
            self.target_gaze = (
                max(-1, min(1, self.target_gaze[0] + micro_x)),
                max(-1, min(1, self.target_gaze[1] + micro_y))
            )
            
            self.last_micro_movement = current_time
            
    def update_natural_behaviors(self):
        """Cập nhật hành vi tự nhiên như nháy mắt, thay đổi hướng nhìn"""
        current_time = time.time()
        
        # Natural blinking
        blink_interval = random.uniform(*self.eye_config["natural_blink_interval"])
        if current_time - self.last_natural_blink > blink_interval and not self.is_blinking:
            self.trigger_blink()
            self.last_natural_blink = current_time
            
        # Random gaze changes
        if current_time - self.last_gaze_change > random.uniform(3, 10):
            self.random_gaze()
            self.last_gaze_change = current_time
            
        # Pupil dilation variation
        if random.random() < 0.01:  # 1% chance per frame
            variation = random.uniform(-0.1, 0.1)
            self.pupil_dilation = max(0.5, min(1.8, self.pupil_dilation + variation))
            
    def trigger_blink(self):
        """Kích hoạt nháy mắt"""
        if self.is_blinking:
            return
            
        self.is_blinking = True
        
        def blink_animation():
            # Đóng mắt
            frames = 5
            for i in range(frames):
                self.blink_state = 1.0 - (i / frames)
                time.sleep(self.eye_config["blink_duration"] / frames)
                
            # Mở mắt
            for i in range(frames):
                self.blink_state = i / frames
                time.sleep(self.eye_config["blink_duration"] / frames)
                
            self.blink_state = 1.0
            self.is_blinking = False
            
        threading.Thread(target=blink_animation, daemon=True).start()
        
    def random_gaze(self):
        """Thiết lập hướng nhìn ngẫu nhiên"""
        # Tạo hướng nhìn tự nhiên (tránh các góc cực đoan)
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0.2, 0.8)
        
        new_gaze_x = math.cos(angle) * distance
        new_gaze_y = math.sin(angle) * distance
        
        self.target_gaze = (new_gaze_x, new_gaze_y)
        
    def render_frame(self):
        """Render một frame của animation"""
        # Clear canvas
        self.canvas.delete('eyes')
        
        # Update behaviors
        self.update_gaze_smooth()
        self.update_natural_behaviors()
        
        # Calculate pupil positions
        left_pupil_pos = self.calculate_eye_position(self.left_eye_center, self.current_gaze)
        right_pupil_pos = self.calculate_eye_position(self.right_eye_center, self.current_gaze)
        
        # Draw eyes
        self.draw_eye(self.left_eye_center, left_pupil_pos)
        self.draw_eye(self.right_eye_center, right_pupil_pos)
        
        # Vẽ thông tin debug
        self.draw_debug_info()
        
    def draw_debug_info(self):
        """Vẽ thông tin debug"""
        info_text = f"Gaze: ({self.current_gaze[0]:.2f}, {self.current_gaze[1]:.2f})\n"
        info_text += f"Pupil: {self.pupil_dilation:.2f}\n"
        info_text += f"Blink: {self.blink_state:.2f}"
        
        self.canvas.create_text(
            10, 10, 
            text=info_text, 
            anchor='nw', 
            fill='white', 
            font=('Arial', 10),
            tags='eyes'
        )
        
    def animation_loop(self):
        """Vòng lặp animation chính"""
        while self.animation_running:
            try:
                self.render_frame()
                time.sleep(1/60)  # 60 FPS
            except:
                break
                
    def start_animation(self):
        """Bắt đầu animation"""
        if not self.animation_running:
            self.animation_running = True
            threading.Thread(target=self.animation_loop, daemon=True).start()
            print("✅ Eye animation started")
            
    def stop_animation(self):
        """Dừng animation"""
        self.animation_running = False
        print("🛑 Eye animation stopped")
        
    def run(self):
        """Chạy ứng dụng"""
        print("🎯 Starting Realistic Eye Animation System...")
        print("📋 Features:")
        print("   - Smooth, natural eye movements")
        print("   - Realistic pupil dilation")
        print("   - Automatic blinking")
        print("   - Micro-movements for realism")
        print("   - Interactive controls")
        
        # Start animation automatically
        self.start_animation()
        
        # Start GUI
        self.root.mainloop()

def main():
    """Main function để chạy eye animation"""
    try:
        animator = RealisticEyeAnimator(canvas_width=500, canvas_height=400)
        animator.run()
    except KeyboardInterrupt:
        print("\n🛑 Animation stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()