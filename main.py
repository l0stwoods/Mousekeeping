from pathlib import Path
import PySimpleGUI as psg
import time

# heavily guided by https://www.youtube.com/watch?v=pmDdUT2Txbs

def main_window():

    work_period = 1500 # 25 minutes in seconds  
    time_left = 1500
    paused = True

    title = "Mousekeeping"
    layout = [
        [psg.T("Welcome to Mousekeeping!")],
        [psg.T("")],
        [psg.T("Work Timer:")],
        [psg.T(f"{(work_period // 60):0>2}:{(work_period % 60):0>2}, {paused}", key='timer')],
        [psg.B("Start Timer", key='toggle', enable_events=True), psg.B("Reset Timer"), psg.Cancel()]
    ]

    # initialize window object 
    window = psg.Window(title, layout)

    # main loop
    while True:
        event, values = window.read(timeout=1)
        if event in (psg.WINDOW_CLOSED, "Cancel"):
            break

        # start timer event
        if event == 'toggle' and paused:
            paused = False
            start_time = int(time.time())
            window['toggle'].update("Stop Timer")
            window.refresh()
            # window.read(timeout=1)

        # reset timer event
        elif event == 'Reset Timer' and not paused:
            start_time = int(time.time())
            time_left = start_time + work_period - int(time.time())
            # window.refresh()
            # unsure if reset button should also pause the timer 

        # stop timer event
        elif event == 'toggle' and not paused:
            paused = True
            window['toggle'].update("Restart Timer")
            window.refresh()

        if not paused: # update timer if not paused
            time_left = start_time + work_period - int(time.time())

        window['timer'].update(f"{(time_left // 60):0>2}:{(time_left % 60):0>2}, {paused}")

    window.close()

if __name__ == "__main__":  # main code, runs on load
    # get path for settings ini file 
    SETTINGS_PATH = Path.cwd()
    settings = psg.UserSettings(
        path=SETTINGS_PATH, filename='config.ini', use_config_file=True, convert_bools_and_none=True
    )

    theme = settings['GUI']['theme']
    font_family = settings['GUI']['font_family']
    font_size = settings['GUI']['font_size']

    psg.theme(theme)
    psg.set_options(font=(font_family, font_size))
    main_window()