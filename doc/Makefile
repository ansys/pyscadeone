# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto -W
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
PLANTUML      = java -jar ../plantuml.jar


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Customized clean due to examples gallery
clean: 
	rm -rf "$(BUILDDIR)"


pdf:
	@echo no PDF generation
	
svg:
	@echo "Generating SVG files from PlantUML files"
	@$(PLANTUML) -version | head -1
	@$(PLANTUML) -splash -tsvg  "$(SOURCEDIR)/**/*.puml"
	@echo "Done"
