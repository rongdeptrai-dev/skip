#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Bot - Cải thiện hiệu quả skip
"""

import os
import time
import logging
import cv2
import numpy as np
import subprocess
import json
from typing import List, Optional
import random

def safe_import():
    """Import các thư viện cần thiết"""
    modules = {}
    
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.05  # Minimal pause for smooth operation
        # Optimize for macro recording
        pyautogui.MINIMUM_DURATION = 0.1
        pyautogui.MINIMUM_SLEEP = 0.05
        modules['pyautogui'] = pyautogui
        print("✅ pyautogui: OK (optimized for smooth operation)")
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
        print("🚀 Khởi tạo TikTok Bot Improved...")
        
        self.modules = safe_import()
        
        # Cấu hình skip methods với độ ưu tiên - optimized order
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
                "name": "combination_method", 
                "priority": 3, 
                "enabled": True,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            },
            {
                "name": "mouse_click_next", 
                "priority": 4, 
                "enabled": True,
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            },
            {
                "name": "external_macro", 
                "priority": 5, 
                "enabled": True,  # Enabled for advanced automation
                "success_rate": 0.0,
                "attempts": 0,
                "successes": 0
            }
        ]
        
        # Cấu hình - Optimized for smoother operation
        self.config = {
            "max_retries": 3,           # Reduced for faster response
            "retry_delay": 0.1,         # Faster retry for smoother operation
            "success_delay": 0.8,       # Reduced delay after success
            "focus_attempts": 2,        # Fewer focus attempts
            "verification_enabled": True,
            "adaptive_timing": True,
            "smooth_mode": True,        # New flag for macro compatibility
            "mouse_speed": 0.2          # Fast mouse movements for macros
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
        """Đảm bảo window được focus đúng cách - optimized for smooth operation"""
        for attempt in range(attempts):
            try:
                # Quick focus sequence for macro compatibility
                window.restore()  # Restore if minimized
                window.activate()
                
                # Minimal delay for smooth operation
                if self.config.get("smooth_mode", False):
                    time.sleep(0.05)
                else:
                    time.sleep(0.2)
                
                # Quick center click for focus
                if self.modules['pyautogui']:
                    center_x = window.left + window.width // 2
                    center_y = window.top + window.height // 2
                    self.modules['pyautogui'].click(center_x, center_y, duration=0.1)
                    time.sleep(0.05)
                
                # Quick verification
                gw = self.modules['pygetwindow']
                try:
                    active_window = gw.getActiveWindow()
                    if active_window and active_window.title == window.title:
                        if attempt == 0:  # Only print on first successful attempt
                            print(f"✅ Window focused quickly")
                        return True
                except:
                    pass  # Continue to retry if verification fails
                
                if attempt < attempts - 1:  # Don't wait on last attempt
                    time.sleep(0.1)
                
            except Exception as e:
                if attempt == attempts - 1:  # Only log error on final attempt
                    print(f"❌ Focus error: {e}")
        
        return False  # Failed after all attempts
    
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
        """Verify xem skip có thành công không - optimized for speed"""
        if not self.config["verification_enabled"]:
            return True
        
        try:
            # Faster verification timing
            wait_time = 0.6 if self.config.get("smooth_mode", False) else 1.0
            time.sleep(wait_time)
            
            post_screenshot = self.capture_screen(window)
            
            if post_screenshot is None:
                return False
            
            # Quick comparison for faster response
            if pre_screenshot is not None:
                # Use smaller regions for faster comparison
                h, w = pre_screenshot.shape[:2]
                # Focus on center area where most changes occur
                y1, y2 = h//4, 3*h//4
                x1, x2 = w//4, 3*w//4
                
                pre_region = cv2.cvtColor(pre_screenshot[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                post_region = cv2.cvtColor(post_screenshot[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                
                # Calculate difference in focused region
                diff = cv2.absdiff(pre_region, post_region)
                diff_percentage = (cv2.countNonZero(diff) / (diff.shape[0] * diff.shape[1])) * 100
                
                # Lower threshold for faster detection
                if diff_percentage > 15:
                    print(f"✅ Skip verified: {diff_percentage:.1f}% change")
                    return True
                else:
                    print(f"❌ Skip failed: only {diff_percentage:.1f}% change")
                    return False
            
            # Fallback: quick live text check
            is_live, _ = self.detect_live_text(post_screenshot)
            success = not is_live
            
            if success:
                print("✅ Skip verified: no LIVE detected")
            else:
                print("❌ Skip failed: still LIVE")
            
            return success
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
    
    # Skip Methods
    def skip_method_enhanced_keyboard(self, window, screenshot):
        """Enhanced keyboard method optimized for macro recording"""
        if not self.modules['pyautogui']:
            return False
        
        try:
            pyautogui = self.modules['pyautogui']
            
            # Ensure focus with minimal attempts
            if not self.ensure_window_focus(window, attempts=1):
                return False
            
            # Simplified keyboard methods for macro compatibility
            keyboard_actions = [
                'down',      # Primary navigation key
                'space',     # Alternative skip key
                'right',     # Horizontal navigation
                'pagedown'   # Page navigation
            ]
            
            for i, key in enumerate(keyboard_actions):
                print(f"   🔄 Keyboard: {key}")
                
                # Quick re-focus if needed
                if i > 0:
                    window.activate()
                    time.sleep(0.02)
                
                # Execute key press - optimized for macros
                pyautogui.press(key)
                
                # Quick verification with shorter wait
                time.sleep(0.3)
                if self.verify_skip_success(window, screenshot):
                    print(f"   ✅ Keyboard {key} successful")
                    return True
                
                print(f"   ❌ Keyboard {key} failed")
                
                # Minimal delay between attempts
                if i < len(keyboard_actions) - 1:
                    time.sleep(0.1)
            
            return False
            
        except Exception as e:
            print(f"❌ Enhanced keyboard error: {e}")
            return False
    
    def skip_method_mouse_swipe_up(self, window, screenshot):
        """Mouse swipe up method optimized for macro recording"""
        if not self.modules['pyautogui']:
            return False
        
        try:
            pyautogui = self.modules['pyautogui']
            
            if not self.ensure_window_focus(window):
                return False
            
            # Calculate swipe coordinates
            center_x = window.left + window.width // 2
            center_y = window.top + window.height // 2
            
            # Optimized swipe patterns for macro compatibility
            swipe_patterns = [
                # Quick swipe - best for macros
                {
                    "start_y": center_y + 120,
                    "end_y": center_y - 120,
                    "duration": self.config.get("mouse_speed", 0.2)
                },
                # Medium swipe
                {
                    "start_y": center_y + 150,
                    "end_y": center_y - 150,
                    "duration": 0.25
                },
                # Strong swipe
                {
                    "start_y": center_y + 180,
                    "end_y": center_y - 180,
                    "duration": 0.3
                }
            ]
            
            for i, pattern in enumerate(swipe_patterns):
                print(f"   🔄 Swipe pattern {i+1}")
                
                # Quick center click for focus
                pyautogui.click(center_x, center_y, duration=0.05)
                time.sleep(0.05)
                
                # Perform optimized swipe
                pyautogui.drag(
                    center_x, pattern["start_y"],
                    center_x, pattern["end_y"],
                    duration=pattern["duration"],
                    button='left'
                )
                
                # Quick verification
                time.sleep(0.5)
                if self.verify_skip_success(window, screenshot):
                    print(f"   ✅ Swipe pattern {i+1} successful")
                    return True
                
                print(f"   ❌ Swipe pattern {i+1} failed")
                
                # Minimal delay between patterns
                if i < len(swipe_patterns) - 1:
                    time.sleep(0.15)
            
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
        """Combination method optimized for smooth operation"""
        print("   🔄 Trying optimized combination method")
        
        try:
            if not self.modules['pyautogui']:
                return False
                
            pyautogui = self.modules['pyautogui']
            center_x = window.left + window.width // 2
            center_y = window.top + window.height // 2
            
            # Combination 1: Quick Click + Keyboard (macro-friendly)
            if self.ensure_window_focus(window):
                pyautogui.click(center_x, center_y, duration=0.05)
                time.sleep(0.05)
                pyautogui.press('down')
                time.sleep(0.4)
                
                if self.verify_skip_success(window, screenshot):
                    print("   ✅ Quick combination successful")
                    return True
            
            # Combination 2: Double swipe (for stubborn content)
            pyautogui.drag(center_x, center_y + 80, center_x, center_y - 80, duration=0.15)
            time.sleep(0.05)
            pyautogui.drag(center_x, center_y + 120, center_x, center_y - 120, duration=0.2)
            time.sleep(0.5)
            
            if self.verify_skip_success(window, screenshot):
                print("   ✅ Double swipe combination successful") 
                return True
            
            # Combination 3: Multi-key sequence
            keys = ['space', 'down', 'right']
            for key in keys:
                pyautogui.press(key)
                time.sleep(0.08)
            
            time.sleep(0.4)
            if self.verify_skip_success(window, screenshot):
                print("   ✅ Multi-key combination successful")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Combination method error: {e}")
            return False
    
    def skip_method_external_macro(self, window, screenshot):
        """External macro method for advanced automation"""
        print("   🔄 Trying external macro method")
        
        try:
            # Method 1: Try to execute external macro script if available
            macro_scripts = [
                "tiktok_skip_macro.ahk",  # AutoHotkey script
                "tiktok_skip.py",         # Python macro script
                "skip_macro.exe"          # Compiled macro
            ]
            
            for script in macro_scripts:
                if os.path.exists(script):
                    print(f"   📄 Found macro script: {script}")
                    try:
                        if script.endswith('.ahk'):
                            # AutoHotkey script
                            result = subprocess.run(['autohotkey', script], 
                                                   timeout=3, capture_output=True)
                        elif script.endswith('.py'):
                            # Python script
                            result = subprocess.run(['python', script], 
                                                   timeout=3, capture_output=True)
                        elif script.endswith('.exe'):
                            # Executable
                            result = subprocess.run([script], 
                                                   timeout=3, capture_output=True)
                        
                        if result.returncode == 0:
                            print(f"   ✅ External macro executed successfully")
                            time.sleep(0.5)
                            return self.verify_skip_success(window, screenshot)
                        
                    except subprocess.TimeoutExpired:
                        print(f"   ⚠️ Macro script timeout: {script}")
                    except Exception as e:
                        print(f"   ❌ Macro script error: {e}")
            
            # Method 2: Simulate advanced macro sequence
            if self.modules['pyautogui']:
                pyautogui = self.modules['pyautogui']
                
                # Advanced sequence: Click + Multiple keys + Swipe
                center_x = window.left + window.width // 2
                center_y = window.top + window.height // 2
                
                # Focus click
                pyautogui.click(center_x, center_y, duration=0.1)
                time.sleep(0.05)
                
                # Key sequence
                pyautogui.press('space')
                time.sleep(0.1)
                pyautogui.press('down')
                time.sleep(0.1)
                
                # Small swipe
                pyautogui.drag(center_x, center_y + 50, center_x, center_y - 50, duration=0.15)
                
                time.sleep(0.5)
                if self.verify_skip_success(window, screenshot):
                    print("   ✅ Macro sequence successful")
                    return True
            
            print("   ❌ External macro method failed")
            return False
            
        except Exception as e:
            print(f"❌ External macro error: {e}")
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
                
                # Optimized adaptive delay for smooth operation
                if self.config["adaptive_timing"]:
                    # Faster delays for better responsiveness
                    base_delay = self.config["retry_delay"]
                    success_factor = max(0.1, method["success_rate"])
                    delay = base_delay * (0.5 + (1 - success_factor) * 0.5)
                    time.sleep(min(delay, 0.5))  # Cap at 0.5s max
                else:
                    time.sleep(self.config["retry_delay"])
            
            # Delay between retry attempts
            if attempt < self.config["max_retries"] - 1:
                print(f"⏳ Chờ trước lần thử tiếp theo...")
                time.sleep(0.5)
        
        print(f"❌ TẤT CẢ METHODS ĐỀU THẤT BẠI sau {self.config['max_retries']} lần thử")
        return False
    
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
        """Bắt đầu giám sát với improved logic"""
        print("🔍 Bắt đầu giám sát TikTok với Smart Skip Selection...")
        print("⚠️ Nhấn Ctrl+C để dừng")
        
        cycle = 0
        consecutive_failures = 0
        
        try:
            while True:
                cycle += 1
                print(f"\n{'='*20} Chu kỳ #{cycle} {'='*20}")
                
                windows = self.find_tiktok_windows()
                
                if not windows:
                    print("⏳ Không tìm thấy TikTok...")
                    consecutive_failures += 1
                    
                    # Adaptive delay based on failures
                    delay = min(3 + consecutive_failures, 10)
                    print(f"⏳ Chờ {delay}s...")
                    time.sleep(delay)
                    continue
                
                consecutive_failures = 0  # Reset counter
                
                for i, window in enumerate(windows):
                    print(f"\n🔍 Window {i+1}/{len(windows)}: {window.title}")
                    
                    screenshot = self.capture_screen(window)
                    if screenshot is None:
                        print("⚠️ Không thể chụp màn hình")
                        continue
                    
                    is_live, keyword = self.detect_live_text(screenshot)
                    
                    if is_live:
                        print(f"🔴 PHÁT HIỆN LIVE! Keyword: '{keyword}'")
                        success = self.skip_with_smart_selection(window)
                        
                        if success:
                            print("🎉 Skip thành công!")
                        else:
                            print("😞 Skip thất bại!")
                    else:
                        print("✅ Không phải live")
                
                print("⏳ Chờ 2 giây trước chu kỳ tiếp theo... (optimized)")
                time.sleep(2)  # Reduced from 3 seconds for faster response
                
        except KeyboardInterrupt:
            print("\n🛑 Dừng bot theo yêu cầu người dùng")
            self.print_detailed_stats()

def main():
    """Main function"""
    print("=" * 70)
    print("🤖 TikTok Bot - IMPROVED VERSION")
    print("📈 Smart Skip Selection với Success Rate Tracking")
    print("=" * 70)
    
    try:
        bot = ImprovedTikTokBot()
        
        while True:
            print("\n🎯 MENU:")
            print("1. Bắt đầu giám sát")
            print("2. Xem thống kê chi tiết")
            print("3. Cấu hình")
            print("4. Thoát")
            
            choice = input("Chọn (1-4): ").strip()
            
            if choice == "1":
                bot.start_monitoring()
            elif choice == "2":
                bot.print_detailed_stats()
            elif choice == "3":
                print("🔧 Cấu hình sẽ được thêm trong phiên bản tiếp theo")
            elif choice == "4":
                print("👋 Tạm biệt!")
                break
            else:
                print("❌ Lựa chọn không hợp lệ")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
