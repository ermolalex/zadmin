FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app

# Expose the port your Django application will run on (default for runserver is 8000)
EXPOSE 8000

# Define the command to run your Django application
# For development, use runserver. For production, consider Gunicorn or uWSGI.
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ./run_all.sh