PYTHONPATH=${HOME}/lib/python
for dir in \
	/usr/local/spa-report/lib/python \
	/usr/autospa/lib/python \
	/usr/autospa/py-modules/lib
do
	if [ -d "$dir" -o -L "$dir" ]
	then
		PYTHONPATH="$PYTHONPATH":"$dir"
	fi
done
PYTHONSTARTUP=$HOME/.pythonrc
PYTHONDOCS=/usr/share/doc/python-doc
export PYTHONPATH PYTHONDOCS PYTHONSTARTUP

