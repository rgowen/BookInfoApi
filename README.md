# BookInfoApi
A Python/Flask based API for grabbing book info from Amazon

Book information is retrieved by ISBN from Amazon and stored in a sqlite database. If information for the same ISBN is requested within the same 24hr period, the API will not access Amazon and instead will return stored data to avoid Amazon API request limits.   
MWS credentials for accessing the Amazon Product API are read from a user-created mws.cfg file. 
