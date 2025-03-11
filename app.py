from fastapi import FastAPI, HTTPException
import random
import math

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust as needed)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility Functions
def reverse_string(text: str) -> str:
    return text[::-1]

def get_factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)

def generate_random_number(start: int = 1, end: int = 100) -> int:
    return random.randint(start, end)

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9/5) + 32

# API Endpoints
@app.get("/")
def root():
    return {"message": "Welcome to FastAPI on OpenShift!"}

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.post("/add")
def add_numbers(a: int, b: int):
    return {"result": a + b}

@app.get("/reverse")
def reverse_string_api(text: str):
    return {"original": text, "reversed": reverse_string(text)}

@app.get("/random-number")
def random_number_api(start: int = 1, end: int = 100):
    return {"random_number": generate_random_number(start, end)}
