FROM python:3.13-slim
WORKDIR /app
COPY . .
EXPOSE 8000
ENV PORT=8000
CMD ["python", "local_server.py"]
