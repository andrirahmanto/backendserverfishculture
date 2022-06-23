mongoimport --db fishapi --collection pond --type json --file /Users/andrirahmanto/flask/fishapi/exportdatabase/pond.json --jsonArray
mongoimport --db fishapi --collection pond_activation --type json --file /Users/andrirahmanto/flask/fishapi/exportdatabase/pond_activation.json --jsonArray
mongoimport --db fishapi --collection feed_type --type json --file /Users/andrirahmanto/flask/fishapi/exportdatabase/feed_type.json --jsonArray
mongoimport --db fishapi --collection feed_history --type json --file /Users/andrirahmanto/flask/fishapi/exportdatabase/feed_history.json --jsonArray
mongoimport --db fishapi --collection water_preparation --type json --file /Users/andrirahmanto/flask/fishapi/exportdatabase/water_preparation.json --jsonArray
mongoimport --db fishapi --collection mongoengine.counters --type json --file /Users/andrirahmanto/flask/fishapi/exportdatabase/mongoengine.counters.json --jsonArray