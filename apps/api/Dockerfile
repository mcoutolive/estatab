FROM python:3.12.10-slim

WORKDIR /app

# Copy the estatab package source
COPY src /estatab-src/src
COPY pyproject.toml /estatab-src/
COPY src/setup.py /estatab-src/

# Install estatab package
RUN pip install --no-cache-dir /estatab-src

# Copy API code
COPY apps/api /app

# Install API dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
