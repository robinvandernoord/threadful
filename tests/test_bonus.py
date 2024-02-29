import sys

from threadful import thread
from threadful.bonus import animate, toggle_cursor, hide_cursor


@thread
def wait(duration: int):
    import time
    time.sleep(duration)
    return duration


def test_animate():
    input_duration = 3
    output_duration = animate(
        wait(input_duration),
    )

    assert input_duration == output_duration

    print('done :)')


def test_animate_async():
    input_duration = 3
    output_thread = animate(
        wait(input_duration),
        threaded=True
    )

    hide_cursor()
    t = '  animating in thread'
    print(t, file=sys.stderr, flush=True, end="\r")

    assert not output_thread.is_done()

    output_duration = output_thread.join()

    assert input_duration == output_duration

    print('done :)' + " " * len(t))  # print extra spaces to remove remainder of 't'


def test_toggle_cursor():
    with toggle_cursor(True): pass
    with toggle_cursor(False): pass


if __name__ == "__main__":
    print('1. sync')
    test_animate()
    print('2. async')
    test_animate_async()
    print('3. done')
