<div align="center">
    <img 
        align="center" 
        src="https://github.com/robinvandernoord/threadful/assets/2529002/7a0bb4cd-2a02-40c1-a2b6-2eb77996cd48" 
        alt="Threaded Python"
        width="400px"
        />
    <h1 align="center">Threadful</h1>
    <small>Python Threads - from Dreadful to Threadful</small>
</div>

<hr/>

## Installation

```bash
pip install threadful
```

## Usage

### Example 1: Basic usage of `@thread`

```python
from threadful import thread

@thread # with or without ()
def some_function():
  time.sleep(10)
  return " done "

# when ready, it will call these callback functions.
some_function().then(lambda result: result.strip()).then(lambda result: print(result)) # prints: "done"

promise = some_function() # ThreadWithResult[str] object
promise.result() # Err(None)
time.sleep(15) # after the thread is done:
promise.result() # Ok(" done ")

# alternative to sleep:
result = promise.join() # " done " if success, raises if the thread raised an exception
```

#### What's happening:
- The `@thread` decorator wraps `some_function` to make it run in a separate thread when invoked. 
- Calling `some_function()` doesn't start the thread immediately. Instead, it returns a `ThreadWithResult` object, allowing you to attach callbacks using `.then()` or `.catch()` before the thread starts.
- The thread starts running when you begin checking for the result (`result`, `join`) or explicitly start it.
- The `.then()` chain demonstrates how to process the result when the thread completes.
- The `promise.result()` method gives access to the result (`Ok` or `Err`) if available.
- The `.join()` method blocks until the thread finishes and directly returns the result or raises any exception from the thread.

---

### Example 2: Handling exceptions in threads

```python
@thread()
def raises() -> str:
  raise ValueError()


promise = raises().catch(lambda err: TypeError())

promise.join() # raises TypeError
promise.result() # Err(TypeError)


promise = raises().catch(lambda err: "Something went wrong")

promise.join()  # returns the string "Something went wrong"
```

#### What's happening:
- The `@thread` decorator is used on `raises()`, which deliberately raises a `ValueError`.
- The first `catch()` replaces the `ValueError` with a `TypeError`, so calling `promise.join()` raises the new `TypeError`.
- The second `catch()` provides a fallback string `"Something went wrong"`. When the thread completes, calling `join()` returns this string instead of raising an exception.
- This mechanism allows you to gracefully handle errors in the thread without crashing your program.

### Example: Animating a Function with Different Options

```python
from threadful import thread, animate
import time

@thread
def wait(duration: int):
    time.sleep(duration)
    return f"Waited for {duration} seconds"

# Example 1: Basic animation with static text
result = animate(wait(3), text="Waiting...") # Output: "Waited for 3 seconds"

# Example 2: Threaded animation (non-blocking)
thread_result = animate(wait(3), text="Running asynchronously...", threaded=True)
# Animation running in the background...
# you can do other things in the main thread here
thread_result.join()  # Get the result (str) after the thread completes

# Example 3: Dynamic text animation
animate(wait(3), text=lambda: f"Current time: {time.strftime('%H:%M:%S')}")
# Animation with dynamic text complete!
```

### What's Happening:
1. **Basic Animation**: Runs `wait` with a loading message (`"Waiting..."`) and returns the result after completion.
2. **Threaded Animation**: Runs both `wait` and the animation in the background. Use `.join()` to get the result.
3. **Dynamic Text**: Updates the animation text dynamically using a callback (e.g., current time). 

These examples show how to use `animate` for different scenarios.

---

### Important Note:
A thread doesn't start running immediately when you invoke the decorated function (e.g., `some_function()`). This delay allows you to attach callbacks (`then`, `catch`) before the thread begins execution. The thread starts:
1. When you check for its result (`result`).
2. When you block for its completion (`join`).
3. In the background if you explicitly call `.start()`.


## License
`threadful` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

[See CHANGELOG.md](https://github.com/robinvandernoord/threadful/blob/master/CHANGELOG.md)
