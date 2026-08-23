FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the entire repository into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir .[all] mkdocs mkdocs-material

# Expose port for mkdocs server
EXPOSE 8000

# Default command to serve the documentation using the example mkdocs.yml
CMD ["mkdocs", "serve", "-f", "example/mkdocs.yml", "--dev-addr=0.0.0.0:8000"]
