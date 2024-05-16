FROM apache/airflow:2.8.3
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt # --no-cache-dir good practise when installing packages using pip. It helps to keep the image lightweight
RUN pip install matplotlib


# Source: https://airflow.apache.org/docs/docker-stack/recipes.html
# Installing the GCP CLI in the container
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

USER 0
# Install AWS CLI to interact with Amazon Web Services, including S3
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf ./aws awscliv2.zip \
    && aws --version

ENV PATH="/root/.local/bin:${PATH}"

USER airflow
ENV S3_BUCKET=marindata


