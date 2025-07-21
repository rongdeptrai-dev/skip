#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eye Movement Demo - Visual demonstration of realistic eye animation
Showcases the enhanced eye movement system for background extensions
"""

import os
import time
import math
import random
from khovl import RealisticEyeMovement

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_ascii_eyes(gaze_x, gaze_y, pupil_dilation, blink_state):
    """Draw ASCII art eyes based on eye state"""
    
    # Calculate pupil position within eye
    pupil_x_offset = int(gaze_x * 2)  # -2 to 2
    pupil_y_offset = int(gaze_y * 1)  # -1 to 1
    
    # Pupil character based on dilation
    if pupil_dilation < 0.7:
        pupil_char = "·"  # Small pupil
    elif pupil_dilation < 1.3:
        pupil_char = "●"  # Normal pupil
    else:
        pupil_char = "◉"  # Dilated pupil
    
    # Eye structure based on blink state
    if blink_state < 0.1:  # Nearly closed
        left_eye = "━━━━━"
        right_eye = "━━━━━"
    elif blink_state < 0.3:  # Partially closed
        left_eye = "─────"
        right_eye = "─────"
    else:  # Open eyes
        # Create eye grid (5x3)
        eye_grid = [
            ["╭", "─", "─", "─", "╮"],
            ["│", " ", " ", " ", "│"],
            ["╰", "─", "─", "─", "╯"]
        ]
        
        # Place pupil in the eye
        pupil_pos_x = 2 + pupil_x_offset  # Center at 2, offset by gaze
        pupil_pos_y = 1 + pupil_y_offset  # Center at 1, offset by gaze
        
        # Keep pupil within bounds
        pupil_pos_x = max(1, min(3, pupil_pos_x))
        pupil_pos_y = max(1, min(1, pupil_pos_y))
        
        # Place pupil
        eye_grid[pupil_pos_y][pupil_pos_x] = pupil_char
        
        # Convert to strings
        left_eye = "".join(eye_grid[0]) + "\n" + "".join(eye_grid[1]) + "\n" + "".join(eye_grid[2])
        right_eye = left_eye  # Same for both eyes
    
    return left_eye, right_eye

def create_eye_visualization(eye_data):
    """Create a visual representation of the eye state"""
    gaze = eye_data['gaze']
    gaze_x, gaze_y = gaze['x'], gaze['y']
    pupil_dilation = eye_data['pupil_dilation']
    blink_state = eye_data['blink_state']
    attention = eye_data['attention_level']
    fatigue = eye_data['fatigue_level']
    
    left_eye, right_eye = draw_ascii_eyes(gaze_x, gaze_y, pupil_dilation, blink_state)
    
    # Create the complete visualization
    if blink_state < 0.3:  # Eyes closed or nearly closed
        display = f"""
    ╔══════════════════════════════════════╗
    ║      REALISTIC EYE ANIMATION         ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║        {left_eye}      {right_eye}        ║
    ║                                      ║
    ╠══════════════════════════════════════╣
    ║ Gaze: ({gaze_x:5.2f}, {gaze_y:5.2f})          ║
    ║ Pupil Dilation: {pupil_dilation:4.2f}              ║
    ║ Blink State: {blink_state:6.2f}               ║
    ║ Attention: {attention:8.2f}                ║
    ║ Fatigue: {fatigue:10.2f}                  ║
    ╚══════════════════════════════════════╝
        """
    else:  # Eyes open
        eye_lines_left = left_eye.split('\n')
        eye_lines_right = right_eye.split('\n')
        
        display = f"""
    ╔══════════════════════════════════════╗
    ║      REALISTIC EYE ANIMATION         ║
    ╠══════════════════════════════════════╣
    ║                                      ║
    ║      {eye_lines_left[0]}      {eye_lines_right[0]}      ║
    ║      {eye_lines_left[1]}      {eye_lines_right[1]}      ║
    ║      {eye_lines_left[2]}      {eye_lines_right[2]}      ║
    ║                                      ║
    ╠══════════════════════════════════════╣
    ║ Gaze: ({gaze_x:5.2f}, {gaze_y:5.2f})          ║
    ║ Pupil Dilation: {pupil_dilation:4.2f}              ║
    ║ Blink State: {blink_state:6.2f}               ║
    ║ Attention: {attention:8.2f}                ║
    ║ Fatigue: {fatigue:10.2f}                  ║
    ╚══════════════════════════════════════╝
        """
    
    return display

def run_demo():
    """Run the eye movement demonstration"""
    print("👁️ REALISTIC EYE MOVEMENT DEMO")
    print("=" * 50)
    print("Demonstrating smooth, natural eye animations")
    print("Press Ctrl+C to stop")
    print()
    
    # Initialize eye movement system
    eye_movement = RealisticEyeMovement()
    eye_movement.start_animation()
    
    try:
        frame_count = 0
        demo_phases = [
            "Natural random gaze movements",
            "Focused attention simulation", 
            "Fatigue and tired behavior",
            "Quick alert movements",
            "Relaxed drifting motion"
        ]
        
        phase_duration = 100  # frames per phase
        current_phase = 0
        
        while True:
            # Update eye animation
            eye_movement.update_animation_frame()
            
            # Change behavior based on demo phase
            if frame_count % phase_duration == 0:
                phase_name = demo_phases[current_phase % len(demo_phases)]
                print(f"\n🎬 Demo Phase: {phase_name}")
                
                if current_phase % 5 == 0:  # Natural movements
                    pass  # Let natural behavior take over
                elif current_phase % 5 == 1:  # Focused attention
                    eye_movement.current_state["attention_level"] = 1.0
                    eye_movement.set_gaze_target(0.0, 0.0)
                elif current_phase % 5 == 2:  # Fatigue
                    eye_movement.current_state["fatigue_level"] = 0.7
                    eye_movement.current_state["attention_level"] = 0.4
                elif current_phase % 5 == 3:  # Alert movements
                    eye_movement.current_state["attention_level"] = 1.0
                    eye_movement.current_state["fatigue_level"] = 0.0
                    # Quick gaze changes
                    if frame_count % 20 == 0:
                        eye_movement.set_gaze_target(
                            random.uniform(-0.8, 0.8),
                            random.uniform(-0.5, 0.5),
                            speed_multiplier=2.0
                        )
                else:  # Relaxed drifting
                    eye_movement.current_state["attention_level"] = 0.6
                    eye_movement.current_state["fatigue_level"] = 0.2
                
                current_phase += 1
            
            # Special events
            if frame_count % 150 == 0:  # Force blink every 15 seconds
                eye_movement.trigger_natural_blink()
            
            if frame_count % 80 == 0:  # Change gaze target
                eye_movement.set_gaze_target(
                    random.uniform(-0.6, 0.6),
                    random.uniform(-0.4, 0.4)
                )
            
            # Get current eye data
            eye_data = eye_movement.get_eye_data()
            
            # Clear screen and draw
            clear_screen()
            
            # Create and display visualization
            visualization = create_eye_visualization(eye_data)
            print(visualization)
            
            # Show frame info
            print(f"Frame: {frame_count:4d} | FPS: ~10 | Phase: {demo_phases[current_phase % len(demo_phases)]}")
            
            frame_count += 1
            time.sleep(0.1)  # ~10 FPS
            
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
        eye_movement.stop_animation()
        eye_movement.print_eye_stats()
        print("\n✅ Eye movement demo completed!")

if __name__ == "__main__":
    run_demo()