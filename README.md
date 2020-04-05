# PECSN-DataAnalysis

## Branch -> dev/nome_di_quello_che_sto_facendo

## Settings.ini (occhio alla sintassi)
- working_csv -> CSV da cui estrarre i dati
- export_directory -> cartella in cui salvare i grafici, se esportati come file.
- draw_plots = yes/no -> abilita/disabilita la visualizzazione dei grafici a schermo.
- save_to_file = yes/no -> abilita/disabilita l'esportazione dei grafici su file.
- cashier_level -> Livelli della cassiera presenti nella simulazione. Non modificare con aggiunte, deve essere una lista.
- statistic_list -> Statistiche di interesse. Non modificare con aggiunte (le statistiche della coda non sono supportate), deve essere una lista.

- la configurazione in Plot_Profile è puramente estetica. Le proprietà dei grafici sono lette da PlotBuilder: non rimuovere le proprietà e, nel caso volessi aggiungerne, aggiungi il relativo codice nella suddetta classe.
- matplotlib_style -> https://matplotlib.org/3.2.1/gallery/style_sheets/style_sheets_reference.html 

## TODO:
1) aggiungere supporto per statistiche coda (bisogna fare il sampling ad istanti temporali basato su colonna vectime. 
   ### N.B Ad ora le colonne vectime NON sono caricate e le colonne vecvalue delle code sono caricate così come sono (tradotto: non    sono utili così come sono).
2) modificare granularità asse x e y in base al grafico (credo  si dovrà fare a mano in base al grafico).
3) modificare colori linee (per farle più belline, se serve).


<br>
<br>
<br>

### TODO "forse, chi lo sa, lo scopriremo solo vivendo e soffrendo":
0) Aggiungere scatterplot (????, non credo serva).
1) aggiungere indicatori riassuntivi su linee (valor medio, etc) se possibile/se serve, altrimenti si metteranno a mano o direttamente nel documento.
###


