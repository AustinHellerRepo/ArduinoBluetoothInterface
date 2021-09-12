if [ "$EUID" -ne 0 ]; then
  echo "Must run as root in order to update groups"
  exit 1
fi

username=$USER
is_reboot_required=0
if getent group tty | grep -q "\b${username}\b"; then
  echo Already in tty group
else
  usermod -a -G tty $USER
  echo Added to tty group
  is_reboot_required=1
fi
if getent group dialout | grep -q "\b${username}\b"; then
  echo Already in dialout group
else
  usermod -a -G dialout $USER
  echo Added to dialout group
  is_reboot_required=1
fi
if [ "$is_reboot_required" -eq "0" ]; then
  echo No reboot required
else
  echo Reboot required
fi
