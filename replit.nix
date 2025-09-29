{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.pip
    pkgs.portaudio
    pkgs.alsa-lib
    pkgs.pulseaudio
  ];
}
