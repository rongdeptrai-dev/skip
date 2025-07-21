#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Bot - Cải thiện hiệu quả skip với Eye Movement Extension
Enhanced with realistic eye movement animations for background overlay
"""

import os
import time
import logging
import json
import math
import threading
from typing import List, Optional, Tuple
import random

# Try to import advanced libraries, fallback to basic implementation
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV không khả dụng - sử dụng implementation cơ bản")

try:
    import subprocess
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False

class RealisticEyeMovement:
    """
    Hệ thống chuyển động mắt chân thật cho background extension
    Tạo chuyển động mắt mượt mà và tự nhiên
    """
    
    def __init__(self):
        print("👁️ Khởi tạo Realistic Eye Movement System...")
        
        # Cấu hình chuyển động mắt
        self.eye_config = {
            "movement_smoothness": 0.08,    # Độ mượt chuyển động (0.01-0.5)
            "pupil_dilation_base": 1.0,     # Kích thước đồng tử cơ bản  
            "blink_frequency": 3.5,         # Tần số nháy mắt (giây)
            "micro_movement_range": 0.15,   # Phạm vi chuyển động nhỏ tự nhiên
            "saccade_speed": 0.25,          # Tốc độ di chuyển nhanh
            "natural_drift": 0.03,          # Trôi chậm tự nhiên
            "focus_tracking": True,         # Theo dõi tiêu điểm
            "realistic_physics": True,      # Áp dụng vật lý chân thật
        }
        
        # Trạng thái hiện tại của mắt
        self.current_state = {
            "gaze_x": 0.0,           # Hướng nhìn X (-1 đến 1)
            "gaze_y": 0.0,           # Hướng nhìn Y (-1 đến 1)
            "target_x": 0.0,         # Mục tiêu X
            "target_y": 0.0,         # Mục tiêu Y
            "pupil_dilation": 1.0,   # Độ giãn đồng tử (0.5-1.8)
            "blink_state": 1.0,      # Trạng thái nháy mắt (0=đóng, 1=mở)
            "attention_level": 1.0,   # Mức độ tập trung (0-1)
            "fatigue_level": 0.0,    # Mức độ mệt mỏi (0-1)
        }
        
        # Timing controls
        self.timing = {
            "last_blink": time.time(),
            "last_micro_movement": time.time(),
            "last_gaze_change": time.time(),
            "last_attention_change": time.time(),
        }
        
        # Animation state
        self.is_active = False
        self.is_blinking = False
        
        # Statistics
        self.stats = {
            "total_blinks": 0,
            "gaze_changes": 0,
            "smooth_movements": 0,
            "session_start": time.time()
        }
        
        print("✅ Eye Movement System initialized")
    
    def calculate_natural_blink_interval(self):
        """Tính toán khoảng thời gian nháy mắt tự nhiên"""
        base_interval = self.eye_config["blink_frequency"]
        
        # Điều chỉnh dựa trên mức độ mệt mỏi
        fatigue_factor = 1 - (self.current_state["fatigue_level"] * 0.3)
        
        # Điều chỉnh dựa trên mức độ tập trung
        attention_factor = 0.8 + (self.current_state["attention_level"] * 0.4)
        
        # Thêm random variation
        random_factor = random.uniform(0.7, 1.3)
        
        return base_interval * fatigue_factor * attention_factor * random_factor
    
    def generate_smooth_movement(self):
        """Tạo chuyển động mắt mượt mà và tự nhiên"""
        current_time = time.time()
        
        # Smooth interpolation to target
        smoothness = self.eye_config["movement_smoothness"]
        
        # Apply realistic physics - không di chuyển quá nhanh
        max_change_per_frame = 0.05
        
        # Calculate movement towards target
        dx = self.current_state["target_x"] - self.current_state["gaze_x"]
        dy = self.current_state["target_y"] - self.current_state["gaze_y"]
        
        # Limit movement speed for realism
        movement_x = max(-max_change_per_frame, min(max_change_per_frame, dx * smoothness))
        movement_y = max(-max_change_per_frame, min(max_change_per_frame, dy * smoothness))
        
        # Apply movement
        self.current_state["gaze_x"] += movement_x
        self.current_state["gaze_y"] += movement_y
        
        # Add micro movements for realism
        if current_time - self.timing["last_micro_movement"] > 0.8:
            micro_range = self.eye_config["micro_movement_range"]
            micro_x = random.uniform(-micro_range, micro_range) * 0.3
            micro_y = random.uniform(-micro_range, micro_range) * 0.3
            
            self.current_state["target_x"] += micro_x
            self.current_state["target_y"] += micro_y
            
            # Keep within bounds
            self.current_state["target_x"] = max(-1, min(1, self.current_state["target_x"]))
            self.current_state["target_y"] = max(-1, min(1, self.current_state["target_y"]))
            
            self.timing["last_micro_movement"] = current_time
            self.stats["smooth_movements"] += 1
    
    def update_pupil_dilation(self):
        """Cập nhật độ giãn đồng tử dựa trên các yếu tố tự nhiên"""
        # Base dilation
        base = self.eye_config["pupil_dilation_base"]
        
        # Attention affects pupil size
        attention_effect = self.current_state["attention_level"] * 0.3
        
        # Fatigue affects pupil size  
        fatigue_effect = self.current_state["fatigue_level"] * 0.2
        
        # Random variation for realism
        random_variation = random.uniform(-0.05, 0.05)
        
        # Calculate new dilation
        new_dilation = base + attention_effect - fatigue_effect + random_variation
        
        # Smooth transition
        current_dilation = self.current_state["pupil_dilation"]
        smooth_factor = 0.02
        self.current_state["pupil_dilation"] = (
            current_dilation * (1 - smooth_factor) + new_dilation * smooth_factor
        )
        
        # Keep within realistic bounds
        self.current_state["pupil_dilation"] = max(0.5, min(1.8, self.current_state["pupil_dilation"]))
    
    def trigger_natural_blink(self):
        """Kích hoạt nháy mắt tự nhiên"""
        if self.is_blinking:
            return
            
        self.is_blinking = True
        self.stats["total_blinks"] += 1
        
        def blink_animation():
            """Animation nháy mắt mượt mà"""
            blink_duration = 0.15  # 150ms
            frames = 8
            frame_time = blink_duration / frames
            
            # Close eyes
            for i in range(frames // 2):
                progress = i / (frames // 2)
                self.current_state["blink_state"] = 1.0 - progress
                time.sleep(frame_time)
            
            # Open eyes  
            for i in range(frames // 2):
                progress = i / (frames // 2)
                self.current_state["blink_state"] = progress
                time.sleep(frame_time)
            
            self.current_state["blink_state"] = 1.0
            self.is_blinking = False
        
        # Run blink animation in separate thread
        threading.Thread(target=blink_animation, daemon=True).start()
    
    def set_gaze_target(self, x: float, y: float, speed_multiplier: float = 1.0):
        """
        Thiết lập mục tiêu hướng nhìn mới
        x, y: Tọa độ mục tiêu (-1 đến 1)
        speed_multiplier: Hệ số tốc độ (1.0 = bình thường)
        """
        self.current_state["target_x"] = max(-1, min(1, x))
        self.current_state["target_y"] = max(-1, min(1, y))
        
        self.stats["gaze_changes"] += 1
        self.timing["last_gaze_change"] = time.time()
        
        # Adjust movement speed if needed
        if speed_multiplier != 1.0:
            self.eye_config["movement_smoothness"] *= speed_multiplier
    
    def generate_natural_gaze_pattern(self):
        """Tạo pattern hướng nhìn tự nhiên"""
        current_time = time.time()
        
        # Change gaze target periodically
        if current_time - self.timing["last_gaze_change"] > random.uniform(4, 12):
            # Natural looking patterns
            patterns = [
                # Looking around naturally
                (random.uniform(-0.8, 0.8), random.uniform(-0.6, 0.6)),
                # Focus on center occasionally
                (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)),
                # Look at specific areas of interest
                (random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)),
                (-random.uniform(0.3, 0.7), random.uniform(-0.3, 0.3)),
            ]
            
            target_x, target_y = random.choice(patterns)
            self.set_gaze_target(target_x, target_y)
    
    def update_attention_and_fatigue(self):
        """Cập nhật mức độ tập trung và mệt mỏi"""
        current_time = time.time()
        
        if current_time - self.timing["last_attention_change"] > 30:  # Every 30 seconds
            # Simulate natural attention fluctuation
            attention_change = random.uniform(-0.1, 0.1)
            self.current_state["attention_level"] = max(0.3, min(1.0, 
                self.current_state["attention_level"] + attention_change))
            
            # Gradual fatigue increase
            fatigue_increase = random.uniform(0.001, 0.005)
            self.current_state["fatigue_level"] = min(0.8, 
                self.current_state["fatigue_level"] + fatigue_increase)
            
            self.timing["last_attention_change"] = current_time
    
    def update_animation_frame(self):
        """Cập nhật một frame của animation"""
        if not self.is_active:
            return
            
        current_time = time.time()
        
        # Update all eye movement components
        self.generate_smooth_movement()
        self.update_pupil_dilation()
        self.generate_natural_gaze_pattern()
        self.update_attention_and_fatigue()
        
        # Handle natural blinking
        blink_interval = self.calculate_natural_blink_interval()
        if current_time - self.timing["last_blink"] > blink_interval:
            self.trigger_natural_blink()
            self.timing["last_blink"] = current_time
    
    def get_eye_data(self) -> dict:
        """Lấy dữ liệu trạng thái mắt hiện tại"""
        return {
            "gaze": {
                "x": self.current_state["gaze_x"],
                "y": self.current_state["gaze_y"]
            },
            "pupil_dilation": self.current_state["pupil_dilation"],
            "blink_state": self.current_state["blink_state"],
            "attention_level": self.current_state["attention_level"],
            "fatigue_level": self.current_state["fatigue_level"]
        }
    
    def start_animation(self):
        """Bắt đầu animation mắt"""
        self.is_active = True
        print("👁️ Eye animation started")
    
    def stop_animation(self):
        """Dừng animation mắt"""
        self.is_active = False
        print("👁️ Eye animation stopped")
    
    def print_eye_stats(self):
        """In thống kê eye movement"""
        runtime = time.time() - self.stats["session_start"]
        print(f"\n👁️ EYE MOVEMENT STATS:")
        print(f"   Runtime: {runtime:.1f}s")
        print(f"   Total blinks: {self.stats['total_blinks']}")
        print(f"   Gaze changes: {self.stats['gaze_changes']}")
        print(f"   Smooth movements: {self.stats['smooth_movements']}")
        print(f"   Current attention: {self.current_state['attention_level']:.2f}")
        print(f"   Current fatigue: {self.current_state['fatigue_level']:.2f}")

def safe_import():
    """Import các thư viện cần thiết"""
    modules = {}
    
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1  # Giảm pause time
        modules['pyautogui'] = pyautogui
        print("✅ pyautogui: OK")
    except ImportError:
        print("❌ pyautogui: MISSING")
        modules['pyautogui'] = None
    
    try:
        import pygetwindow as gw
        modules['pygetwindow'] = gw
        print("✅ pygetwindow: OK")
    except ImportError:
        print("❌ pygetwindow: MISSING")
        modules['pygetwindow'] = None
    
    try:
        import pytesseract
        import platform
        if platform.system() == "Windows":
            paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            for path in paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        pytesseract.get_tesseract_version()
        modules['pytesseract'] = pytesseract
        print("✅ pytesseract: OK")
    except:
        print("❌ pytesseract: ERROR")
        modules['pytesseract'] = None
    
    return modules

class ImprovedTikTokBot:
    def __init__(self):
        print("🚀 Khởi tạo TikTok Bot Improved với Eye Movement Extension...")
        
        self.modules = safe_import()
        
        # Initialize Eye Movement System
        self.eye_movement = RealisticEyeMovement()
        
        # Cấu hình skip methods với độ ưu tiên
        self.skip_methods = [
            {
                "name": "enhanced_keyboard", 
                "priority": 1, 
                "enabled": True,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            },
            {
                "name": "mouse_swipe_up", 
                "priority": 2, 
                "enabled": True,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            },
            {
                "name": "mouse_click_next", 
                "priority": 3, 
                "enabled": True,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            },
            {
                "name": "combination_method", 
                "priority": 4, 
                "enabled": True,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            },
            {
                "name": "external_macro", 
                "priority": 5, 
                "enabled": False,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            }
        ]
        
        # Cấu hình
        self.config = {
            "max_retries": 5,
            "retry_delay": 0.3,
            "success_delay": 1.5,
            "focus_attempts": 3,
            "verification_enabled": True,
            "adaptive_timing": True
        }
        
        # Keywords
        self.live_keywords = [
            "LIVE", "Live", "live", 
            "TRỰC TIẾP", "Trực tiếp", "trực tiếp",
            "ĐANG LIVE", "Đang live",
            "PHÁT TRỰC TIẾP", "Phát trực tiếp"
        ]
        
        # Thống kê
        self.stats = {
            "total_detections": 0,
            "total_successes": 0,
            "session_start": time.time()
        }
        
        print("✅ Bot khởi tạo thành công!")
    
    def find_tiktok_windows(self):
        """Tìm cửa sổ TikTok với filter tốt hơn"""
        if not self.modules['pygetwindow']:
            return []
        
        try:
            gw = self.modules['pygetwindow']
            all_windows = gw.getAllWindows()
            
            tiktok_windows = []
            for window in all_windows:
                title = window.title.lower()
                # Mở rộng criteria tìm kiếm
                if any(keyword in title for keyword in ['tiktok', 'tik tok']) and \
                   window.width > 300 and window.height > 400 and \
                   window.visible:
                    tiktok_windows.append(window)
                    print(f"🎯 TikTok: {window.title} ({window.width}x{window.height})")
            
            return tiktok_windows
            
        except Exception as e:
            print(f"❌ Lỗi tìm cửa sổ: {e}")
            return []
    
    def ensure_window_focus(self, window, attempts=3):
        """Đảm bảo window được focus đúng cách"""
        for attempt in range(attempts):
            try:
                # Bring to front
                window.restore()  # Restore if minimized
                window.activate()
                time.sleep(0.2)
                
                # Click vào giữa window để đảm bảo focus
                if self.modules['pyautogui']:
                    center_x = window.left + window.width // 2
                    center_y = window.top + window.height // 2
                    self.modules['pyautogui'].click(center_x, center_y)
                    time.sleep(0.1)
                
                # Verify focus bằng cách kiểm tra active window
                gw = self.modules['pygetwindow']
                active_window = gw.getActiveWindow()
                if active_window and active_window.title == window.title:
                    print(f"✅ Window focused successfully (attempt {attempt + 1})")
                    return True
                
                print(f"⚠️ Focus attempt {attempt + 1} failed, retrying...")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Focus attempt {attempt + 1} error: {e}")
        
        print(f"❌ Failed to focus window after {attempts} attempts")
        return False
    
    def capture_screen(self, window):
        """Chụp màn hình với error handling tốt hơn"""
        if not self.modules['pyautogui']:
            return None
        
        try:
            # Ensure focus first
            if not self.ensure_window_focus(window):
                return None
            
            pyautogui = self.modules['pyautogui']
            
            # Capture với bounds checking
            left = max(0, window.left)
            top = max(0, window.top)
            width = min(window.width, 1920)  # Limit max width
            height = min(window.height, 1080)  # Limit max height
            
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            print(f"❌ Lỗi chụp màn hình: {e}")
            return None
    
    def detect_live_text(self, image):
        """Phát hiện LIVE với OCR cải thiện"""
        if not self.modules['pytesseract']:
            return False, ""
        
        try:
            pytesseract = self.modules['pytesseract']
            
            # Preprocess image cho OCR tốt hơn
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Multiple OCR attempts với configs khác nhau
            configs = [
                '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠ-ỹ ',
                '--oem 3 --psm 8',
                '--oem 3 --psm 7'
            ]
            
            all_text = ""
            for config in configs:
                try:
                    text = pytesseract.image_to_string(enhanced, config=config, lang='vie+eng')
                    all_text += " " + text
                except:
                    continue
            
            # Check keywords
            for keyword in self.live_keywords:
                if keyword in all_text:
                    return True, keyword
            
            return False, ""
            
        except Exception as e:
            return False, ""
    
    def verify_skip_success(self, window, pre_screenshot):
        """Verify xem skip có thành công không"""
        if not self.config["verification_enabled"]:
            return True
        
        try:
            time.sleep(1.0)  # Wait for transition
            post_screenshot = self.capture_screen(window)
            
            if post_screenshot is None:
                return False
            
            # So sánh screenshots để xác định có thay đổi không
            if pre_screenshot is not None:
                # Convert to grayscale cho comparison
                pre_gray = cv2.cvtColor(pre_screenshot, cv2.COLOR_BGR2GRAY)
                post_gray = cv2.cvtColor(post_screenshot, cv2.COLOR_BGR2GRAY)
                
                # Calculate difference
                diff = cv2.absdiff(pre_gray, post_gray)
                diff_percentage = (cv2.countNonZero(diff) / (diff.shape[0] * diff.shape[1])) * 100
                
                # If >20% của image thay đổi, coi như skip thành công
                if diff_percentage > 20:
                    print(f"✅ Skip verified: {diff_percentage:.1f}% change detected")
                    return True
                else:
                    print(f"❌ Skip failed: only {diff_percentage:.1f}% change")
                    return False
            
            # Fallback: check if still live
            is_live, _ = self.detect_live_text(post_screenshot)
            success = not is_live
            
            if success:
                print("✅ Skip verified: no more LIVE detected")
            else:
                print("❌ Skip failed: still detecting LIVE")
            
            return success
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
    
    # Skip Methods
    def skip_method_enhanced_keyboard(self, window, screenshot):
        """Enhanced keyboard method với multiple approaches"""
        if not self.modules['pyautogui']:
            return False
        
        try:
            pyautogui = self.modules['pyautogui']
            
            # Ensure strong focus
            if not self.ensure_window_focus(window, attempts=2):
                return False
            
            # Try multiple keyboard combinations
            methods = [
                lambda: pyautogui.press('down'),
                lambda: pyautogui.press('space'),
                lambda: pyautogui.press('right'),
                lambda: [pyautogui.press('space'), time.sleep(0.2), pyautogui.press('down')],
                lambda: [pyautogui.keyDown('down'), time.sleep(0.1), pyautogui.keyUp('down')]
            ]
            
            for i, method in enumerate(methods):
                print(f"   🔄 Keyboard method {i+1}")
                
                # Re-focus before each attempt
                window.activate()
                time.sleep(0.1)
                
                # Execute method
                if callable(method):
                    method()
                else:
                    for action in method:
                        if callable(action):
                            action()
                        else:
                            time.sleep(action)
                
                # Quick verification
                time.sleep(0.5)
                if self.verify_skip_success(window, screenshot):
                    print(f"   ✅ Keyboard method {i+1} successful")
                    return True
                
                print(f"   ❌ Keyboard method {i+1} failed")
                time.sleep(0.2)
            
            return False
            
        except Exception as e:
            print(f"❌ Enhanced keyboard error: {e}")
            return False
    
    def skip_method_mouse_swipe_up(self, window, screenshot):
        """Mouse swipe up method với variations"""
        if not self.modules['pyautogui']:
            return False
        
        try:
            pyautogui = self.modules['pyautogui']
            
            if not self.ensure_window_focus(window):
                return False
            
            # Calculate swipe coordinates
            center_x = window.left + window.width // 2
            center_y = window.top + window.height // 2
            
            # Try different swipe patterns
            swipe_patterns = [
                # Pattern 1: Normal swipe
                {
                    "start_y": center_y + 150,
                    "end_y": center_y - 150,
                    "duration": 0.3
                },
                # Pattern 2: Longer swipe
                {
                    "start_y": center_y + 200,
                    "end_y": center_y - 200, 
                    "duration": 0.4
                },
                # Pattern 3: Quick swipe
                {
                    "start_y": center_y + 100,
                    "end_y": center_y - 100,
                    "duration": 0.2
                }
            ]
            
            for i, pattern in enumerate(swipe_patterns):
                print(f"   🔄 Swipe pattern {i+1}")
                
                # Ensure focus
                pyautogui.click(center_x, center_y)
                time.sleep(0.1)
                
                # Perform swipe
                pyautogui.drag(
                    center_x, pattern["start_y"],
                    center_x, pattern["end_y"],
                    duration=pattern["duration"]
                )
                
                # Verification
                time.sleep(0.7)
                if self.verify_skip_success(window, screenshot):
                    print(f"   ✅ Swipe pattern {i+1} successful")
                    return True
                
                print(f"   ❌ Swipe pattern {i+1} failed")
                time.sleep(0.3)
            
            return False
            
        except Exception as e:
            print(f"❌ Mouse swipe error: {e}")
            return False
    
    def skip_method_mouse_click_next(self, window, screenshot):
        """Click vào vị trí nút next (nếu có)"""
        if not self.modules['pyautogui']:
            return False
        
        try:
            pyautogui = self.modules['pyautogui']
            
            if not self.ensure_window_focus(window):
                return False
            
            # Possible next button locations (relative to window)
            click_positions = [
                # Right side (common for next buttons)
                (window.left + window.width - 50, window.top + window.height // 2),
                # Bottom right
                (window.left + window.width - 100, window.top + window.height - 100),
                # Center right
                (window.left + window.width - 30, window.top + window.height // 2),
                # Bottom center (swipe area)
                (window.left + window.width // 2, window.top + window.height - 50)
            ]
            
            for i, (x, y) in enumerate(click_positions):
                print(f"   🔄 Click position {i+1}")
                
                # Click position
                pyautogui.click(x, y)
                time.sleep(0.3)
                
                # Verification
                if self.verify_skip_success(window, screenshot):
                    print(f"   ✅ Click position {i+1} successful")
                    return True
                
                print(f"   ❌ Click position {i+1} failed")
                time.sleep(0.2)
            
            return False
            
        except Exception as e:
            print(f"❌ Mouse click error: {e}")
            return False
    
    def skip_method_combination_method(self, window, screenshot):
        """Combination của nhiều methods"""
        print("   🔄 Trying combination method")
        
        try:
            # Combination 1: Click + Keyboard
            if self.modules['pyautogui']:
                pyautogui = self.modules['pyautogui']
                
                # Focus + Click center
                if self.ensure_window_focus(window):
                    center_x = window.left + window.width // 2
                    center_y = window.top + window.height // 2
                    
                    pyautogui.click(center_x, center_y)
                    time.sleep(0.1)
                    pyautogui.press('down')
                    time.sleep(0.5)
                    
                    if self.verify_skip_success(window, screenshot):
                        print("   ✅ Combination method successful")
                        return True
            
            # Combination 2: Multiple swipes
            if self.modules['pyautogui']:
                center_x = window.left + window.width // 2
                center_y = window.top + window.height // 2
                
                # Small swipe + big swipe
                pyautogui.drag(center_x, center_y + 50, center_x, center_y - 50, duration=0.1)
                time.sleep(0.1)
                pyautogui.drag(center_x, center_y + 150, center_x, center_y - 150, duration=0.3)
                time.sleep(0.7)
                
                if self.verify_skip_success(window, screenshot):
                    print("   ✅ Combination method successful") 
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Combination method error: {e}")
            return False
    
    def skip_method_external_macro(self, window, screenshot):
        """External macro method"""
        # Implementation tương tự như trước
        return False
    
    def update_method_stats(self, method, success):
        """Update statistics cho method"""
        method["attempts"] += 1
        if success:
            method["successes"] += 1
        
        # Calculate success rate
        if method["attempts"] > 0:
            method["success_rate"] = method["successes"] / method["attempts"]
    
    def get_best_methods(self):
        """Get methods sorted by success rate"""
        enabled_methods = [m for m in self.skip_methods if m["enabled"]]
        
        # Sort by success rate (descending), then by priority
        return sorted(enabled_methods, 
                     key=lambda x: (-x["success_rate"], x["priority"]))
    
    def skip_with_smart_selection(self, window):
        """Skip với smart method selection"""
        self.stats["total_detections"] += 1
        
        # Capture screenshot for verification
        screenshot = self.capture_screen(window)
        if screenshot is None:
            return False
        
        # Get best methods
        methods = self.get_best_methods()
        
        if not methods:
            print("❌ Không có method nào được kích hoạt")
            return False
        
        print(f"🎯 Thử {len(methods)} methods theo thứ tự hiệu quả...")
        
        for attempt in range(self.config["max_retries"]):
            print(f"\n🔄 Lần thử {attempt + 1}/{self.config['max_retries']}")
            
            for method in methods:
                method_name = method["name"]
                success_rate = method["success_rate"] * 100
                
                print(f"⚡ Method: {method_name} (success rate: {success_rate:.1f}%)")
                
                # Get method function
                method_func = getattr(self, f"skip_method_{method_name}", None)
                if not method_func:
                    continue
                
                # Execute method
                start_time = time.time()
                success = method_func(window, screenshot)
                execution_time = time.time() - start_time
                
                # Update stats
                self.update_method_stats(method, success)
                
                print(f"   ⏱️ Execution time: {execution_time:.2f}s")
                
                if success:
                    self.stats["total_successes"] += 1
                    print(f"✅ SKIP THÀNH CÔNG bằng {method_name}!")
                    time.sleep(self.config["success_delay"])
                    return True
                else:
                    print(f"❌ {method_name} failed")
                
                # Adaptive delay based on success rate
                if self.config["adaptive_timing"]:
                    delay = self.config["retry_delay"] * (1 + (1 - method["success_rate"]))
                    time.sleep(min(delay, 1.0))
                else:
                    time.sleep(self.config["retry_delay"])
            
            # Delay between retry attempts
            if attempt < self.config["max_retries"] - 1:
                print(f"⏳ Chờ trước lần thử tiếp theo...")
                time.sleep(0.5)
        
        print(f"❌ TẤT CẢ METHODS ĐỀU THẤT BẠI sau {self.config['max_retries']} lần thử")
        return False
    
    def test_eye_movement_system(self):
        """Test hệ thống chuyển động mắt"""
        print("\n👁️ TESTING EYE MOVEMENT SYSTEM")
        print("=" * 50)
        
        self.eye_movement.start_animation()
        
        try:
            print("🔄 Testing various eye movement patterns...")
            
            # Test 1: Basic gaze patterns
            print("\n1. Testing basic gaze patterns...")
            gaze_patterns = [
                (0.0, 0.0),      # Center
                (0.7, 0.0),      # Right
                (-0.7, 0.0),     # Left  
                (0.0, 0.5),      # Up
                (0.0, -0.5),     # Down
                (0.5, 0.3),      # Top-right
                (-0.5, -0.3),    # Bottom-left
            ]
            
            for i, (x, y) in enumerate(gaze_patterns):
                print(f"   Pattern {i+1}: Gaze to ({x}, {y})")
                self.eye_movement.set_gaze_target(x, y)
                
                # Simulate animation for 2 seconds
                for _ in range(20):  # 10 FPS for 2 seconds
                    self.eye_movement.update_animation_frame()
                    eye_data = self.eye_movement.get_eye_data()
                    time.sleep(0.1)
                
                current_gaze = eye_data['gaze']
                print(f"   Current gaze: ({current_gaze['x']:.2f}, {current_gaze['y']:.2f})")
            
            # Test 2: Natural behaviors
            print("\n2. Testing natural behaviors (10 seconds)...")
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < 10:
                self.eye_movement.update_animation_frame()
                frame_count += 1
                
                if frame_count % 20 == 0:  # Every 2 seconds
                    eye_data = self.eye_movement.get_eye_data()
                    print(f"   Frame {frame_count}: Gaze({eye_data['gaze']['x']:.2f}, {eye_data['gaze']['y']:.2f}) "
                          f"Pupil:{eye_data['pupil_dilation']:.2f} Blink:{eye_data['blink_state']:.2f}")
                
                time.sleep(0.1)
            
            # Test 3: Forced blinks
            print("\n3. Testing forced blinks...")
            for i in range(3):
                print(f"   Blink {i+1}")
                self.eye_movement.trigger_natural_blink()
                time.sleep(1)
            
            # Test 4: Attention simulation
            print("\n4. Testing attention simulation...")
            print("   Simulating high attention...")
            self.eye_movement.current_state["attention_level"] = 1.0
            self.eye_movement.set_gaze_target(0.0, 0.0)
            
            for _ in range(20):
                self.eye_movement.update_animation_frame()
                time.sleep(0.1)
            
            print("   Simulating low attention...")
            self.eye_movement.current_state["attention_level"] = 0.3
            
            for _ in range(20):
                self.eye_movement.update_animation_frame()
                time.sleep(0.1)
            
            print("\n✅ Eye movement test completed successfully!")
            self.eye_movement.print_eye_stats()
            
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
        finally:
            self.eye_movement.stop_animation()
            
        input("\nPress Enter to return to main menu...")

    def print_detailed_stats(self):
        """In thống kê chi tiết"""
        print("\n" + "="*60)
        print("📊 THỐNG KÊ CHI TIẾT")
        print("="*60)
        
        # Overall stats
        runtime = time.time() - self.stats["session_start"]
        hours = int(runtime // 3600)
        minutes = int((runtime % 3600) // 60)
        
        print(f"⏰ Thời gian chạy: {hours}h {minutes}m")
        print(f"🎯 Tổng phát hiện LIVE: {self.stats['total_detections']}")
        print(f"✅ Skip thành công: {self.stats['total_successes']}")
        
        if self.stats['total_detections'] > 0:
            overall_rate = (self.stats['total_successes'] / self.stats['total_detections']) * 100
            print(f"📈 Tỷ lệ thành công tổng: {overall_rate:.1f}%")
        
        print(f"\n📋 CHI TIẾT THEO METHOD:")
        print("-" * 60)
        
        for method in sorted(self.skip_methods, key=lambda x: -x["success_rate"]):
            if method["attempts"] > 0:
                rate = method["success_rate"] * 100
                status = "🟢" if method["enabled"] else "🔴"
                print(f"{status} {method['name']:<20} | "
                      f"{method['successes']:>3}/{method['attempts']:<3} | "
                      f"{rate:>6.1f}% | "
                      f"Priority: {method['priority']}")
        
        print("="*60)
    
    def start_monitoring(self):
        """Bắt đầu giám sát với improved logic và eye movement"""
        print("🔍 Bắt đầu giám sát TikTok với Smart Skip Selection và Realistic Eye Movement...")
        print("⚠️ Nhấn Ctrl+C để dừng")
        
        # Start eye movement animation
        self.eye_movement.start_animation()
        
        cycle = 0
        consecutive_failures = 0
        
        try:
            while True:
                cycle += 1
                print(f"\n{'='*20} Chu kỳ #{cycle} {'='*20}")
                
                # Update eye movement animation
                self.eye_movement.update_animation_frame()
                
                # Show current eye state every 10 cycles
                if cycle % 10 == 0:
                    eye_data = self.eye_movement.get_eye_data()
                    print(f"👁️ Gaze: ({eye_data['gaze']['x']:.2f}, {eye_data['gaze']['y']:.2f}) | "
                          f"Pupil: {eye_data['pupil_dilation']:.2f} | "
                          f"Attention: {eye_data['attention_level']:.2f}")
                
                windows = self.find_tiktok_windows()
                
                if not windows:
                    print("⏳ Không tìm thấy TikTok...")
                    consecutive_failures += 1
                    
                    # Update eye movement to show boredom/waiting
                    self.eye_movement.set_gaze_target(
                        random.uniform(-0.5, 0.5), 
                        random.uniform(-0.3, 0.3)
                    )
                    
                    # Adaptive delay based on failures
                    delay = min(3 + consecutive_failures, 10)
                    print(f"⏳ Chờ {delay}s...")
                    
                    # Continue eye animation during wait
                    for _ in range(delay * 2):  # 2 updates per second
                        self.eye_movement.update_animation_frame()
                        time.sleep(0.5)
                    continue
                
                consecutive_failures = 0  # Reset counter
                
                for i, window in enumerate(windows):
                    print(f"\n🔍 Window {i+1}/{len(windows)}: {window.title}")
                    
                    # Update eye movement to show attention to window
                    window_attention_x = random.uniform(-0.3, 0.3)
                    window_attention_y = random.uniform(-0.2, 0.2)
                    self.eye_movement.set_gaze_target(window_attention_x, window_attention_y)
                    
                    screenshot = self.capture_screen(window)
                    if screenshot is None:
                        print("⚠️ Không thể chụp màn hình")
                        # Show confusion in eye movement
                        self.eye_movement.set_gaze_target(
                            random.uniform(-0.8, 0.8),
                            random.uniform(-0.4, 0.4)
                        )
                        continue
                    
                    is_live, keyword = self.detect_live_text(screenshot)
                    
                    if is_live:
                        print(f"🔴 PHÁT HIỆN LIVE! Keyword: '{keyword}'")
                        
                        # Show focused attention in eye movement
                        self.eye_movement.current_state["attention_level"] = 1.0
                        self.eye_movement.set_gaze_target(0.0, 0.0)  # Focus center
                        
                        success = self.skip_with_smart_selection(window)
                        
                        if success:
                            print("🎉 Skip thành công!")
                            # Show satisfaction/relief in eye movement
                            self.eye_movement.trigger_natural_blink()
                            self.eye_movement.set_gaze_target(
                                random.uniform(-0.2, 0.2),
                                random.uniform(-0.2, 0.2)
                            )
                        else:
                            print("😞 Skip thất bại!")
                            # Show frustration in eye movement
                            self.eye_movement.set_gaze_target(
                                random.uniform(-0.6, 0.6),
                                random.uniform(-0.4, 0.4),
                                speed_multiplier=1.5
                            )
                    else:
                        print("✅ Không phải live")
                        # Relaxed eye movement
                        self.eye_movement.set_gaze_target(
                            random.uniform(-0.4, 0.4),
                            random.uniform(-0.3, 0.3)
                        )
                
                print("⏳ Chờ 3 giây trước chu kỳ tiếp theo...")
                
                # Continue eye animation during wait
                for _ in range(6):  # 6 updates over 3 seconds
                    self.eye_movement.update_animation_frame()
                    time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n🛑 Dừng bot theo yêu cầu người dùng")
            self.eye_movement.stop_animation()
            self.print_detailed_stats()
            self.eye_movement.print_eye_stats()

def main():
    """Main function"""
    print("=" * 70)
    print("🤖 TikTok Bot - IMPROVED VERSION với EYE MOVEMENT EXTENSION")
    print("📈 Smart Skip Selection với Success Rate Tracking")
    print("👁️  Realistic Eye Movement Animation cho Background")
    print("=" * 70)
    
    try:
        bot = ImprovedTikTokBot()
        
        while True:
            print("\n🎯 MENU:")
            print("1. Bắt đầu giám sát")
            print("2. Xem thống kê chi tiết")
            print("3. Test Eye Movement System")
            print("4. Cấu hình")
            print("5. Thoát")
            
            choice = input("Chọn (1-5): ").strip()
            
            if choice == "1":
                bot.start_monitoring()
            elif choice == "2":
                bot.print_detailed_stats()
                bot.eye_movement.print_eye_stats()
            elif choice == "3":
                bot.test_eye_movement_system()
            elif choice == "4":
                print("🔧 Cấu hình sẽ được thêm trong phiên bản tiếp theo")
            elif choice == "5":
                print("👋 Tạm biệt!")
                break
            else:
                print("❌ Lựa chọn không hợp lệ")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
