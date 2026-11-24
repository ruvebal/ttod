# ATELIER-IA memoria → PDF (pandoc + XeLaTeX; UDIT/ECSIT logos from ../ethics/assets)
export PATH := /Library/TeX/texbin:/opt/homebrew/bin:$(PATH)
DOC := MEMORIA-TECNICA-ATELIER-IA-ES
PANDOC_OPTS := --pdf-engine=xelatex -H header.tex \
  -V geometry:a4paper,margin=2.2cm,top=2.8cm -V fontsize=10.5pt \
  -V mainfont="Helvetica Neue" -V lang=es -V colorlinks=true -V linkcolor=uditnavy -V urlcolor=uditnavy

.PHONY: all
all: $(DOC).pdf

$(DOC).pdf: $(DOC).md header.tex
	pandoc $(DOC).md $(PANDOC_OPTS) -o $@
