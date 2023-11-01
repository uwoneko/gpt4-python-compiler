import ast
import astunparse
import openai
import sys
import json
import os
import argparse
import logging
import re
from typing import Tuple, Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] <%(levelname)s> %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Fetch API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-3.5-turbo"

# Define cache file
CACHE_FILE = "function_cache.json"

class MagicFunctionTransformer(ast.NodeTransformer):
    def __init__(self):
        self.function_codes = []
        self.load_cache()

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Check if the function call is 'magic' or 'magic_advanced'
        if isinstance(node.func, ast.Name) and node.func.id == 'magic':
            if len(node.args) == 1:
                description, = node.args
                function_name = description.s.replace(' ', '_')
                description = description.s
                logging.info(f'Generating magic function at {node.lineno}:{node.col_offset} described as "{description}"')
            elif len(node.args) == 2:
                function_name, description = node.args
                function_name = function_name.s
                description = description.s
                logging.info(f'Generating magic function at {node.lineno}:{node.col_offset} named "{function_name}" described as "{description}"')
            else:
                logging.error(f'Wrong number of arguments at {node.lineno}:{node.col_offset}! Skipping.')
                return self.generic_visit(node)

            cache_key = (function_name, description)
            if cache_key in self.function_cache:
                function_code = self.function_cache[cache_key]
            else:
                function_code = self.generate_function(function_name, description)
                self.function_cache[cache_key] = function_code
                self.save_cache()
            logging.info(f'Generated code:\n\n{function_code}\n')
            self.function_codes.append(function_code)
            return ast.Name(id=function_name, ctx=ast.Load())
            
        return self.generic_visit(node)

    def generate_function(self, function_name: str, description: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": f"Below is a python function with the name {function_name} that does the following: {description}. No code blocks/formatting are allowed. Assume any uncertainties."},
                ]
            )
            code = response['choices'][0]['message']['content']
            code_blocks = re.search(r'```.*?\n(.*?)```', code, re.DOTALL)
            code = code_blocks.group(1) if code_blocks else code
            compile(code, '<string>', 'exec')
            return code
        except Exception as e:
            logging.error(f"Failed to generate function: {e}")
            return ""

    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    read_cache = json.load(f)
                    self.function_cache = {eval(k): v for k, v in read_cache.items()}
            except Exception as e:
                logging.error(f"Failed to load cache: {e}")
                self.function_cache = {}
        else:
            self.function_cache = {}

    def save_cache(self):
        try:
            with open(CACHE_FILE, 'w') as f:
                save_cache = {str((fname,desc)): code for (fname,desc), code in self.function_cache.items()}
                json.dump(save_cache, f)
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")

def magic_compiler(input_path: str, output_path: str):
    try:
        with open(input_path, 'r') as f:
            code = f.read()
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        return

    module = ast.parse(code)
    transformer = MagicFunctionTransformer()
    transformer.visit(module)

    new_code = '\n\n'.join(transformer.function_codes) + astunparse.unparse(module)

    try:
        with open(output_path, 'w') as f:
            f.write(new_code)
    except Exception as e:
        logging.error(f"Failed to write output file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Magic Compiler')
    parser.add_argument('input_path', type=str, help='Path to the input Python script')
    parser.add_argument('output_path', type=str, help='Path to the output file')
    parser.add_argument('--api_key', type=str, help='OpenAI API key', default=os.getenv("OPENAI_API_KEY"))
    parser.add_argument('--model', type=str, help='OpenAI model to use', default=model)
    args = parser.parse_args()

    if args.api_key is None:
        logging.error("No OpenAI API key provided. Please set the OPENAI_API_KEY environment variable or use the --api_key argument.")
        sys.exit(1)

    openai.api_key = args.api_key
    model = args.model

    magic_compiler(args.input_path, args.output_path)

