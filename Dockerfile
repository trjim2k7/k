FROM python:3.10-slim-buster

# Set environment variables for Python
# PYTHONUNBUFFERED: Ensures that Python output is sent straight to the terminal without buffering.
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk, saving space.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Define argument for user ID for the non-root user.
# Using a high UID (e.g., >10000) is a common practice for service accounts
# to avoid conflicts with system UIDs.
ARG UID=10001

# Create a non-root system user and group named 'appuser'.
# The '--system' flag creates a system account with no home directory and no shell.
RUN adduser --system --uid ${UID} --group appuser

# Set the working directory for the application inside the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
# This step is done separately to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt .

# Install Python dependencies.
# '--no-cache-dir' prevents pip from storing its cache, reducing image size.
# '--upgrade pip' ensures pip itself is up to date before installing other packages.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory.
# This should be done after installing dependencies to again leverage caching.
COPY . .

# Change ownership of the /app directory to the 'appuser'.
# This ensures the non-root user has necessary permissions for the application files.
RUN chown -R appuser:appuser /app

# Switch to the non-root user 'appuser'.
# All subsequent commands and the application itself will run as this user,
# enhancing security by limiting potential damage if the application is compromised.
USER appuser

# Expose the port that FastAPI will listen on.
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn.
# 'app.main:app' specifies that the FastAPI instance named 'app'
# is located in the 'main.py' file within the 'app' directory.
# '--host 0.0.0.0' makes the server accessible from outside the container.
# '--port 8000' specifies the port Uvicorn should listen on.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]