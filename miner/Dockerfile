FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Al arrancar el contenedor, ejecutamos el script principal
CMD ["python", "main.py"]