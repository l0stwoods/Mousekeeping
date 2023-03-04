from pathlib import Path
import PySimpleGUI as psg
import time

ANIMALS = ['Mouse', 'Otter']

# heavily guided by https://www.youtube.com/watch?v=pmDdUT2Txbs

'''
Functionality still to be added:
- make the sleep pop up window
    - prevent mouse movement
- add images

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

#converts hr:min to seconds could maybe implement am/pm instead of military time
def timetosec(t):
    t_array = t.split(':')
    print(t_array)
    sec = int(t_array[0]) * 3600 + int(t_array[1]) * 60
    return sec

# does the reverse of timetosec, returns HH:MM
def sectotime(s):
    hour = (s // 60) // 60
    mins = (s // 60) % 60 
    return f"{hour:0>2}:{mins:0>2}"

def sleep_window(animal, wake_time):
    global ANIMALS

    if animal == 0:
        animal_sleep_image = "images//mouse//mouse_asleep.png"
    else:
        animal_sleep_image = "images//otter//otter_asleep.png"

    wake_timef = sectotime(wake_time) # formatted version of wake_time
    layout = [
        [psg.T(f"Current Time: {get_current_time()}", key="current_time")],
        [psg.T(ANIMALS[animal] + f" is asleep until {wake_timef}.")],
        [psg.Image(animal_sleep_image)],
        [psg.T("If you do work you'll wake them!")],
    ]
    window = psg.Window(
        'Bedtime!', layout, 
        keep_on_top=True, grab_anywhere=True, no_titlebar=True
    )

    while True:
        event, values = window.read(timeout=10)
        if get_current_time() == wake_timef:
            break
        if event == psg.WINDOW_CLOSED:
            break
        window['current_time'].update(f"Current Time: {get_current_time()}")

    window.close()


def sleepwarn_window(animal, sleep_warning): #sleep warning window function
    global ANIMALS
    # not sure if this would be better as a blocking window, or a non-blocking popup that doesn't update

    # records current time the window pops up
    start = int(time.time())
    i = int(time.time()) - start

    if animal == 0:
        sleepy_image = "images//mouse//mouse_tired.png"
    else:
        sleepy_image = "images//otter//otter_tired.png"

    layout = [
        [psg.T(f'{sleep_warning - i} seconds before {ANIMALS[animal]} goes to sleep!', key='sleep_warning')],
         [psg.Image(sleepy_image)],
         [psg.T("Finish up what you have to before bedtime!")]
    ]
    window = psg.Window(
        'Bedtime Reminder', layout, 
        keep_on_top=True, grab_anywhere=True, no_titlebar=True
    )
    while True:
        event, values = window.read(timeout=5)
        if i == int(time.time()) - start:
            continue
        i = int(time.time()) - start
        if i >= sleep_warning or event == psg.WINDOW_CLOSED:
            break
        else:
            window['sleep_warning'].update(f'{sleep_warning - i} seconds before {ANIMALS[animal]} goes to sleep!')
    
    window.close()


def main_window():
    global ANIMALS

    # retrieve variables from config file 
    work_period = int(settings['GUI']['work_period']) 
    break_period = int(settings['GUI']['break_period']) 
    bed_time = int(settings['GUI']['bed_time'])
    wake_time = int(settings['GUI']['wake_time'])
    sleep_warning = int(settings['GUI']['sleep_warning'])
    periods = [work_period, break_period]

    # 0 -> mouse, 1 -> otter
    animal = int(settings['GUI']['animal'])

    work_time = True # True -> periods[0], False -> periods[1]
    time_left = work_period
    paused = True
    sleep_mode = False
    start_time = -1

    if animal == 0:
        static_animal_image = "images//mouse//mouse_idle.png"
    else:
        static_animal_image = "images//otter//otter_idle.png"

    time_zone = int(settings['GUI']['time_zone'])
    print(time_zone)
    title = settings['GUI']['title']
    layout = [
        [psg.T(f"Current Time: {get_current_time()}", key="current_time")],
        #this is just to see the internal time for debugging sleep timer
        #[psg.T(f"Current time: {(int(time.time())+time_zone)%86400}", key="time_s")],
        [psg.Image(static_animal_image, key='animal_image')],
        [psg.T(f"{'Work' if work_time else 'Break'} Timer:", key='timer_name')],
        [psg.T(f"{(periods[i(work_time)] // 60):0>2}:{(periods[i(work_time)] % 60):0>2}{', Paused' if paused else ''}", key='timer')],
        [psg.B("Start Working", key='toggle', enable_events=True), psg.B("Reset"), psg.B("Settings"), psg.B("Exit", key="Cancel")]
    ]

    # initialize window object 
    window = psg.Window(title, layout)

    # main loop
    while True:
        event, values = window.read(timeout=10)
        if event in (psg.WINDOW_CLOSED, "Cancel"):
            break

        # sleep + warning event
        # finds current time in seconds and compares to stored bed time
        if (int(time.time())+time_zone)%86400 == bed_time:
            if not sleep_mode:
                print("bed time warning!")
            # still need to add a window pop up when this goes off
            sleepwarn_window(animal, sleep_warning)
            # sleep_mode = True
            sleep_window(animal, wake_time)
            window.BringToFront()

            # ====== consider combining the bed time event here ======

            # idea: record the current mouse position when bedtime hits, 
            #   if the mouse is in a different spot => user is awake 

        # start timer event
        elif event == 'toggle' and paused:
            paused = False
            start_time = int(time.time())
            window['toggle'].update("Stop Working")
            window.refresh()
            # window.read(timeout=1)

        # reset timer event
        elif event == 'Reset':
            periods = [int(settings['GUI']['work_period']), int(settings['GUI']['break_period'])]
            start_time = int(time.time())
            time_left = get_time_left(start_time, periods[i(work_time)])
            print(animal)
            if animal == 0:
                window['animal_image'].update("images//mouse//mouse_idle.png")
            else:
                window['animal_image'].update("images//otter//otter_idle.png")
# window.refresh()
            # unsure if reset button should also pause the timer 

        # stop timer event
        elif event == 'toggle' and not paused:
            paused = True
            work_time = True
            periods = [int(settings['GUI']['work_period']), int(settings['GUI']['break_period'])]
            start_time = int(time.time())
            time_left = get_time_left(start_time, periods[i(work_time)])
            window['toggle'].update("Start Working")
            window.refresh()

        #Settings event
        elif event == 'Settings':
            settings_window(animal)

            bed_time = int(settings['GUI']['bed_time'])
            wake_time = int(settings['GUI']['wake_time'])
            animal = int(settings['GUI']['animal'])
            # update period lengths and timerwith new settings
            if not paused and work_period != int(settings['GUI']['work_period']) or break_period != int(settings['GUI']['break_period']):
                work_period = int(settings['GUI']['work_period'])
                break_period = int(settings['GUI']['break_period'])
                periods = [work_period, break_period]
                time_left = get_time_left(start_time if start_time != -1 else int(time.time()), periods[i(work_time)])

        if sleep_mode:
            pass

        # pause timer functionality during sleep mode
        else: 
            # update timer if not paused
            if not paused: 
                time_left = get_time_left(start_time, periods[i(work_time)])

                # switch phases from work -> break or break -> work
                if time_left <= 0:
                    paused = False
                    window['toggle'].update("Start Timer")
                    if work_time:
                        psg.popup_auto_close(
                            f'Work time is over! Why not stand up with {ANIMALS[animal]}?',
                            auto_close=True,
                            auto_close_duration=20,
                            keep_on_top=True
                        )
                        if animal == 0:
                            window['animal_image'].update("images//mouse//mouse_stand.png")
                        else:
                            window['animal_image'].update("images//otter//otter_stand.png")
                    else:
                        psg.popup_auto_close(
                            "Break time is over!",
                            auto_close=True,
                            auto_close_duration=20,
                            keep_on_top=True
                        )
                        if animal == 0:
                            window['animal_image'].update("images//mouse//mouse_idle.png")
                        else:
                            window['animal_image'].update("images//otter//otter_idle.png")
                            
                    work_time = not work_time
                    start_time = int(time.time())
                    time_left = get_time_left(start_time, periods[i(work_time)])

            window['timer'].update(f"{(time_left // 60):0>2}:{(time_left % 60):0>2}{', Paused' if paused else ''}")
            window['current_time'].update(f"Current Time: {get_current_time()}")
            #window['time_s'].update(f"Current time: {(int(time.time())+time_zone)%86400}")
            window['timer_name'].update(f"{'Work' if work_time else 'Break'} Timer:")

    window.close()

def settings_window(animal): #settings window function
    global ANIMALS
    layout = [
        [psg.Text('Set Work Time (mins)', size =(18, 1)), psg.InputText(key='work_in', enable_events=True, s=15)],
        [psg.Text('Set Break Time (mins)', size =(18, 1)), psg.InputText(key='break_in', enable_events=True, s=15)],
        [psg.Text('Set Bed Time (hr:min)', size =(18, 1)), psg.InputText(key='bed_time', enable_events=True, s=15)],
        [psg.Text('Set Wake Time (hr:min)', size =(18, 1)), psg.InputText(key='wake_time', enable_events=True, s=15)],
        [psg.Text('Choose Animal:', size =(18, 1))],
        [psg.Combo(ANIMALS, default_value=ANIMALS[animal], key='animal_choice')],
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

        elif event == 'bed_time' and values['bed_time'] and values['bed_time'][-1] not in '0123456789:':
            window['bed_time'].update(values['bed_time'][:-1])

        elif event == 'wake_time' and values['wake_time'] and values['wake_time'][-1] not in '0123456789:':
            window['wake_time'].update(values['wake_time'][:-1])

        # submit settings event
        elif event == "Submit":
            # replaces setting only if input is given to field
            if values['work_in'] != '':
                settings['GUI']['work_period'] = int(values['work_in'])*60
            if values['break_in'] != '':
                settings['GUI']['break_period'] = int(values['break_in'])*60
            if values['bed_time'] != '':
                settings['GUI']['bed_time'] = timetosec(values['bed_time'])
            if values['wake_time'] != '':
                settings['GUI']['wake_time'] = timetosec(values['wake_time'])
            settings['GUI']['animal'] = ANIMALS.index(values['animal_choice'])
            break

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