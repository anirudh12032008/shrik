import re

from numpy import exp

rules = [
    ("blah",    r'//.*?$'),
    ("num",     r'\d+(\.\d+)?'),
    ("txt",     r'"[^"]*"'),
    ("word",    r'\b(grab|as|say|craft|return|oops|if|else|input)\b'),
    ("name",    r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("math",    r'==|!=|<=|>=|[+\-*/%=<>]'),
    ("sym",     r'[;(){}]'),
    ("skip",    r'\s+'),
    ("weird",   r'.'),
]

def cut(code):
    out = []
    pat = '|'.join(f'(?P<{n}>{p})' for n, p in rules)
    i = 1
    for m in re.finditer(pat, code, re.MULTILINE):
        kind = m.lastgroup
        val = m.group()

        if kind in ("skip", "blah"):
            continue
        if kind == "weird":
            raise SyntaxError(f"what is {val!r} on line {i}")
        if kind == "num":
            val = float(val) if '.' in val else int(val)
        if kind == "txt":
            val = val[1:-1]
        if kind == "word":
            val = val.lower()

        out.append((kind, val))
        if '\n' in str(val):
            i += val.count('\n')
    return out

class Thing: pass

class Set(Thing):
    def __init__(self, who, val):
        self.who = who
        self.val = val

class Say(Thing):
    def __init__(self, val):
        self.val = val

class Num(Thing):
    def __init__(self, val):
        self.val = val

class Txt(Thing):
    def __init__(self, val):
        self.val = val

class Name(Thing):
    def __init__(self, val):
        self.val = val

class Inp(Thing):
    def __init__(self):
        pass

class If(Thing):
    def __init__(self, cond, body, other):
        self.cond = cond
        self.body = body
        self.other = other

class Oops(Thing):
    def __init__(self, msg):
        self.msg = msg

class Func(Thing):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

class Call(Thing):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Brain:
    def __init__(self, stuff):
        self.stuff = stuff
        self.spot = 0

    def look(self):
        if self.spot < len(self.stuff):
            return self.stuff[self.spot]
        return None

    def move(self):
        t = self.look()
        self.spot += 1
        return t

    def want(self, kind, val=None):
        t = self.look()
        if not t or t[0] != kind:
            raise SyntaxError(f"nope wanted {kind}, got {t}")
        if val and t[1] != val:
            raise SyntaxError(f"wanted {val}, got {t[1]}")
        return self.move()

    def go(self):
        all = []
        while self.look():
            it = self.do()
            if it:
                all.append(it)
        return all

    def do(self):
        t = self.look()
        if t[0] == "word" and t[1] == "grab":
            return self.make()
        if t[0] == "word" and t[1] == "say":
            return self.talk()
        if t[0] == "word" and t[1] == "if":
            return self.iffy()
        if t[0] == "word" and t[1] == "oops":
            return self.fail()
        if t[0] == "word" and t[1] == "craft":
            return self.build()
        if t[0] == "name":
            return self.callish()

        raise SyntaxError(f"huh what is {t}")
    
    def fail(self):
        self.want("word", "oops")
        msg = self.expr()

    def iffy(self):
        self.want("word", "if")
        cond = self.expr()
        self.want("sym", "{")
        yes = []
        while self.look() and self.look()[1] != "}":
            yes.append(self.do())
        self.want("sym", "}")

        no = None
        if self.look() and self.look()[0] == "word" and self.look()[1] == "else":
            self.move()
            self.want("sym", "{")
            no = []
            while self.look() and self.look()[1] != "}":
                no.append(self.do())
            self.want("sym", "}")

        return If(cond, yes, no)

        
    def make(self):
        self.want("word", "grab")
        who = self.want("name")
        self.want("word", "as")
        val = self.expr()
        self.want("sym", ";")
        return Set(who[1], val)

    def talk(self):
        self.want("word", "say")
        val = self.expr()
        self.want("sym", ";")
        return Say(val)

    

    def expr(self):
        l = self.atom()
        while self.look() and self.look()[0] == "math":
            op = self.move()
            r = self.atom()
            l = (op[1], l, r)
        return l
    
    def atom(self):
        t = self.move()
        if t[0] == "num":
            return Num(t[1])
        if t[0] == "txt":
            return Txt(t[1])
        if t[0] == "name":
            return Name(t[1])        
        if t[0] == "word" and t[1] == "input":
            return Inp()

        raise SyntaxError(f"no clue what to do with {t}")
    
    def evalexp(self, exp, mem):
        if isinstance(exp, Num):
            return exp.val
        if isinstance(exp, Txt):
            return exp.val
        if isinstance(exp, Inp):
            return input("Input: ")
        if isinstance(exp, Name):
            if exp.val in mem:
                return mem[exp.val]
            raise NameError(f"{exp.val} is not set")
        if isinstance(exp, tuple):
            op, left, right = exp
            l = self.evalexp(left, mem)
            r = self.evalexp(right, mem)
            if op == "+": return l + r
            if op == "-": return l - r
            if op == "*": return l * r
            if op == "/": return l / r
            if op == ">": return l > r
            if op == "<": return l < r
            if op == "==": return l == r
            if op == "!=": return l != r
            if op == ">=": return l >= r
            if op == "<=": return l <= r
            if op == "%": return l % r
            raise SyntaxError(f"bad op {op}")
        raise TypeError(f"can't eval this thing")

    


if __name__ == "__main__":
    code = '''
    grab score as 92;

    say "What's your name?";
grab name as input;
say "Hello " + name;


    '''

    tokens = cut(code)
    brain = Brain(tokens)
    plan = brain.go()

    mem = {}

    for line in plan:
        if isinstance(line, Say):
            val = brain.evalexp(line.val, mem)
            print(val)
        elif isinstance(line, Set):
            mem[line.who] = brain.evalexp(line.val, mem)
        elif isinstance(line, Oops):
            val = brain.evalexp(line.msg, mem)
            raise RuntimeError(f"oops! {val}")
        elif isinstance(line, If):
            cond = brain.evalexp(line.cond, mem)
            if cond:
                for stmt in line.body:
                    if isinstance(stmt, Say):
                        print(brain.evalexp(stmt.val, mem))
                    elif isinstance(stmt, Set):
                        mem[stmt.who] = brain.evalexp(stmt.val, mem)
                    elif isinstance(stmt, Oops):
                        val = brain.evalexp(stmt.msg, mem)
                        raise RuntimeError(f"oops! {val}")
            elif line.other:
                for stmt in line.other:
                    if isinstance(stmt, Say):
                        print(brain.evalexp(stmt.val, mem))
                    elif isinstance(stmt, Set):
                        mem[stmt.who] = brain.evalexp(stmt.val, mem)
                    elif isinstance(stmt, Oops):
                        val = brain.evalexp(stmt.msg, mem)
                        raise RuntimeError(f"oops! {val}")
