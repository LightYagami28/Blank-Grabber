import random
import string
import base64
import codecs
import argparse
import os
import sys
import lzma

from textwrap import wrap
from marshal import dumps

def print_error(data):
    print(data, file=sys.stderr)

class BlankOBF:
    def __init__(self, code, output_path):
        self.code = code.encode()
        self.out_path = output_path
        self.var_len = 3
        self.vars = {}

        self.marshal()
        self.encrypt1()
        self.encrypt2()
        # self.encrypt3() # This one increases detections
        self.finalize()
    
    def generate(self, name):
        res = self.vars.get(name)
        if res is None:
            res = "_" + "".join(["_" for _ in range(self.var_len)])
            self.var_len += 1
            self.vars[name] = res
        return res
    
    def encrypt_string(self, string, config={}, func=False):
        b64 = list(b"base64")
        b64decode = list(b"b64decode")
        __import__ = config.get("__import__", "__import__")
        getattr = config.get("getattr", "getattr")
        bytes_ = config.get("bytes", "bytes")
        eval_ = config.get("eval", "eval")
        if not func:
            return f'{getattr}({__import__}({bytes_}({b64}).decode()), {bytes_}({b64decode}).decode())({bytes_}({list(base64.b64encode(string.encode()))})).decode()'
        else:
            attrs = string.split(".")
            base = self.encrypt_string(attrs[0], config)
            attrs = list(map(lambda x: self.encrypt_string(x, config, False), attrs[1:]))
            new_attr = ""
            for i, val in enumerate(attrs):
                if i == 0:
                    new_attr = f'{getattr}({eval_}({base}), {val})'
                else:
                    new_attr = f'{getattr}({new_attr}, {val})'
            return new_attr
            
    def encryptor(self, config):
        def func_(string, func=False):
            return self.encrypt_string(string, config, func)
        return func_
    
    def compress(self):
        self.code = lzma.compress(self.code)
    
    def marshal(self):
        self.code = dumps(compile(self.code, "<string>", "exec"))
    
    def encrypt1(self):
        code = base64.b64encode(self.code).decode()
        part_len = int(len(code) / 4)
        code = wrap(code, part_len)
        var1 = self.generate("a")
        var2 = self.generate("b")
        var3 = self.generate("c")
        var4 = self.generate("d")
        init = [f'{var1}="{codecs.encode(code[0], "rot13")}"', f'{var2}="{code[1]}"', f'{var3}="{code[2][::-1]}"', f'{var4}="{code[3]}"']

        random.shuffle(init)
        init = ";".join(init)
        self.code = f'''
# Obfuscated using https://github.com/Blank-c/BlankOBF
{init};__import__({self.encrypt_string("builtins")}).exec(__import__({self.encrypt_string("marshal")}).loads(__import__({self.encrypt_string("base64")}).b64decode(__import__({self.encrypt_string("codecs")}).decode({var1}, __import__({self.encrypt_string("base64")}).b64decode("{base64.b64encode(b'rot13').decode()}").decode())+{var2}+{var3}[::-1]+{var4})))
'''.strip().encode()
    
    def encrypt2(self):
        self.compress()
        var1 = self.generate("e")
        var2 = self.generate("f")
        var3 = self.generate("g")
        var4 = self.generate("h")
        var5 = self.generate("i")
        var6 = self.generate("j")
        var7 = self.generate("k")
        var8 = self.generate("l")
        var9 = self.generate("m")

        conf = {
            "getattr": var4,
            "eval": var3,
            "__import__": var8,
            "bytes": var9
        }
        encrypt_string = self.encryptor(conf)
        
        self.code = f'''# Obfuscated using https://github.com/Blank-c/BlankOBF
{var3} = eval({self.encrypt_string("eval")});{var4} = {var3}({self.encrypt_string("getattr")});{var8} = {var3}({self.encrypt_string("__import__")});{var9} = {var3}({self.encrypt_string("bytes")});{var5} = lambda {var7}: {var3}({encrypt_string("compile")})({var7}, {encrypt_string("<string>")}, {encrypt_string("exec")});{var1} = {self.code}
{var2} = {encrypt_string('__import__("builtins").list', func=True)}({var1})
try:
    {encrypt_string('__import__("builtins").exec', func=True)}({var5}({encrypt_string('__import__("lzma").decompress', func=True)}({var9}({var2})))) or {encrypt_string('__import__("os")._exit', func=True)}(0)
except {encrypt_string('__import__("lzma").LZMAError', func=True)}:...
'''.strip().encode()

    def encrypt3(self):
        self.compress()
        data = base64.b64encode(self.code)
        self.code = f'# Obfuscated using https://github.com/Blank-c/BlankOBF\n\nimport base64, lzma; exec(compile(lzma.decompress(base64.b64decode({data})), "<string>", "exec"))'.encode()

    def finalize(self):
        if os.path.dirname(self.out_path).strip() != "":
            os.makedirs(os.path.dirname(self.out_path), exist_ok=True)
        with open(self.out_path, "w") as e:
            e.write(self.code.decode())
        # print("Saved as --> " + os.path.realpath(self.out_path))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="Obfuscates python program to make it harder to read")
    parser.add_argument("FILE", help="Path to the file containing the python code")
    parser.add_argument("-o", type=str, help='Output file path [Default: "Obfuscated_<FILE>.py"]', dest="path")
    args = parser.parse_args()

    if not os.path.isfile(source_file := args.FILE):
        print_error(f'No such file: "{args.FILE}"')
        os._exit(1)
    elif not source_file.endswith((".py", ".pyw")):
        print_error('The file does not have a valid python script extension!')
        os._exit(1)
    
    if args.path is None:
        args.path = "Obfuscated_" + os.path.basename(source_file)
    
    with open(source_file) as source_file:
        code = source_file.read()
    
    BlankOBF(code, args.path)
