# DO NOT REMOVE: Original author credit
# Original Author: https://github.com/littleflo/Shellshock-Live-AutoAim?tab=MIT-1-ov-file


import math
import time
from pynput import mouse, keyboard

# ========== Physics ==========
def calc_velocity(distancex, distancey, angle):
    g = -379.106
    q = 0.0518718
    v0 = -2 / (g * q) * math.sqrt(
        (-distancex * distancex * g)
        / (2 * math.cos(math.radians(angle)) ** 2 * (math.tan(math.radians(angle)) * distancex - distancey))
    )
    return v0

def calc_optimal(diffx, diffy, mode="standard"):
    smallest_velocity = float("inf")
    best_angle = 0

    if mode == "standard":
        angle_range = range(1, 90)
    elif mode == "high":
        angle_range = range(60, 90)
    elif mode == "ultra":
        angle_range = range(80, 90)
    else:
        angle_range = range(1, 90)

    for a in angle_range:
        try:
            v0 = calc_velocity(diffx, diffy, a)
            if v0 < smallest_velocity:
                smallest_velocity = v0
                best_angle = a
        except Exception:
            pass
    return best_angle, smallest_velocity

# ========== State ==========
clicks = []
start_point = None
end_point = None
current_angle = 0
current_power = 0
mode = "standard"
listening_for_clicks = False

kb_ctrl = keyboard.Controller()

START_POWER = 100
START_ANGLE = 90

def tap_key(key, times, delay=0.005):  # ⚡ faster keypress delay
    times = int(round(times))
    if times == 0:
        return
    for _ in range(abs(times)):
        kb_ctrl.press(key)
        kb_ctrl.release(key)
        time.sleep(delay)

# ========== Aiming ==========
def perform_aiming():
    global start_point, end_point, current_power, current_angle

    if not start_point or not end_point:
        print("No target selected.")
        return

    direction = "right" if end_point[0] > start_point[0] else "left"
    print(f"Aiming {direction} -> Power {current_power}, Angle {current_angle} (mode {mode})")

    diff_power = current_power - START_POWER
    diff_angle = current_angle - START_ANGLE

    angle_key = keyboard.Key.right if direction == "right" else keyboard.Key.left

    # Adjust power
    if diff_power > 0:
        tap_key(keyboard.Key.up, diff_power)
    elif diff_power < 0:
        tap_key(keyboard.Key.down, diff_power)

    # Adjust angle
    tap_key(angle_key, abs(diff_angle))

    print(f"✅ Aiming complete → Direction: {direction.upper()} | Power: {current_power} | Angle: {current_angle}\n")

# ========== Mouse handler ==========
def on_click(x, y, button, pressed):
    global clicks, start_point, end_point, current_angle, current_power, listening_for_clicks
    if not listening_for_clicks:
        return
    if pressed:
        clicks.append((x, y))
        print(f"Clicked at: ({x}, {y})")

        if len(clicks) == 2:
            start_point, end_point = clicks
            clicks.clear()

            dx = abs(end_point[0] - start_point[0])
            dy = -end_point[1] + start_point[1]
            angle, power = calc_optimal(dx, dy, mode)
            current_angle = int(round(angle))
            current_power = int(round(power))

            listening_for_clicks = False
            print(f"\nMode: {mode.upper()}  →  Power: {current_power}, Angle: {current_angle}")
            print("Press J to prepare, then Y to execute.\n")

# ========== Keyboard handler ==========
pending = None
confirming = False
mouse_listener = None

def on_press(key):
    global listening_for_clicks, start_point, end_point, pending, confirming, mode, mouse_listener

    if key == keyboard.Key.esc:
        print("Exiting...")
        if mouse_listener:
            mouse_listener.stop()
        return False

    if hasattr(key, "char"):
        c = key.char.lower()

        if c == '1':
            mode = "standard"; print("Mode: STANDARD"); return
        if c == '2':
            mode = "high"; print("Mode: HIGH"); return
        if c == '3':
            mode = "ultra"; print("Mode: ULTRA"); return

        if c == 'j':
            if not start_point or not end_point:
                start_point = None; end_point = None; listening_for_clicks = True
                print("Click start, then target...")
            else:
                pending = (current_power, current_angle)
                print(f"\nReady to aim at Power {current_power}, Angle {current_angle}. Press Y to confirm or N to cancel.")
                confirming = True

        if c == 'y' and confirming and pending:
            perform_aiming()
            start_point = None; end_point = None
            confirming = False; pending = None
            listening_for_clicks = False

        if c == 'n' and confirming:
            print("Cancelled. Press J to select again.")
            confirming = False; pending = None
            start_point = None; end_point = None
            listening_for_clicks = False

        if c == 'r':
            print("Resetting selections.")
            clicks.clear()
            start_point = None; end_point = None
            confirming = False; pending = None
            listening_for_clicks = False

# ========== Run ==========
print("Controls:")
print("  1=Standard  2=High  3=Ultra")
print("  J=start clicks / confirm shot")
print("  Y=execute shot, N=cancel, R=reset, ESC=quit\n")
print(f"  Place power={START_POWER}, angle={START_ANGLE} before aiming.\n")

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

with keyboard.Listener(on_press=on_press) as kl:
    kl.join()

# DO NOT REMOVE: Original author credit
# Original Author: https://github.com/littleflo/Shellshock-Live-AutoAim?tab=MIT-1-ov-file