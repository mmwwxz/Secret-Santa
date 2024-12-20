FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY req.txt /app/
RUN pip install -r req.txt

COPY . /app/

EXPOSE 8000

CMD ["python3", "main.py"]