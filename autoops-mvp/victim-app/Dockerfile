FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize the DB during build or it will be fresh every run. 
# Better to have it persistent or init on startup. 
# The app.py has init logic now, so we are good.

CMD ["python", "app.py"]
