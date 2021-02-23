# TODO Added hysteresis

from time import sleep
import webbrowser
import subprocess
import os
import pkg_resources
from infi.systray import SysTrayIcon
from PIL import Image, ImageDraw, ImageFont


def on_quit_callback(_):
    global main_loop
    main_loop = False


def resource_path(relative_path):
    try:
        # Get PyInstaller temp path
        base_path = os.sys._MEIPASS
    except Exception:
        # Get current path
        base_path = os.getcwd() + "\lib"

    return base_path + relative_path


def headset_status():
    global r, g, b
    global pos
    global font_type

    # Get headset data
    output = subprocess.check_output(resource_path('\headsetcontrol.exe') + ' -bc', shell=True,
                                     stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL) or False

    # Not connected
    if not output:
        systray_output = -1

    # Charging or 100%
    elif int(output) < 0 or int(output) == 100:
        pos = 0
        r, g, b = 255, 255, 0
        systray_output = ""
        if int(output) == 100:
            b = 255

        font_type = ImageFont.truetype("holomdl2.ttf", 50)

    # On Battery
    else:
        pos = 10
        systray_output = int(output)

        # Set color based on battery level
        # Red
        if systray_output <= 15:
            r, g, b = 255, 0, 0
        # Yellow
        elif systray_output <= 25:
            r, g, b = 255, 255, 0
        # White
        else:
            r, g, b = 255, 255, 255

        font_type = ImageFont.truetype("seguisb.ttf", 38)

    return systray_output


def about(_):
    webbrowser.open('https://github.com/zampierilucas/HeadsetControl-SystemTray')  # Go to example.com


def reload(_):
    global loop_time
    loop_time = 0


def percentage_systray(systray):
    global font_type
    global loop_time
    font_type = ImageFont.truetype("seguisb.ttf", 37)

    while main_loop:
        if loop_time <= 0:
            # Create image
            img = Image.new('RGBA', (50, 50), color=(r, g, b, 0))
            systray_icon = ImageDraw.Draw(img)
            systray_icon.rectangle([(0, 100), (50, 50)], fill=(39, 112, 229), outline=None)

            result = headset_status()

            # Headset not connected
            if result == -1:
                systray.shutdown()

            # Update state
            else:
                systray.start()

                # add text to the image
                systray_icon.text((pos, -1), f"{result}", fill=(r, g, b), font=font_type)

                img.save(image)
                systray.update(icon=image)

            loop_time = 60
        else:
            loop_time -= 1
            sleep(1)


r, g, b = 255, 255, 255  # Icon Color
pos = 10  # Center icon
main_loop = True
loop_time = 0  # Sleep time, between updated
font_type = ImageFont.truetype("seguisb.ttf", 37)  # default font
image = resource_path("\pil_text.ico")  # Systray icon tmp path

menu_options = (("About", None, about), ("Reload", None, reload),)
systray_module = SysTrayIcon(image, "HeadsetControl-SystemTray", menu_options, on_quit=on_quit_callback)
percentage_systray(systray_module)

systray_module.shutdown()
