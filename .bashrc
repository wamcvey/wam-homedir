# .bashrc

# User specific aliases and functions

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Load bash completions if running bash later than 2.04
bash=${BASH_VERSION%.*}; bmajor=${bash%.*}; bminor=${bash#*.}
if [ "$PS1" ] && [ $bmajor -eq 2 ] && [ $bminor '>' 04 ] \
   && [ -f /etc/bash_completion ]; then # interactive shell
	# Source completion code
	. /etc/bash_completion
fi
unset bash bmajor bminor

