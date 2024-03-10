#!/usr/bin/env python3

import asyncio
import logging
import time

from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from random import randint, uniform
from sys import exc_info

# https://gpiozero.readthedocs.io/en/stable/
from gpiozero import LED


__version__ = "2024.03.rc1"

# How-to auto start at boot
"""
sudo apt update
sudo apt install tmux

cat >> ~/.bashrc << xxEOFxx

# Start the LED blinker
BLINKER=$(tmux list-sessions | grep asyncio_blinker);
if [[ -z "${BLINKER}" ]]; then
    # Peak Hour: 07am MT
    # Quiet Hours: 9pm MT - 4am MT
    # UTC is adjusted for daylight savings
    tmux new-session -s blinker -d 'python3 raspberrypi_blinker.py --peak 14 --quiet-hours 04:00-11:00'
fi

xxEOFxx
"""

# GPIO IDs of wired LEDs
"""
+-------------------------+
|   X X X X X X X X X RED |
| RED X X X X X X X X X   |
+-------------------------+
--leds 05,19,06,26,13,22,09,00,11,10,
       21,20,16,15,18,07,08,25,14,23

# Manually blink the LEDs to assert functionality
python3 -m pip install --upgrade pip gpiozero

from gpiozero import LED

# Setup all LEDs
leds = []
for i in range(0,28):
    led = LED(i)
    led.off()
    leds.append(led)

# Setup default LEDs
leds = []
for i in '05,19,06,26,13,22,09,00,11,10,21,20,16,15,18,07,08,25,14,23'.split(','):
    led = LED(int(i))
    led.off()
    leds.append(led)

# Power each LED and wait for input to continue
for index,led in enumerate(leds):
    print(index, led)
    led.on()
    input('waiting...')
    led.off()

"""


def set_up(leds):
    """Setup the LEDs"""
    logging.debug("Setup the LEDs")
    if not isinstance(leds, list):
        leds = leds.split(",")
    logging.debug(f"leds = {leds}")
    for index, led in enumerate(leds):
        # Create instances of LED using the GPIO ID
        logging.debug(f"index = {index}, led = {led}")
        if not isinstance(led, LED):
            led = LED(int(led))
            leds[index] = led
        # Make sure LED is off
        if led.is_lit:
            led.off()
    # Debug message
    logging.debug(f"{' set_up(leds) ':=^80}")
    for index, value in enumerate(leds):
        logging.debug(f"leds[{index}] = {value}")
    logging.debug(f"{'=':=^80}")


def toggle(led, off=None):
    """Turn on or off a LED"""
    if isinstance(led, LED):
        if off is True or led.is_lit:
            led.off()
        else:
            led.on()


def get_offset_map(peak: int = 23, delay: float = 0.1) -> dict:
    """Return a dictionary of hour to delay mapping based on a "peak" hour"""
    logging.debug(f"{f' offset_map(peak={peak}, delay={delay}) ':=^80}")
    peak = datetime(1970, 1, 1, peak)
    offset_map = {
        (peak - timedelta(hours=11)).hour: delay + 4.5,
        (peak - timedelta(hours=10)).hour: delay + 4.0,
        (peak - timedelta(hours=9)).hour: delay + 3.5,
        (peak - timedelta(hours=8)).hour: delay + 3.0,
        (peak - timedelta(hours=7)).hour: delay + 2.5,
        (peak - timedelta(hours=6)).hour: delay + 2.0,
        (peak - timedelta(hours=5)).hour: delay + 1.5,
        (peak - timedelta(hours=4)).hour: delay + 1,
        (peak - timedelta(hours=3)).hour: delay + 0.75,
        (peak - timedelta(hours=2)).hour: delay + 0.5,
        (peak - timedelta(hours=1)).hour: delay + 0.25,
        peak.hour: delay,
        (peak + timedelta(hours=1)).hour: delay + 0.25,
        (peak + timedelta(hours=2)).hour: delay + 0.5,
        (peak + timedelta(hours=3)).hour: delay + 0.75,
        (peak + timedelta(hours=4)).hour: delay + 1,
        (peak + timedelta(hours=5)).hour: delay + 1.5,
        (peak + timedelta(hours=6)).hour: delay + 2.0,
        (peak + timedelta(hours=7)).hour: delay + 2.5,
        (peak + timedelta(hours=8)).hour: delay + 3.0,
        (peak + timedelta(hours=9)).hour: delay + 3.5,
        (peak + timedelta(hours=10)).hour: delay + 4.0,
        (peak + timedelta(hours=11)).hour: delay + 4.5,
        (peak + timedelta(hours=12)).hour: delay + 4.75,
    }
    for key, value in offset_map.items():
        logging.debug(f"offset_map[{key}] = {value}")
    logging.debug(f"{'=':=^80}")
    return offset_map


def get_delay(hour: int, minute: int, offset_map: dict) -> float:
    """Return a delay based on the time of day"""
    min_delay = offset_map[hour]
    # Randomly use one second as minimum when min_delay is greater than one
    if min_delay > 1 and randint(1, 10) <= 3:
        min_delay = 1
    max_delay = offset_map[hour] + (minute + 0.01) / 100
    delay = uniform(min_delay, max_delay)
    logging.debug(
        f"get_delay selected: uniform({min_delay:03.1f}, {max_delay:06f}) = {delay}"
    )
    return delay


