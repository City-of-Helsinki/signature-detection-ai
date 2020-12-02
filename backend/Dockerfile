FROM fastai/fastai:latest

RUN apt update && apt install -y poppler-utils

#COPY resnet34-333f7ec4.pth /root/.cache/torch/hub/checkpoints/resnet34-333f7ec4.pth

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