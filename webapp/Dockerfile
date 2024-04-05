# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set environment variables
ENV DB_HOST=mysql
ENV DB_USER=root
ENV DB_PASSWORD=hcQXGBcDSWAx3N0J
ENV DB_NAME=weather_data
    
# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir flask mysql-connector-python

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]