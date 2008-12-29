#!/bin/ksh

#setup the environment
umask 022

# For when I'm travelling
# TZ='America/New_York'; export TZ		# EST
# TZ='America/Chicago'; export TZ		# CST

# XXX quick hack for now
# . $HOME/bin/kill-locale

PATH=${HOME}/bin
for dir in \
	/usr/local/bin /opt/local/bin \
	/usr/local/sbin /opt/local/sbin \
	/usr/local/etc /opt/local/etc \
	/usr/cisco/bin /usr/cisco/sbin /router/bin \
	/usr/gnu/bin /usr/local/gnu \
	/usr/local/lib \
	/usr/local/news /usr/local/perl /usr/local/tcl \
	/usr/local/tex/bin \
	/usr/local/misc \
	/usr/ccs/bin /opt/SUNWspro/bin /usr/lang \
	/usr/local/java /usr/local/java/bin /usr/java/bin \
	/usr/local/xep/bin /usr/local/xep \
	/bin /etc /usr/etc /usr/sbin /sbin /usr/bin \
	/usr/ucb /usr/bsd \
	/usr/X11R6/bin /p/X11R6 /usr/local/X11 /opt/x11r5/bin \
	/usr/bin/X11 /opt/X11/x11r5/bin /usr/openwin/bin \
	/usr/local/spa \
	/usr/autospa/bin /usr/autospa/scripts \
	/usr/local/spa-report/bin \
	/usr/local/ssl/bin /usr/local/pgp \
	/usr/local/netpbm /usr/local/pbm \
	/usr/local/graphviz/bin \
	/usr/local/www /usr/local/mozilla \
	/usr/local/MH /usr/local/mh /usr/local/mh/bin /usr/local/nmh/bin \
	/usr/lib/nmh \
	/opt/req/bin \
	/opt/pure/purify \
	/usr/local/scanner /usr/local/cfs /usr/local/jdk/bin \
	/usr/ov/bin /usr/kerberos/ov/bin \
	/cygdrive/c/WINDOWS/system32 /cygdrive/c/WINDOWS \
	/cygdrive/c/WINDOWS/i386 \
	/cygdrive/c/winnt/system32 /cygdrive/c/winnt /cygdrive/c/winnt/i386 \
	/cygdrive/c/spatools \
	${HOME}/hosts 
do
	if [ -d $dir ]; then
		PATH=${PATH}:${dir}
	fi
done

#MANPATH=$HOME/man:/usr/local/man:/usr/X11R6/man:/usr/X386/man:/usr/gnu/man:\
#/usr/share/man:/usr/local/mh/man


CDPATH=".:${HOME}:${HOME}/projs:/data:/usr/autospa:${HOME}/lib/personal"
EDITOR=vi
# BASH_ENV gets executed for non-interactive bash sessions (shell scripts)
BASH_ENV=$HOME/.bashrc
# ENV gets executed for interactive non-bash sessions
ENV=$HOME/.kshrc

if [ -f $HOME/lib/dircolors.db ] && dircolors > /dev/null 2>/dev/null
then
	eval `dircolors  -b  $HOME/lib/dircolors.db`
fi
HISTSIZE=1500
HISTIGNORE="&:[bf]g:exit"
export HISTIGNORE
USER=${USER:-${LOGNAME:-`whoami || whoiam`}}
TMP=/var/tmp/${USER}
HISTFILE=${TMP}/.hist$$
HOST=`hostname || uuname -l ; ` 
if [ -f $HOME/lib/hosts ]
then
	HOSTFILE=$HOME/lib/hosts
else
	HOSTFILE=/etc/hosts
fi
SHORTHOST=${HOST%%.*}
#LD_LIBRARY_PATH=/usr/lib:/usr/local/X11/lib:/usr/x11r5/lib:/usr/openwin/lib

NAME="William McVey"
# XAUTHORITY=${HOME}/.Xauthority
ORGANIZATION="Cisco Systems"
PAGER=$( which less 2>/dev/null ) || \
	PAGER=`which more 2>/dev/null ` || \
	( PAGER=/bin/cat && echo "No pager found.  Using /bin/cat." >&2 /dev/tty ; )
if [ -d ${HOME}/lib/pgp ] ; then
	PGPPATH=${HOME}/lib/pgp
	export PGPPATH
fi

ROOTPROMPT='$'
if [ "wam" = "$USER" ] ; then
	USERAT=""
elif [ "root" = "$USER" ] ; then
	USERAT=""
	ROOTPROMPT='#'
else
	USERAT="${USER}@"
fi
case "$SHELL" in
*bash)
	# The brackets indicate escape codes so command editing doesn't get
	# screwed up
	PS1='\[`color yellow`\]${USERAT}${SHORTHOST} ${DIR}\[`color off`\] ${ROOTPROMPT} '
	;;
*ksh|sh)
	PS1='`color yellow`${USERAT}${SHORTHOST} ${DIR}`color off` ${ROOTPROMPT} '
	;;
*)
	PS1='${USERAT}${SHORTHOST} ${DIR} ${ROOTPROMPT} '
	;;
esac

