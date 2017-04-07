all: charnet.py
	./$< -a

charnet.py: book.py lobby.py

help: charnet.py
	./$< -h

clean:
	$(RM) *.csv *.png global.tex hapax.tex

.PHONY: all clean help
