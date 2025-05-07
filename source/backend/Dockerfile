FROM python:3.11-alpine

# Install dependencies needed to build psycopg2-binary
RUN apk update && apk add --no-cache gcc musl-dev postgresql-dev libpq

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]