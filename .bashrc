# .bashrc

# User specific aliases and functions

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi


_optcomplete()
{
	COMPREPLY=( $( \
	COMP_LINE=$COMP_LINE  COMP_POINT=$COMP_POINT \
	COMP_WORDS="${COMP_WORDS[*]}"  COMP_CWORD=$COMP_CWORD \
	OPTPARSE_AUTO_COMPLETE=1 $1 ) )
}

