FROM python:3.13-slim
WORKDIR /app
COPY requirements_hosting.txt ./
RUN pip install --no-cache-dir -r requirements_hosting.txt
COPY . .
EXPOSE 8000
ENV PORT=8000
CMD ["python", "local_server.py"]
