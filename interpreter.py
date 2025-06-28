import re
import sys

memory = {}

def evalexp(exp):
    try:
        return eval(exp, memory)
    except Exception as e:
        raise Exception(f"[Shrik Error] Failed to evaluate expression '{exp}'")

def interline(line):
    line = line.strip()

# GRAB - define variables
    if line.startswith("grab") and "as" in line:
        p = line.replace(";","").split("as")
        var = p[0].replace("grab", "").strip()
        exp = p[1].strip()
        val = evalexp(exp)
        memory[var] = val

# SAY 
    elif line.startswith("say"):
        exp = line.replace("say", "").replace(";", "").strip()
        print(evalexp(exp))

    elif line == "" or line.startswith("//"):
        pass
# CHILL
    elif line.startswith("chill"):
        import time
        p = line.replace("chill", "").replace(";", "").strip()
        if p.isdigit():
            time.sleep(int(p))
        else:
            raise Exception(f"[Shrik Error] Invalid Chill '{p}'")

    else:
        raise Exception(f"[Shrik Error] Unknown Command in '{line}'")
    
def run(file):
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            interline(line)

if __name__ == "__main__":
    run(sys.argv[1])
