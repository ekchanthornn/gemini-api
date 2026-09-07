def generate_fibonacci(n):
    fib = []
    a, b = 0, 1
    for _ in range(n):
        fib.append(a)
        a, b = b, a + b
    return fib

def main():
    n = 20
    fib_numbers = generate_fibonacci(n)
    
    # Save to fibonacci.txt
    filename = "fibonacci.txt"
    with open(filename, "w") as f:
        for num in fib_numbers:
            f.write(f"{num}\n")
    
    # Read the file and print its contents
    with open(filename, "r") as f:
        content = f.read()
    
    print("Contents of fibonacci.txt:")
    print(content, end="")

if __name__ == "__main__":
    main()
