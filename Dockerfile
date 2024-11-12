FROM python:3.11-alpine

WORKDIR /usr/local/app

# install required libraries
RUN pip install -U pip setuptools wheel
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the code into image
COPY . .

# run the application
CMD ["python", "-u", "code/code.py"]
