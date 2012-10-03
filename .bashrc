# .bashrc

# User specific aliases and functions

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

run_bash_completion() {
	# Run bash completions as a function so it doesn't inherit 
	# my error handler.

	# Load bash completions if running bash later than 2.04
	bash=${BASH_VERSION%.*}; bmajor=${bash%.*}; bminor=${bash#*.}
	if [ "$PS1" ] && [ $bmajor -eq 2 ] && [ $bminor '>' 04 ] \
	   && [ -f /etc/bash_completion ]; then # interactive shell
		# Source completion code
		. /etc/bash_completion
		echo
	fi
	unset bash bmajor bminor
}
run_bash_completion
if [ "$PS1" ]
then
	[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*
fi

PATH=$PATH:$HOME/.rvm/bin # Add RVM to PATH for scripting
