FROM python:3.11-alpine

WORKDIR /usr/local/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy source code (except static)
COPY cobochat ./cobochat
EXPOSE 5000

CMD ["gunicorn", "cobochat:app", "-w", "1", "--threads", "4", "--port", "5000"]