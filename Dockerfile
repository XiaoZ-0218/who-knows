FROM python:3.12-slim
WORKDIR /app
COPY src ./src
COPY web ./web
COPY serve.py ./serve.py
ENV PYTHONPATH=/app/src
ENV WHO_KNOWS_DATA=/data/catalog.json
ENV WHO_KNOWS_PORT=8765
EXPOSE 8765
VOLUME /data
CMD ["python", "serve.py"]
