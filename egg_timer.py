#!/usr/bin/env python3

import sys
import time

ASCII_BELL = '\a'
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def main(seconds, message):
    """Display a countdown timer on a single line"""

    ## Start the countdown timer
    while seconds > 0:
        print(f"EGG TIMER: {int(seconds / 60):02d}:{seconds % 60:02d}")
        seconds = seconds - 1
        time.sleep(1)
        ## Clear the line of the current content for the next loop
        print(LINE_UP, end=LINE_CLEAR)

    ## Print the final message and sound the ASCII bell
    print(message + ASCII_BELL)


if __name__ == '__main__':
    ## Seconds to start the countdown timer at, default 5 minutes
    if len(sys.argv) < 2:
        seconds = 300
    ## Handle non-digit as argument 1 (-h, --help, foobar, ...)
    elif not sys.argv[1].isdigit():
        print('Usage: egg_timer.py <SECONDS> [<MESSAGE ...>]')
        sys.exit(0)
    else:
        seconds = int(sys.argv[1])

    ## Allow a different message to be supplied
    if len(sys.argv) >= 3:
        message = ' '.join(sys.argv[2:])
    else:
        message = 'Time to go do that thing!'

    try:
        main(seconds, message)
    except KeyboardInterrupt:
        pass

