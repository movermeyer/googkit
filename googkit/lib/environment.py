class Environment(object):
    """Environment class that has runtime information.
    """

    def __init__(self, cwd, argument, tree):
        # [todo] - Add docstirng.
        self.cwd = cwd
        self.argument = argument
        self.tree = tree
