FROM python
MAINTAINER Doby2333 [lyzhang0113@gmail.com]
WORKDIR /src
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "/src/main.py"]