# gpt4-python-compiler
A python parser that uses gpt 4 to generate functions for you, at compile time.
## Usage
`python3 magic.py --api_key sk-your-api-key input.py output.py`
## Examples
### Simple usage
input.py:
```py
magic('print hello world')()
```
output.py:
```py
def print_hello_world():
    print("hello world")

print_hello_world()
```
### Advanced usage
input.py:
```py
num = magic('add_one', 'add 1 to the input number')(1)
print(num)
```
output.py:
```py
def add_one(num):
    return num + 1

num = add_one(2)
print(num)
```
### Multiple calls
input.py:
```py
magic('uwu', 'adds uwu after each period')
print(uwu("hello! i am very owo."))
print(uwu("lorem ipsum. stuff stuff stuff stuff."))
```
output.py:
```py
def uwu(text):
    return text.replace(".", ". uwu")

uwu
print(uwu('hello! i am very owo.'))
print(uwu('lorem ipsum. stuff stuff stuff stuff.'))
```
Note: i am too lazy to remove the name of the function if you arent gonna call it and python doesnt care, so it is what it is