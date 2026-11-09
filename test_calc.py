from calc import add, mod, mul, power, sub


def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
    assert add(-1, 1) == 0
    assert add(10, -3) == 7


def test_sub():
    assert sub(5, 3) == 2
    assert sub(0, 0) == 0
    assert sub(1, -1) == 2
    assert sub(-3, -10) == 7


def test_mul():
    """Test multiplication, including zero and negative numbers."""
    assert mul(2, 3) == 6
    assert mul(0, 5) == 0
    assert mul(-2, 3) == -6
    assert mul(-4, -5) == 20


def test_mod():
    """Test remainder calculation, including exact division and negatives."""
    assert mod(10, 3) == 1
    assert mod(9, 3) == 0
    assert mod(7, 1) == 0
    assert mod(-7, 3) == 2


def test_power():
    """Test exponentiation, including zero and negative bases."""
    assert power(2, 3) == 8
    assert power(5, 0) == 1
    assert power(10, 1) == 10
    assert power(-2, 3) == -8


if __name__ == "__main__":
    test_add()
    test_sub()
    test_mul()
    test_mod()
    test_power()
    print("All tests passed successfully!")
