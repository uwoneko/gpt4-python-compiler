# gpt4-python-compiler
A compiler that uses gpt 4 to generate functions for you, at compile time.
## Compiling
`python magic_compiler.py input.py output.py`
## Example usage
```py
magic('print hello world')
print_hello_world()
magic_advanced('print_hello_world_advanced', 'Prints Hello World and returns')
print_hello_world_advanced()
```
## Example output
```py
def print_hello_world():
    print("hello world")
def print_hello_world_advanced():
    print("Hello World")
    return
print_hello_world
print_hello_world()
print_hello_world_advanced
print_hello_world_advanced()
```
Note: the 'magic' calls gets replaced with function names, so `magic('print hello world')()` is acceptable too.
