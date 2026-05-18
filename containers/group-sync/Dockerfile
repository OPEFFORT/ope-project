FROM quay.io/operate-first/opf-toolbox:v0.8.0

# Create the destination directory
WORKDIR /scripts

# Install pip first
RUN dnf install -y python3-pip

# Install requirements first to maximize caching
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Install the group-sync application
COPY group-sync.py ./
