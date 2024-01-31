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

```python
from threadful import thread

@thread # with or without ()
def some_function():
  time.sleep(10)
  return " done "

# when ready, it sill call these callback functions.
some_function().then(lambda result: result.strip().then(lambda result: print(result)) # prints: "done"

promise = some_function() # ThreadWithResult[str] object
promise.result() # Err(None)
time.sleep(15) # after the thread is done:
promise.result() # Ok(" done ")

# alternative to sleep:
result = promise.join() # " done " if success, raises if the thread raised an exception
```

```python

@thread()
def raises() -> str:
  raises ValueError()


promise = raises().catch(lambda err: TypeError())

promise.join() # raises TypeError
promise.result() # Err(TypeError)


promise = raises().catch(lambda err: "Something went wrong")

promise.join()  # returns the string "Something went wrong"

```



## License
`threadful` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Changelog

[See CHANGELOG.md](https://github.com/robinvandernoord/threadful/blob/master/CHANGELOG.md)
