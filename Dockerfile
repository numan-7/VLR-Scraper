# Use an official Python runtime as a parent image
FROM python:3.8.9
# Set the working directory in the container
WORKDIR /usr/src/app
# Copy the current directory contents into the container at /usr/src/app
COPY . .
# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt
# Make port 8000 available to the world outside this container
EXPOSE 8000
# Run Django server when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]