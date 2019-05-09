import os

def check_state(expression, formatted_message, *args):
    if not expression:
        raise Exception(formatted_message.format(*args))

def check_executable(filename):
    check_state(os.path.exists(filename), "The path '{}' does not exist", filename)
    check_state(os.path.isfile(filename), "The path '{}' is not a file", filename)
    check_state(os.access(filename, os.X_OK), "The path '{}' is not executable", filename)