def quiet_standby_mode(leds, quiet_hours, delay_between_time_checks=10):
    """Use a standby mode while in a "quiet" period"""
    logging.debug(f"quiet_standby_mode - quiet_hours: {quiet_hours}")

    # Exit early when no `quiet_hours' are set
    if quiet_hours is None:
        return

    # Get the current time
    now = datetime.now(timezone.utc)
    logging.debug(f"quiet_standby_mode - now: {now}")

    # Separate the `start' and `end' of `quiet_hours'
    start, end = quiet_hours.split("-")

    # Create a datetime instance of the `start' time
    hour, minute = start.split(":")
    start = now.replace(hour=int(hour), minute=int(minute))
    # Adjust for daylight savings
    if time.localtime().tm_isdst > 0:
        start = start - timedelta(hours=1)
    logging.debug(f"quiet_standby_mode - start: {start}")

    # Create a datetime instance of the `end' time
    hour, minute = end.split(":")
    end = now.replace(hour=int(hour), minute=int(minute))
    # Adjust for daylight savings
    if time.localtime().tm_isdst > 0:
        end = end - timedelta(hours=1)
    logging.debug(f"quiet_standby_mode - end: {end}")

    # Exit if `now' is NOT within the `quiet_hours' so go blink some LEDs
    logging.debug(
        f"quiet_standby_mode - in a quiet period: {(now > start and now < end)}"
    )
    if not (now > start and now < end):
        return

    # Else `now' IS within the `quiet_hours'

    # Turn off all the LEDs
    for led in leds:
        toggle(led, off=True)

    # GPIO2 "purple" LED
    standby_led = LED(2)

    # If we are in a quiet period, block until `end' date/time
    while now > start and now < end:
        # Flash the LED
        toggle(standby_led, off=False)
        time.sleep(0.5)
        toggle(standby_led, off=True)
        logging.debug(
            f"quiet_standby_mode - check time again in {delay_between_time_checks} seconds: {now}"
        )
        # Sleep for a period before continuing the loop
        time.sleep(delay_between_time_checks)
        # Update `now' or we will never exit the loop
        now = datetime.now(timezone.utc)

    # End of quiet period block
    logging.debug(
        f"quiet_standby_mode - in a quiet period: {(now > start and now < end)}"
    )


async def worker(name, queue):
    """Process an item from the queue"""
    while True:

        # Get an item out of the queue.
        led, sleep_for = await queue.get()

        # Sleep for the "sleep_for" time.
        await asyncio.sleep(sleep_for)

        # Toggle the LED power state
        toggle(led)

        # Notify the queue that the item has been processed.
        queue.task_done()

        logging.debug(f"{name} slept for {sleep_for:0.5f} seconds, toggled led {led}")


