FROM python:3.13.5-slim

WORKDIR /library_app
COPY requirements.txt .
COPY app/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
