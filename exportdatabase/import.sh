mongoimport --db fishapi --collection pond --type json --file /var/www/html/fishapi/exportdatabase/pond.json --jsonArray
mongoimport --db fishapi --collection feed_type --type json --file /var/www/html/fishapi/exportdatabase/feed_type.json --jsonArray
mongoimport --db fishapi --collection feed_history --type json --file /var/www/html/fishapi/exportdatabase/feed_history.json --jsonArray
mongoimport --db fishapi --collection mongoengine.counters --type json --file /var/www/html/fishapi/exportdatabase/mongoengine.counters.json --jsonArray