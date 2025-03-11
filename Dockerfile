# Use official Python base image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy application files
COPY app.py /app

# Install FastAPI and Uvicorn
RUN pip install fastapi uvicorn

# Expose the port that FastAPI runs on
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
