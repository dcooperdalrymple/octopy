#!/bin/bash

echo "Starting installation..."

echo "Updating package index files..."
sudo apt-get update
echo "Installing apt depedencies..."
sudo apt-get install python3-pip git libasound2-dev libjack-dev
echo "Installing python dependencies..."
sudo pip3 install pyalsaaudio python-rtmidi pyserial wave mido pygame

if [ -d "~/octopy" ]; then

    echo -n "Would you like to update your Octopy install? All local changes will be erased. [y/N] "
    read
    if [[ "$REPLY" =~ (yes|y|Y)$ ]]; then
        echo "Updating repository..."
        cd ~/octopy
        git checkout master
        git fetch --all
        git reset --hard origin/master
    fi

else

    echo "Cloning repository..."
    cd ~/
    git clone https://github.com/dcooperdalrymple/octopy.git

fi

echo "Updating git submodules..."
cd ~/octopy
git submodule init
git submodule update

echo -n "Would you like to install pyvidplayer2? (recommended) [y/N] "
read
if [[ "$REPLY" =~ (yes|y|Y)$ ]]; then
    echo "Installing pyvidplayer2..."
    sudo apt-get install libmediainfo-dev libavcodec-dev libavfilter-dev libavdevice-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev libpostproc-dev ffmpeg
    sudo apt-get install portaudio19-dev python3-pyaudio
    sudo pip3 install pyvidplayer2
fi

echo -n "Would you like to install MPV? [y/N] "
read
if [[ "$REPLY" =~ (yes|y|Y)$ ]]; then
    echo "Installing MPV..."
    sudo apt-get mpv
fi

echo -n "Would you like to install FFmpeg? (recommended) [y/N] "
read
if [[ "$REPLY" =~ (yes|y|Y)$ ]]; then
    echo "Installing FFmpeg..."
    sudo apt-get ffmpeg
fi

echo -n "Would you like to install hello video? (recommended) [y/N] "
read
if [[ "$REPLY" =~ (yes|y|Y)$ ]]; then
    echo "Installing hello video..."
    cd ~/
    git clone https://github.com/adafruit/pi_hello_video.git
    cd ~/pi_hello_video
    chmod +x ./rebuild.sh
    ./rebuild.sh
    sudo make install
fi

echo "Copying default configuration..."
sudo cp ~/octopy/config.ini /root/octopy.ini

echo -n "Would you like to run Octopy on boot? (recommended) [y/N] "
read
if [[ "$REPLY" =~ (yes|y|Y)$ ]]; then
    echo "sudo python3 ~/octopy/octo.py" >> ~/.bashrc
fi

echo
echo "Octopy installation complete!"
echo "Additional Steps:"
echo "- Make sure to edit your /root/octopy.ini file to best fit your system."
echo "- Run 'sudo python3 ~/octopy/octo.py --verbose' to test your system before deployment and scan available alsa devices."
echo "- If using GPIO serial for MIDI input/output, you may need to enable \"Serial Port\" under \"Interface Options\" with 'sudo raspi-config' (do not enable login shell over serial)."
echo "- If you would like to start octopy after boot automatically, use 'sudo raspi-config' to enable auto-login to console. (recommended)"
echo "- If you would like to make your boot media read-only, use 'sudo raspi-config' to enable \"Overlay File System\". (recommended after configuration)"
