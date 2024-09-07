FROM python:3.10

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN apt-get update && apt-get install -y wget && \
    if [ ! -d "/opt/spades" ]; then \
        wget https://github.com/ablab/spades/releases/download/v4.0.0/SPAdes-4.0.0-Linux.tar.gz && \
        tar -xzf SPAdes-4.0.0-Linux.tar.gz && \
        mv SPAdes-4.0.0-Linux /opt/spades && \
        rm SPAdes-4.0.0-Linux.tar.gz; \
    fi

ENV PATH="/opt/spades/bin:$PATH"

EXPOSE 8000

RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
