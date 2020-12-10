FROM fastai/fastai:2020-11-15
# Note: there is a bug in more recent images. I've filed a bug
# report and once it's resolved the :latest tag could be used.

RUN apt update && apt install -y poppler-utils

COPY hki_sig_ml /ml_lib

WORKDIR /ml_lib

RUN pip install pdf2image

RUN python setup.py install

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT ["python"]

CMD ["run_server.py"]
