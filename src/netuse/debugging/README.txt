En Bor:
	simulate
		for es in ExecutionSet.objects.get_unsimulated()
			Tarda 17 segundos en traerse 35MBs de Odin y ocupando 10% de RAM (de 8GBs)


En Odin (mongod):
	tcpflow -i eth1 -C port 27017 > tela.txt
		Con esto hemos visto que al hacer un simple ExecutionSet.objects.get_unsimulated() usando mongoengine,
		se trae 35MB a memoria, que expandida en objetos, ocupan alrededor de 10% de RAM.
		
		Puede estar relacionado con el uso, o con el estado de Lazy Loading en mongoengine:
			http://mongoengine.org/roadmap.html
		O con cómo lo uso:
			http://stackoverflow.com/questions/9841359/is-this-possible-to-lazily-query-the-database-with-mongoengine-python
		