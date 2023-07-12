import ast
import astunparse
import openai
import sys
import json
import os

openai.api_key = "sk-"
#openai.api_base = "https://api.openai.com/v1"

CACHE_FILE = "function_cache.json"

class MagicFunctionTransformer(ast.NodeTransformer):
    def __init__(self):
        self.function_codes = []
        self.load_cache()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ['magic', 'magic_advanced']:
            if node.func.id == 'magic':
                description, *args = node.args
                function_name = description.s.replace(' ', '_')
                description = description.s
                print(f'Working on magic "{description}" call at {node.lineno}:{node.col_offset}')
            elif node.func.id == 'magic_advanced':
                function_name, description = node.args
                function_name = function_name.s
                description = description.s
                print(f'Working on magic_advanced "{function_name}" call with description "{description}" at {node.lineno}:{node.col_offset}')

            cache_key = (function_name, description)
            if cache_key in self.function_cache:
                function_code = self.function_cache[cache_key]
            else:
                function_code = self.generate_function(function_name, description)
                self.function_cache[cache_key] = function_code
                self.save_cache()
                
            self.function_codes.append(function_code)
            return ast.Name(id=function_name, ctx=ast.Load())
            
        return self.generic_visit(node)

    def generate_function(self, function_name, description):
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            temperature=0,
            messages=[
                {"role": "system", "content": f"Write only a python function with the name {function_name} that does the following: {description}. Include no formatting in your response."}
            ]
        )
        return response['choices'][0]['message']['content']

    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                read_cache = json.load(f)
                # Use eval to safely turn string representation of tuples back into actual tuples
                self.function_cache = {eval(k): v for k, v in read_cache.items()}
        else:
            self.function_cache = {}

    def save_cache(self):
        with open(CACHE_FILE, 'w') as f:
            save_cache = {str((fname,desc)): code for (fname,desc), code in self.function_cache.items()}
            json.dump(save_cache, f)

def magic_compiler(input_path, output_path):
    with open(input_path, 'r') as f:
        code = f.read()

    module = ast.parse(code)
    transformer = MagicFunctionTransformer()
    transformer.visit(module)

    new_code = '\n'.join(transformer.function_codes) + astunparse.unparse(module)

    with open(output_path, 'w') as f:
        f.write(new_code)

# USAGE: python magic_compiler.py input.py output.py
if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    magic_compiler(input_path, output_path)
