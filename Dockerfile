# Use a base image compatible with ARM64 (Apple Silicon)
FROM --platform=linux/arm64 ubuntu:22.04

RUN mkdir /app /app/recordings /app/screenshots


# Set the working directory inside the container
WORKDIR /app

# Install necessary dependencies including Chrome and ChromeDriver for ARM64
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    pulseaudio \
    pavucontrol \
    curl \
    sudo \
    pulseaudio \
    xvfb \
    libnss3-tools \
    ffmpeg \
    xdotool \
    unzip \
    x11vnc \
    libfontconfig \
    libfreetype6 \
    xfonts-scalable \
    fonts-liberation \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    xterm \
    vim \
    wget \
    gnupg \
    ca-certificates \
    qemu-user-static \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium for ARM64 (native support)
RUN apt-get update \
    && apt-get install -y chromium \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver for ARM64 (using x86_64 version with emulation)
RUN CHROME_VERSION=$(chromium --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+') \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}") \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver \
    && echo '#!/bin/bash\nqemu-x86_64 /usr/local/bin/chromedriver "$@"' > /usr/local/bin/chromedriver-wrapper \
    && chmod +x /usr/local/bin/chromedriver-wrapper

RUN usermod -aG audio root
RUN adduser root pulse-access

ENV DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
ENV XDG_RUNTIME_DIR=/run/user/0


RUN mkdir -p /run/dbus
RUN chmod 755 /run/dbus

RUN rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse


RUN dbus-daemon --system --fork



RUN wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz

RUN tar -xvf pa_stable_v190700_20210406.tgz

RUN mv portaudio /usr/src/

WORKDIR /usr/src/portaudio

RUN ./configure && \
    make && \
    make install && \
    ldconfig

RUN pip3 install \
    pyaudio \
    click \
    opencv-python \
    Pillow \
    fastapi \
    uvicorn \
    python-multipart \
    undetected-chromedriver

RUN echo 'user ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN adduser root pulse-access

RUN mkdir -p /var/run/dbus

RUN dbus-uuidgen > /var/lib/dbus/machine-id

#RUN dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address

WORKDIR /app

#COPY chromedriver /usr/bin/chromedriver

# Copy your application code to the container
COPY . /app

# Set any environment variables if required
# GLADIA_API_KEY will be provided at runtime
ENV X_SERVER_NUM=1
ENV SCREEN_WIDTH=1280
ENV SCREEN_HEIGHT=1024
ENV SCREEN_RESOLUTION=1280x1024
ENV COLOR_DEPTH=24
ENV DISPLAY=:${X_SERVER_NUM}.0

RUN touch /root/.Xauthority
RUN chmod 600 /root/.Xauthority

RUN rm /run/dbus/pid
RUN mv pulseaudio.conf /etc/dbus-1/system.d/pulseaudio.conf

# Expose the API port
EXPOSE 8000

# Define the command to run your application
CMD ["/app/entrypoint.sh"]


