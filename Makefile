VER=3.0.5
RELEASE=pyvolve-${VER}.zip
WEBSITE=http://setiathome.berkeley.edu/~aparsons
REMHOST=aparsons@jill.ssl.berkeley.edu

# DIRECTORIES
SCR=scripts
EDEN=eden

# SCRIPTS
RUNLIFE=${SCR}/run_life.py
VISUALIZE=${SCR}/visuals.py
CRITTERS=${SCR}/critter.py
SUBMIT=${SCR}/submit.py

# FILES
CRIT=3.py
EVOLOG=evolog.gz

# FILES TO BACKUP
FILES=${SCR}/*.py ${CRIT} Makefile README.txt

life:
	rm -rf halt.txt
	if [ -s ${EVOLOG} ]; then gunzip -c ${EVOLOG} | gzip > ${EVOLOG}.tmp; mv ${EVOLOG}.tmp ${EVOLOG} 2> /dev/null; fi
	${RUNLIFE}

conf:
	mkdir -p ${EDEN}

real_clean: clean
	rm -rf ${EDEN}/*.py
	rm -rf ${EVOLOG}

clean:
	rm -rf nohup.out ${ADAM} halt.txt ${EDEN}/*stackdump* *.tmp ${EDEN}/scripts/d_parser* run_life.st ${EDEN}/d_parser*

halt:
	echo 1 > ./halt.txt

post: 
	zip -qr ${RELEASE} ${FILES}
	scp ${RELEASE} ${REMHOST}:pyvolve
	scp ${RELEASE} ${REMHOST}:public_html/pyvolve/pyvolve.zip
	scp ${CRIT} ${REMHOST}:public_html/pyvolve/${CRIT}
	rm -rf ${RELEASE}

update:
	wget ${WEBSITE}/pyvolve/pyvolve.zip
	unzip -qq -u pyvolve.zip
	rm -rf pyvolve.zip

demograph:
	${DEMOGRAPH} ${EDEN}

visuals:
	rm -rf halt.txt
	if [ -s ${EVOLOG} ]; then gunzip -c ${EVOLOG} | gzip > ${EVOLOG}.tmp; mv ${EVOLOG}.tmp ${EVOLOG} 2> /dev/null; fi
	${RUNLIFE} -v

viewlog:
	gunzip -c evolog.gz | tail -80

submit: halt
	${SUBMIT}

