import ast
import inspect
import re
import sys
import time
import traceback
from functools import wraps

def fill_in_lines(frames, source_name, source, start_line):
    # this function is from in https://stackoverflow.com/a/63238621
    lines = source.splitlines()
    for filename, line_number, function_name, text in frames:
        if filename == source_name:
            text = lines[line_number - 1]
        yield filename, line_number + start_line, function_name, text

def painless_timeit(func):
    """
    Decorator function that measures the execution time of `func` and its split times.

    Example:
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

    If you resume the timer for the same split, the time will be accumulated. 
    """
    
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        def split_start(split):
            timeit_wrapper.split_time[split] = timeit_wrapper.split_time.get(split, 0) - time.perf_counter()
        def split_end(split):
            timeit_wrapper.split_time[split] += time.perf_counter()
            print(f'[{func.__name__}->{split}]: Took {timeit_wrapper.split_time[split]:.4f} seconds up until now')
        def pause():
            timeit_wrapper.start_time -= time.perf_counter()
        def resume():
            timeit_wrapper.start_time += time.perf_counter()
            
        lines, start_line = inspect.getsourcelines(func)
        for i, l in enumerate(lines):
            l = l.strip()
            _start = re.match(re.escape("#|>") + r" ([\w\s0-9]+)", l)
            if _start:
                lines[i] = lines[i].replace(l, f"{func.__name__}.split_start('{_start.group(1)}')")
                continue
            _end = re.match(re.escape("#||") + r" ([\w\s0-9]+)", l)
            if _end:
                lines[i] = lines[i].replace(l, f"{func.__name__}.split_end('{_end.group(1)}')")
                continue
            _pause = re.match(re.escape("#||"), l)
            if _pause:
                lines[i] = lines[i].replace(l, f"{func.__name__}.pause()")
                continue
            _resume = re.match(re.escape("#|>"), l)
            if _resume:
                lines[i] = lines[i].replace(l, f"{func.__name__}.resume()")
                continue
            
        source = "".join(lines[1:])
        ast_tree = ast.parse(source)
        ast.fix_missing_locations(ast_tree)
        code = compile(ast_tree, func.__code__.co_filename, mode="exec")
        mod = {}
        
        timeit_wrapper.pause = pause
        timeit_wrapper.resume = resume
        timeit_wrapper.split_start = split_start
        timeit_wrapper.split_end = split_end
        
        timeit_wrapper.split_time = dict()
        timeit_wrapper.start_time = time.perf_counter()
        exec(code, func.__globals__, mod)
        try:
            result = mod[func.__name__](*args, **kwargs)
        except Exception as e:
            _, _, tb = sys.exc_info()
            frames = traceback.extract_tb(tb)
            frames = fill_in_lines(frames, func.__code__.co_filename, source, start_line)

            print('Traceback (most recent call last):')
            print(''.join(traceback.format_list(frames)), end='')
            print('{}: {}'.format(type(e).__name__, str(e)))
            return None
        
        total_time = time.perf_counter() - timeit_wrapper.start_time
        print(f'[{func.__name__}] Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper
