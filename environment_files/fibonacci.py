def generate_fibonacci(n):
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence

if __name__ == "__main__":
    fib_numbers = generate_fibonacci(20)
    with open("fibonacci.txt", "w") as f:
        for num in fib_numbers:
            f.write(f"{num}\n")
    print("Fibonacci numbers successfully written to fibonacci.txt.")
