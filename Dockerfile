# Use Python 3.10 slim (stable for numpy 1.23.5)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (better for caching)
COPY requirements.txt .

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port your Flask app uses
EXPOSE 5000

# Start command for Gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "--workers", "1"]