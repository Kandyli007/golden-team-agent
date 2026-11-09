def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b


def mod(a, b):
    """Return the remainder of dividing a by b.

    Args:
        a: The dividend.
        b: The divisor. Must not be zero.

    Returns:
        The remainder of a divided by b.
    """
    return a % b


def power(a, b):
    """Return a raised to the power of b.

    Args:
        a: The base.
        b: The exponent.

    Returns:
        The result of a raised to the power of b.
    """
    return a ** b


def divide(a, b):
    """Return the quotient of a divided by b.

    Args:
        a: The dividend.
        b: The divisor. Must not be zero.

    Returns:
        The quotient of a divided by b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b
