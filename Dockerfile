FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000

ENV SHOPIFY_API_KEY=${SHOPIFY_API_KEY}
ENV SHOPIFY_PASSWORD=${SHOPIFY_PASSWORD}
ENV SHOPIFY_STORE_NAME=${SHOPIFY_STORE_NAME}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]