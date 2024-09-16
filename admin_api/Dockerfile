# Use Python as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

# Expose the port the app will run on
EXPOSE 8080

# Set environment variables from .env file
ENV $(cat /app/.env | xargs)
RUN python manage.py makemigrations --no-input && \
    python manage.py migrate --no-input


# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
