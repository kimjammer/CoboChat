FROM python:3.11-alpine

WORKDIR /usr/local/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy source code (except static)
COPY cobochat ./cobochat
EXPOSE 8000

CMD ["gunicorn", "cobochat:app", "-w", "1", "--threads", "4", "-b", "0.0.0.0:8000"]