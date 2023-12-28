# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r req.txt

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Run dashboard.py when the container launches
CMD ["python3", "dashboard.py"]