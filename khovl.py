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
        print("🚀 Khởi tạo TikTok Bot Improved...")
        
        self.modules = safe_import()
        
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
                
                print("⏳ Chờ 3 giây trước chu kỳ tiếp theo...")
                time.sleep(3)
                
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
