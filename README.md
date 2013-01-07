Imports all cities in the US, including long. lat. postal code. 
Creates three tables 'city', 'county', 'state'. I also included a db dump,
will update the dump every time i change the script

##TABLE -> FIELD NAME
=============================================
	state -> id
		  -> name
		  -> abbr

	county -> id
		   -> county (will rename this to 'name')
		   -> state_id 

	city -> id
		 -> name
		 -> postal_code
		 -> latitude
		 -> longitude
		 -> state_id
		 -> county_id

	>> GeoNames data dump is here: http://download.geonames.org/export/dump/