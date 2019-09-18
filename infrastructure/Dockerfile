FROM python:3.7

RUN pip install awscli

WORKDIR /home

ENV KUBEONE_VERSION=0.9.2

RUN curl -LO https://github.com/kubermatic/kubeone/releases/download/v${KUBEONE_VERSION}/kubeone_${KUBEONE_VERSION}_linux_amd64.zip
RUN unzip kubeone_${KUBEONE_VERSION}_linux_amd64.zip
RUN mv kubeone /usr/local/bin

ENV TERRAFORM_VERSION=0.12.9

RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN mv terraform /usr/local/bin/

ENV AWS_ACCESS_KEY_ID=AKIAJB57ZSNOCXIQW5EA
ENV AWS_SECRET_ACCESS_KEY=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