PYTHONPATH=/home/wam/lib/python 
for dir in /usr/local/spa-report/lib/python /usr/autospa/lib/python /usr/autospa/py-modules/lib 
do
	if [ -d "$dir" -o -L "$dir" ]
	then
		PYTHONPATH="$PYTHONPATH":"$dir"
	fi
done
export PYTHONPATH
PYTHONSTARTUP=$HOME/.pythonrc

for dir in /usr/local/java /usr/local/jdk /usr/java /usr/lib/jvm/java-1.5.0-sun
do
	if [ -d "$dir" ]; then
		JAVA_HOME=$dir 
		export JAVA_HOME
		break
	fi
done


[ "${PWD}" = "${HOME}" ] && DIR='~'
VISUAL=vi

#
# Application specific environment variables
#

ENTOMB=yes ; export ENTOMB
GIT_PAGER="less -RFX" ; export GIT_PAGER
LESSOPEN="| lesspipe %s" 
LESS="-CedmPm?f%f:<stdin>. ?eeof:?pb%pb:\?.\%. ?lb%lb." 
export LESSOPEN LESS

RSYNC_RSH=ssh ; export RSYNC_RSH

#RNINIT='-m -M -s -e -q' 
TRNINIT='-B -t -p -s -M -m'
export RNINIT TRNINIT

MINICOM='-o'
export MINICOM

XKEYSYMDB=/usr/X11R6/lib/X11/XKeysymDB
XNLSPATH=/usr/X11R6/lib/X11/netscape/nls
export XNLSPATH XKEYSYMDB

if [ -d ${HOME}/.app-defaults ] ; then
	XAPPLRESDIR=${HOME}/.app-defaults/
	export XAPPLRESDIR
fi
SGML_CATALOG_FILES=/etc/sgml/dsssl.cat:/etc/sgml/xml-docbook.cat:/etc/sgml/sgml-docbook.cat:/etc/sgml/sgml-docbook-3.1.cat
export SGML_CATALOG_FILES

if [ -e ${HOME}/tools/forrest ]
then
	export FORREST_HOME=${HOME}/tools/forrest
	PATH=${PATH}:${HOME}/tools/forrest/bin
fi

GDFONTPATH=/mnt/windows/windows/Fonts:/usr/X11R6/lib/X11/fonts/mozilla-fonts:/usr/X11R6/lib/X11/fonts/TTF:/usr/X11R6/lib/X11/fonts/Type1:$HOME/.cxoffice/dotwine/fake_windows/Windows/Fonts
export GDFONTPATH

export BASH_ENV CDPATH DISPLAY EDITOR ENV LD_LIBRARY_PATH \
	HISTSIZE HISTFILE HOST MANPATH NAME ORGANIZATION PS1 USER \
	PRINTER PAGER PATH PYTHONSTARTUP  RNINIT TRNINIT SHELL SHORTHOST \
	TMP TERM TERMCAP VISUAL XAUTHORITY

alias ls="/bin/ls -F"

#setup the terminal 
if [ -z "$TERM" ]
then
	eval `tset -s -Q -m 'unknown:?vt100' -m 'network:?xterm' -m 'dialup:cons25'`
	# we do the stty on seperate lines so if one bombs out,
	# it doesn't affect others
	stty kill "^U" intr "^C" erase "^H" susp "^Z" 
	stty werase "^W"
	stty status "^T" 2> /dev/null
fi
set +o noglob 
set -o vi 
set -o viraw 2> /dev/null

[ "${TERM}" = "z29" ] && z29init
if [ "${TERM}" = "screen" ]; then
	if [ "${USER}" != "wm218226" ]; then
		echo -n "\"${USER}\\"
	else
		echo -n "\"${SHORTHOST}\\"
	fi
fi

[ -d "${TMP}" ] ||  mkdir ${TMP}
[ -d ${TMP}/outbox ] || mkdir ${TMP}/outbox
[ -d ${TMP}/junk ] || mkdir ${TMP}/junk
[ -f $HOME/lib/dircolors.db ] && eval `dircolors $HOME/lib/dircolors.db`
[ -f $HOME/.profile-`hostname` ] && . $HOME/.profile-`hostname`
[ -f $HOME/lib/aliases ] && . $HOME/lib/aliases

if [ -n "${DISPLAY}" ]; then
	echo "Display is: ${DISPLAY}"
fi
echo
mesg y 2>/dev/null


# Convenience variables (should be no need to export them though)
nsi=whois.networksolutions.com
arin=whois.arin.com
arin=whois.ripe.com
ip_re='[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*'

trap "echo \(\$?\)" ERR 2>/dev/null
trap '/bin/rm -f $HISTFILE' EXIT HUP TERM

if [ -f /etc/bash_completion ]
then
	. /etc/bash_completion
fi

_optcomplete()
{
	COMPREPLY=( $( \
	COMP_LINE=$COMP_LINE  COMP_POINT=$COMP_POINT \
	COMP_WORDS="${COMP_WORDS[*]}"  COMP_CWORD=$COMP_CWORD \
	OPTPARSE_AUTO_COMPLETE=1 $1 ) )
}

if [ -f /usr/local/django-trunk/extras/django_bash_completion ]
then
	. /usr/local/django-trunk/extras/django_bash_completion
fi

. ${HOME}/lib/aliases

