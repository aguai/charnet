author := Adriano J. Holanda
proj := booknet
url := ajholanda@holanda.xyz:~/www/data/$(proj)

# BOOKNET
booknet_data := data/acts.csv data/arthur.csv \
		data/luke.csv data/tolkien.csv data/hobbit.csv \
		data/newton.csv	data/pythagoras.csv
booknet_pajek := $(patsubst data/%.csv,%.net,$(booknet_data))

# SGB
sgb_data := sgb/david.dat sgb/huck.dat
sgb_pajek := $(patsubst sgb/%.dat,%.net,$(sgb_data))

# GRAPHS
graphs := $(booknet_pajek)
graphs += $(sgb_pajek)

# Images
pictures := $(patsubst %.net,%.png,$(graphs))

# Excel file
excel := $(proj).xlsx rank.xlsx

VPATH = data

# results (output)
run: $(pictures)

# Convert data
## pythagoras and newton have their own freq file
## we have to overwrite the freq file generated
## by convert.pl
$(booknet_pajek): convert.pl $(booknet_data)
	@perl $<
	@cp data/pythagoras.freq data/newton.freq .

## convert sgb files to pajek format
$(sgb_pajek): sgb.pl $(sgb_data)
	perl $<

# Process data
$(pictures): booknet.py $(graphs)
	python $<

# Tangle code
booknet.py: booknet.mdw
	ptangle $<

# Weave documentation
booknet.html: booknet.mdw
	pweave -f md2html $<

booknet.pdf: booknet.mdw
	@pweave -f pandoc2latex $<
	@pdflatex booknet.tex

# homepage
index.html: index.md
	asciidoctor $<

sync: index.html $(pictures) $(booknet_data) $(sgb_data)
	scp $^ $(url)

.PHONY: clean sync

clean: 
	@$(RM) `cat .gitignore`
	@$(RM) *.freq

# BUFFER
$(excel): main.py $(booknet_pajek) $(sgb_pajek)
	python $<

