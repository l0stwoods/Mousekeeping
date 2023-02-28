from pathlib import Path
import PySimpleGUI as psg
import time

# heavily guided by https://www.youtube.com/watch?v=pmDdUT2Txbs

# function to return corresponding 0 if True, 1 if False
def i(bool):
    return 0 if bool else 1

def get_current_time():
    return time.strftime('%H:%M')

# funtion to get remaining time left
def get_time_left(start, length):
    return start + length - int(time.time())

def main_window():

    work_period = 1500 # 25 minutes in seconds, by default
    break_period = 300 # 5 minutes in seconds, by default
    ''' smaller values, for testing
    work_period = 2
    break_period = 2
    '''
    periods = [work_period, break_period]
    work_time = True # True = periods[0], False = periods[1]

    time_left = work_period
    paused = True

    title = "Mousekeeping"
    layout = [
        [psg.T(f"Current time: {get_current_time()}", key="current_time")],
        [psg.T("")],
        [psg.T(f"{'Work' if work_time else 'Break'} Timer:", key='timer_name')],
        [psg.T(f"{(periods[i(work_time)] // 60):0>2}:{(periods[i(work_time)] % 60):0>2}{', Paused' if paused else ''}", key='timer')],
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
            time_left = get_time_left(start_time, periods[i(work_time)])
            work_time = True
            # window.refresh()
            # unsure if reset button should also pause the timer 

        # stop timer event
        elif event == 'toggle' and not paused:
            paused = True
            window['toggle'].update("Restart Timer")
            window.refresh()

        # update timer if not paused
        if not paused: 
            time_left = get_time_left(start_time, periods[i(work_time)])

            # switch phases from work -> break or break -> work
            if time_left <= 0:  
                work_time = not work_time
                paused = True
                window['toggle'].update("Start Timer")
                start_time = int(time.time())
                time_left = get_time_left(start_time, periods[i(work_time)])

        window['timer'].update(f"{(time_left // 60):0>2}:{(time_left % 60):0>2}{', Paused' if paused else ''}")
        window['current_time'].update(f"Current time: {get_current_time()}")
        window['timer_name'].update(f"{'Work' if work_time else 'Break'} Timer:")

    window.close()

if __name__ == "__main__":  # main code, runs on load

    # get path for settings ini file 
    SETTINGS_PATH = Path.cwd()
    settings = psg.UserSettings(
        path=SETTINGS_PATH, filename='config.ini', use_config_file=True, convert_bools_and_none=True
    )

    # fetch ini file settings
    theme = settings['GUI']['theme']
    font_family = settings['GUI']['font_family']
    font_size = settings['GUI']['font_size']

    psg.theme(theme)
    psg.set_options(font=(font_family, font_size))
    main_window()