async def blinker_loop(
    leds: list,  # list of LEDs to toggle
    offset_map: dict,  # dictionary map of hours to delay values
    randomized: bool = True,  # randomized the order or `leds`
    allow_linger: int = 0.7,  # percent of LEDs allowed continue in the current state)
    uniform_delay: int = False,  # use the same delay for all LED toggles
    **kwargs,
):
    """Run a blinker loop"""

    # Use a standby mode while in a "quiet" period
    quiet_standby_mode(leds, kwargs.get("quiet_hours"))

    total_sleep_time = 0

    logging.debug(f"{' blinker_loop ':=^80}")

    # Note the start time for this loop
    start = datetime.now(timezone.utc)
    logging.debug(f"blinker loop start time: {start}")

    # Create the queue
    queue = asyncio.Queue()

    # Create the work items to be done
    # Each item is a tuple of a LED instance and a delay time in seconds
    # When `uniform_delay` is not True, the delay should be selected from the
    # `offset_map` based on the time of day.

    # Randomize the order the LEDs are added to the queue
    if not randomized:
        randomized = leds.copy()

    # Randomize the order the LEDs are added to the queue
    else:
        leds_copy = leds.copy()
        randomized = []
        while len(leds_copy) > 0:
            # Make a random selection of the index values left in the list
            index = randint(0, (len(leds_copy) - 1))
            led = leds_copy.pop(index)
            randomized.append(led)

    # Randomly reduce the list by a `linger` percent
    # This allows the state of some LEDs to "linger" between loops
    if allow_linger:
        while len(randomized) / len(leds) > allow_linger:
            # Make a random selection of an index value
            index = randint(0, (len(randomized) - 1))
            # Remove the value from the list
            _ = randomized.pop(index)

    # Create the task for each led
    logging.debug(f"{' create the tasks ':=^80}")
    for led in randomized:
        # Set a delay for the `sleep_for` value
        if uniform_delay:
            sleep_for = uniform_delay
        else:
            sleep_for = get_delay(start.hour, start.minute, offset_map)
            # sleep_for = offset_map.get(start.hour, 0.25)
            # sleep_for = random.uniform(0.05, 1.0)
        # Keep track of the total sleep time
        total_sleep_time += sleep_for
        # Add the item to the queue
        queue.put_nowait((led, sleep_for))
    logging.debug(f"{'=':=^80}")

    # Divvy up the tasks between the workers
    # The queue is processed concurrently
    tasks = []
    workers = kwargs.get("workers", 3)
    for i in range(workers):
        task = asyncio.create_task(worker(f"worker-{i}", queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel the worker tasks.
    for task in tasks:
        task.cancel()

    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    logging.debug(f"{'=':=^80}")

    logging.debug(f"blinker worker(s) slept in parallel for {total_slept_for}")
    logging.debug(f"blinker loop total sleep time: {total_sleep_time}")

    # Note the end time for this loop
    end = datetime.now(timezone.utc)
    logging.debug(f"blinker loop end time: {end}")

    # Note the time delta for this loop
    logging.debug(f"blinker loop time delta: {end - start}")

    logging.debug(f"{'=':=^80}")


async def main(*args, **kwargs):
    """Blink some LEDs"""
    logging.debug(f"**kwargs: {kwargs}")

    # Setup the LEDs
    leds = kwargs.pop("leds").split(",")
    if leds == ["all"]:
        leds = [f"{i:02}" for i in range(0, 28)]
    logging.debug(f"leds: {leds}")

    skip_setup = kwargs.get("skip_setup", False)
    logging.debug(f"skip_setup = {skip_setup}")
    if not skip_setup:
        set_up(leds)

    # Get the `offset_map` dictionary of delay values
    offset_map = get_offset_map(kwargs.get("peak"), kwargs.get("delay"))

    # Run a "power on self test" loop unless `skip_post` was set
    if not kwargs.get("skip_post", False):
        # By using only one worker for a POST loop we are effectively
        # disabling asynchronous execution of LED toggles. Setting
        # `uniform_delay=True` makes each LED toggle at a consistent rate.
        await blinker_loop(
            leds,
            offset_map,
            randomized=False,
            allow_linger=False,
            uniform_delay=0.1,
            workers=1,
        )
        # We expect all LEDs to have been powered on
        # Run a second loop to toggle the power off
        await blinker_loop(
            leds,
            offset_map,
            randomized=False,
            allow_linger=False,
            uniform_delay=0.1,
            workers=1,
        )

    # Run blinker_loop until count equals `loops`
    # or run blinker_loop forever when `loops` is less than zero
    # or do nothing if `loops` is zero, for testing maybe?
    if kwargs.get("loops") > 0:
        loop_count = 0
        while loop_count < kwargs.get("loops"):
            await blinker_loop(leds, offset_map, **kwargs)
            loop_count += 1
    elif kwargs.get("loops") < 0:
        while True:
            await blinker_loop(leds, offset_map, **kwargs)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="raspberrypi_blinker.py",
        description="Make LEDs attached to a Raspberry Pi blink",
        epilog="Example: raspberrypi_blinker.py --peak 14 --quiet-hours 07:00-13:00",
    )

    # Options for controlling the blinking LEDs
    parser.add_argument(
        "--peak",
        type=int,
        metavar="int",
        default=15,
        help="UTC hour of minimal delay between toggles (default=15)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        metavar="float",
        default=0.1,
        help="minimal delay in seconds between toggles (default=0.1)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        metavar="int",
        default=3,
        help="number of workers to perform toggles (default=3)",
    )
    parser.add_argument(
        "--loops",
        type=int,
        metavar="int",
        default=-1,
        help="number of loops to run (default=-1)",
    )
    parser.add_argument(
        "--quiet-hours",
        metavar="HH:MM-HH:MM",
        default="05:00-11:00",
        help="enter a quiet standby mode between UTC hours, \
        adjusted for daylight savings (default=05:00-11:00)",
    )
    parser.add_argument(
        "--leds",
        metavar="<GPIO#>,<GPIO#>,...",
        default="05,19,06,26,13,22,09,00,11,10,21,20,16,15,18,07,08,25,14,23",
        help='active GPIO pin IDs (use: "all" for all GPIO pin IDs)',
    )

    # Options likely used less often
    parser.add_argument(
        "--version", "-V", action="version", version=f"version {__version__}"
    )
    parser.add_argument("--verbose", "-v", action="store_true")

    # Likely only used with development
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--skip-setup", action="store_true", help="skip setup")
    parser.add_argument(
        "--skip-post", action="store_true", help="skip power on self test"
    )

    parser.set_defaults(func=main)
    argv, remaining_argv = parser.parse_known_args()

    # Setup logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    if argv.debug:
        logger.setLevel(logging.DEBUG)
    elif argv.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    # Warn about any `remaining_argv'
    if remaining_argv:
        logger.warning(f"Ignored arguments: {remaining_argv}")

    # Pass the options to `main'
    try:
        logging.debug(f"argv {type(argv)}: {argv}")
        asyncio.run(argv.func(remaining_argv=remaining_argv, **vars(argv)))
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(f"{exc_info()[0]}; {err}")
        if hasattr(argv, "debug") and argv.debug:
            raise
