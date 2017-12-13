all: charnet.py
	./$< -a

charnet.py: book.py lobby.py

help: charnet.py
	./$< -h

clean:
	$(RM) *.csv *.dot *.log *.pdf *.png *.pyc centr.tex global.tex legomenas.tex

.PHONY: all clean help
