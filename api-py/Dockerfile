FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY api-py/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app folder
COPY ./api-py/app /app/app
# in this case the test file should be
# api-py/app/test_main.py ----- will be in /app/app/test_main.py

# Expose port
EXPOSE 8000

# Start uvicorn (note the app module)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]