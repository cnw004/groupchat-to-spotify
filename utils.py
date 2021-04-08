from functools import wraps

def print_length(message: str):
  def decorator(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
      val = func(*args, **kwargs)
      print(str(len(val)) + f" {message}")
      return val
    return func_wrapper
  return decorator
