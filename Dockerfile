
FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-devel
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub && \
    apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub
RUN apt-get update && \
    apt-get install -y wget && \
    wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | apt-key add - && \
    apt-get update && \
    apt-get install -y git && \
    apt-get install libsndfile1 -y && \
    apt install ffmpeg -y && \
    apt-get clean


COPY requirements.txt /whisperx_api/requirements.txt 
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install git+https://github.com/m-bain/whisperx.git
RUN pip install jupyter ipykernel
RUN pip install -r /whisperx_api/requirements.txt
WORKDIR /whisperx_api

EXPOSE 8888
# Use external volume for data
ENV NVIDIA_VISIBLE_DEVICES 1
CMD ["bash"]
