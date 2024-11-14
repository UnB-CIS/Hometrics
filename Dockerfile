FROM python:3.9-alpine

# Set the working directory
WORKDIR /

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt . 
RUN pip install -r requirements.txt

# Copy the project files into the container
COPY ./database /database
COPY ./scripts /scripts
COPY ./pipeline /pipeline
COPY ./tests /tests
COPY .env /

# Set PYTHONPATH to the root directory to allow imports across folders
ENV PYTHONPATH="/:${PYTHONPATH}"


