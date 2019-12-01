list_file = output/file_list.yml
sequence_file = config/sequence.yml
plot_file = config/plot.yml
ntuple_directory = ntuples
output_directory = output

curator:
	@echo "===================="
	@echo "running fast_curator"
	@echo "===================="
	rm -f $(list_file)
	mkdir -p $(output_directory)
	fast_curator -o $(list_file) -t background -d Background --mc -m type=nominal $(ntuple_directory)/prediction.root
	fast_curator -o $(list_file) -t signal -d Signal --mc -m type=nominal $(ntuple_directory)/prediction.root
	fast_curator -o $(list_file) -t pseudodata -d Data --data $(ntuple_directory)/data.root

carpenter: curator
	@echo "====================="
	@echo "running fast_carpenter"
	@echo "====================="
	fast_carpenter $(list_file) $(sequence_file) --outdir $(output_directory)

plotter: carpenter
	@echo "===================="
	@echo "running fast_plotter"
	@echo "===================="
	fast_plotter -c $(plot_file) $(output_directory)/tbl*.csv --outdir $(output_directory)


clean: clean-curator clean-carpenter clean-plotter

clean-curator:
	rm -f $(list_file)

clean-carpenter:
	rm -f $(output_directory)/*csv

clean-plotter:
	rm -f $(output_directory)/*png
