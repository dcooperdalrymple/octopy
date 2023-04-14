#!/bin/sh
set -x
set -e

sudo apt-get update;
sudo apt-get -y install libegl1-mesa-dev libgles2-mesa-dev;
sudo apt-get -y install libsdl2-dev libsdl2-mixer-dev python-dev;
sudo pip3 install --upgrade cython

mkdir ~/ffmpeg_sources || true;
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/ffmpeg_build/lib;

sudo apt-get -y install yasm;
sudo apt-get -y install nasm;

sudo apt-get -y install libx264-dev;
cd ~/ffmpeg_sources;
wget http://download.videolan.org/pub/x264/snapshots/last_x264.tar.bz2;
tar xjf last_x264.tar.bz2;
cd x264-snapshot*;
PATH="$HOME/ffmpeg_build/bin:$PATH" ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/ffmpeg_build/bin" --enable-shared --extra-cflags="-fPIC";
PATH="$HOME/ffmpeg_build/bin:$PATH" make -j4;
make install;
make distclean;

sudo apt-get -y install libmp3lame-dev;

cd ~/ffmpeg_sources;
wget http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz;
tar xzf lame-3.99.5.tar.gz;
cd lame-3.99.5;
./configure --prefix="$HOME/ffmpeg_build" --enable-nasm --enable-shared;
make -j4;
make install;
make distclean;

sudo apt-get -y install libass-dev libfreetype6-dev libtheora-dev libvorbis-dev;
cd ~/ffmpeg_sources;
wget http://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2;
tar xjf ffmpeg-snapshot.tar.bz2;
cd ffmpeg;
PATH="$HOME/ffmpeg_build/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --extra-cflags="-I$HOME/ffmpeg_build/include -fPIC" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --bindir="$HOME/ffmpeg_build/bin" --enable-gpl --enable-libass --enable-libfreetype --enable-libmp3lame --enable-libtheora --enable-libvorbis --enable-libx264 --enable-shared;
PATH="$HOME/ffmpeg_build/bin:$PATH" make -j4;
sudo make install;
make distclean;
hash -r;

sudo pip3 install --upgrade cython nose;
export PKG_CONFIG_PATH=$HOME/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH
sudo -E pip3 install https://github.com/matham/ffpyplayer/archive/master.zip
echo "Add 'export LD_LIBRARY_PATH=~/ffmpeg_build/lib/:\$LD_LIBRARY_PATH' to your env"
