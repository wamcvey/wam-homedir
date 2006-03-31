#!/bin/sh
HOME=${HOME:-/export/home/wam}
PATH=$HOME/bin:/usr/local/bin:/usr/local/etc:/opt/local/bin:/opt/local/etc:/usr/local/lib:/bin:/etc:/usr/sbin:/sbin:/usr/bin:$PATH
export PATH
export HOME

cd $HOME/projs/cvs-changes
rm -f cvslog.txt errors

if [ "$1" = "-n" ];
then
	mail_it=false
	shift
else
	mail_it=true
fi


now=`strftime "%c"`
#before=`strftime -s "NOW - ${1:-1} DAYS" "%c %Z"` 
#cvsdate=-d\'${before}\<${now}\'
before=`strftime -s "NOW - ${1:-1} DAYS" "%c"`

for dir in *
do
	if [ ! -d "$dir" ]
	then
		continue
	fi
	rm -f changes-$dir
	(
	cd $dir
	cvs -q update -dP >/dev/null 2>>../errors
	cvs2cl --stdout -l "-d'$before<$now'" 2>>../errors > ../changes-$dir
	#cvs2cl -f ../changes-$dir -l "${cvsdate}" 2>/dev/null
	)
	if [ -s changes-$dir ]
	then
		echo "CHANGES in $dir" >> cvslog.txt
		echo "========================" >> cvslog.txt
		cat changes-$dir >> cvslog.txt
		echo >> cvslog.txt
		echo >> cvslog.txt
	fi
	rm -f changes-$dir
done

if [ -s cvslog.txt ]
then
	if $mail_it
	then
		mailx -s "cvs logs from $before to $now" spacvs-autospa@cisco.com < cvslog.txt
	else
		cat cvslog.txt
	fi
fi

