# painless-timeit
A timeit decorator for Python functions that allows for splits measurements inside of the function without the hustles of modifying too much code after performance analysis

# Installation
Put the `painless_timeit.py` file inside you project and import it using
```python
from painless_timeit import painless_timeit
```

# Usage
Apply `@painless_timeit` decorator to your function and it will be timed as usual, printing the measured time at the end of its execution.
If you want to also measure timesplits inside your function you can add the comment `#|> [split_name]` before the code block you want to time and `#|| [split_name]` after.
The wrapper function keeps a record of each split with its current measured time, meaning that multiple references to the same split will accumulate.
You can also pause time measurements for the function by commenting `#||` and resume it with `#|>`.
The wrapper function will replace the lines with these kind of comments with the needed code, so be sure to place these comments in dedicated lines, or else you may not execute important pieces of code.

Here's an example of a decorated function and its execution:
```python
@painless_timeit
def my_function():
    #|> split1
    time.sleep(2) # code in this block will be measured as split1
    #|| split1
    #|> split2
    time.sleep(0.5) # code in this block will be measured as split2
    #|| split2
    #||
    time.sleep(10) # code in this block won't be measured
    #|>
    time.sleep(1) # code in this block will be measured as the main function
```
Output:
```python
>>> my_function()
[my_function->split1]: Took 2.0000 seconds up until now
[my_function->split2]: Took 0.5000 seconds up until now
[my_function]: Took 3.5000 seconds
```


### Note
The choice for the symbols used for the signal comments will be clear if you use Fira Code font with ligatures
