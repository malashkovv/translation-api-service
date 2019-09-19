FROM python:3.7

RUN pip install awscli

WORKDIR /home/tmp

ENV KUBEONE_VERSION=0.9.2
ENV TERRAFORM_VERSION=0.12.9
ENV KUBECTL_VERSION=1.16.0

RUN curl -LO https://github.com/kubermatic/kubeone/releases/download/v${KUBEONE_VERSION}/kubeone_${KUBEONE_VERSION}_linux_amd64.zip && \
    unzip kubeone_${KUBEONE_VERSION}_linux_amd64.zip && \
    mv kubeone /usr/local/bin

RUN curl -LO https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/

WORKDIR /home

RUN rm -r /home/tmp

ENV AWS_ACCESS_KEY_ID=AKIAJB57ZSNOCXIQW5EA
ENV AWS_SECRET_ACCESS_KEY=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