FROM python:3.12-slim-bookworm
LABEL authors="zymawy"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

RUN apt-get update  \
    && apt-get install -y ca-certificates curl gnupg \
  	&& mkdir -p /etc/apt/keyrings \
    && apt-get install -y curl  \
    && curl -sL https://deb.nodesource.com/setup_20.x | bash -  \
    && apt-get install -y nodejs

RUN npm install -g tailwindcss@latest postcss@latest autoprefixer@latest
RUN npm i rimraf

# Copy project files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000
RUN mkdir -p /app/db && chown -R www-data:www-data /app/db

RUN touch /app/db.sqlite3
RUN chmod 664 /app/db.sqlite3
RUN touch /db.sqlite3
RUN chmod 664 /db.sqlite3

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Give execution permissions to the entrypoint script
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]

