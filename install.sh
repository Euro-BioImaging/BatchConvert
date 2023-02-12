SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; )
mkdir -p $HOME/.batchconvert/bin;
chmod -R 777 $HOME/.batchconvert;
chmod -R 777 $SCRIPTPATH;

#echo $(ls $SCRIPTPATH);

echo $'#!/usr/bin/env bash' > $HOME/.batchconvert/bin/batchconvert && \
echo "$SCRIPTPATH/batchconvert.sh '$@'" >> $HOME/.batchconvert/bin/batchconvert && \
chmod 777 $HOME/.batchconvert/bin/batchconvert;

#cat $HOME/.batchconvert/bin/batchconvert;

if ! echo $PATH | tr ":" "\n" | grep "batchconvert" &> /dev/null;
then
	echo "export PATH="$HOME/.batchconvert/bin:$PATH"" >> $HOME/.bashrc;
fi;

source $HOME/.bashrc;
source $HOME/.bashrc;
