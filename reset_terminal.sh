#!/bin/bash
# Reset terminal to normal state

# Reset terminal
reset

# Disable mouse mode explicitly
printf '\e[?1000l'  # Disable mouse tracking
printf '\e[?1003l'  # Disable any mouse tracking
printf '\e[?1015l'  # Disable urxvt mouse mode
printf '\e[?1006l'  # Disable SGR mouse mode

# Clear screen
clear

echo "Terminal reset complete!"