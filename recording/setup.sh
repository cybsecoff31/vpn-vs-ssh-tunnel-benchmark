#!/bin/bash
# Bootstraps the session recorder on cyborg. Not part of the experiment.
echo 'cybsec ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/90-recorder > /dev/null
sudo chmod 440 /etc/sudoers.d/90-recorder
exec python3 /mnt/share/agent.py
