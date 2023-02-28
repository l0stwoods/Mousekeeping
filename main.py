from pathlib import Path
import PySimpleGUI as psg
import time

# heavily guided by https://www.youtube.com/watch?v=pmDdUT2Txbs

'''
Functionality still to be added:
- add other config file arguments to settings menu
    - ex: bed time, sleep warning etc
- make settings menu only take valid arguments
    - just add if statements to check validity before writing
- make the sleep and work pop up windows and add images

Probably stretch goals:
- alt-text/hover text
- ???
'''

# function to return corresponding 0 if True, 1 if False
def i(bool):
    return 0 if bool else 1

def get_current_time():
    return time.strftime('%H:%M')

# funtion to get remaining time left
def get_time_left(start, length):
    return start + length - int(time.time())

def sleepwarn_window(): #sleep warning window function
    sleep_warning = int(settings['GUI']['sleep_warning'])
    layout = [
        [psg.T(f'{sleep_warning} seconds before sleep')],
        [psg.Submit()]
    ]
    window = psg.Window('bedtime soon', layout)
    event, values = window.read()
    window.close()

def settings_window(): #settings window function
    layout = [
        [psg.Text('Set Work Time', size =(15, 1)), psg.InputText(key='work_in', enable_events=True)],
        [psg.Text('Set Break Time', size =(15, 1)), psg.InputText(key='break_in', enable_events=True)],
        [psg.Submit(), psg.Cancel()]
    ]
    window = psg.Window('Settings', layout)

    while True:
        event, values = window.read()

        # close window event
        if event in (psg.WINDOW_CLOSED, "Cancel"):
            break

        # input character into work time event
        if event == 'work_in' and values['work_in'] and values['work_in'][-1] not in '0123456789':
            window['work_in'].update(values['work_in'][:-1])

        # input character into break time event
        elif event == 'break_in' and values['break_in'] and values['break_in'][-1] not in '0123456789':
            window['break_in'].update(values['break_in'][:-1])

        # submit settings event
        elif event == "Submit":
            # replaces setting only if input is given to field
            if values['work_in'] != '':
                settings['GUI']['work_period'] = values['work_in']
            if values['break_in'] != '':
                settings['GUI']['break_period'] = values['break_in']

    window.close()

def main_window():
    work_period = int(settings['GUI']['work_period']) # 25 minutes in seconds, by default
    break_period = int(settings['GUI']['break_period']) # 5 minutes in seconds, by default
    ''' smaller values, for testing
    work_period = 2
    break_period = 2
    '''
    bed_time = int(settings['GUI']['bed_time'])
    sleep_warning = int(settings['GUI']['sleep_warning'])
    periods = [work_period, break_period]
    work_time = True # True = periods[0], False = periods[1]

    time_left = work_period
    paused = True
    sleep_mode = False

    time_zone = int(settings['GUI']['time_zone'])
    print(time_zone)
    title = settings['GUI']['title']
    layout = [
        [psg.T(f"Current time: {get_current_time()}", key="current_time")],
        #this is just to see the internal time for debugging sleep timer
        [psg.T(f"Current time: {(int(time.time())+time_zone)%86400}", key="time_s")],
        [psg.T("")],
        [psg.T(f"{'Work' if work_time else 'Break'} Timer:", key='timer_name')],
        [psg.T(f"{(periods[i(work_time)] // 60):0>2}:{(periods[i(work_time)] % 60):0>2}{', Paused' if paused else ''}", key='timer')],
        [psg.B("Start Timer", key='toggle', enable_events=True), psg.B("Reset Timer"), psg.B("Settings"), psg.Cancel()]
    ]

    # initialize window object 
    window = psg.Window(title, layout)

    # main loop
    while True:
        event, values = window.read(timeout=1)
        if event in (psg.WINDOW_CLOSED, "Cancel"):
            break

        #sleepwarn event
        #finds current time in seconds and compares to stored bed time
        if (int(time.time())+time_zone+sleep_warning)%86400 == bed_time:
            sleepwarn_window()

        #sleep event
        #finds current time in seconds and compares to stored bed time
        if (int(time.time())+time_zone)%86400 == bed_time:
            #still need to add a window pop up when this goes off
            sleep_mode = True

        # start timer event
        if event == 'toggle' and paused:
            paused = False
            start_time = int(time.time())
            window['toggle'].update("Stop Timer")
            window.refresh()
            # window.read(timeout=1)

        # reset timer event
        elif event == 'Reset Timer' and not paused:
            periods = [int(settings['GUI']['work_period']), int(settings['GUI']['break_period'])]
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

        #Settings event
        elif event == 'Settings':
            settings_window()

            # update period lengths and timer with new settings
            work_period = int(settings['GUI']['work_period'])
            break_period = int(settings['GUI']['break_period'])
            time_left = get_time_left(start_time, periods[i(work_time)])

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
        window['time_s'].update(f"Current time: {(int(time.time())+time_zone)%86400}")
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