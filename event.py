from inspect import signature

class Event:
    def __init__(self):
        self.funcs = list()

    def add_handler(self, f):
        if not callable(f):
            raise ValueError("'f' must be a function type")
        self.funcs.append(f)


    def remove_handler(self, f):
        if not callable(f):
            raise ValueError("'f' must be a function type")
        self.funcs.remove(f)


    def clear_handler(self):
        self.funcs.clear()


    def fire(self, sender, e):
        for f in self.funcs:
            sig = signature(f)
            counts = len(sig.parameters)
            
            if counts == 0:
                f()
            elif counts == 1:
                f(e)
            elif counts == 2:
                f(sender, e)
            else:
                raise ValueError("handler must have no more than two parameters")


class ProgressEventArgs:
    def __init__(self, name, current, allcount):
        self.name = name
        self.current = current
        self.allcount = allcount