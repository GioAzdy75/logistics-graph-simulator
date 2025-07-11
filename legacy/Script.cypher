LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CREATE (:Intersection {id: row.`node_id:ID`, lat: toFloat(row.`lat:float`), lon: toFloat(row.`lon:float`)});

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (u:Intersection {id: row.`:START_ID`})
MATCH (v:Intersection {id: row.`:END_ID`})
MERGE (u)-[r:STREET]->(v)
SET 
    r.name = row.`name:string`,
    r.length = toFloat(row.`length:float`),
    r.maxspeed = CASE WHEN row.`maxspeed:int` IS NOT NULL THEN row.`maxspeed:int` ELSE 50 END,
    r.weight = CASE WHEN row.`weight:float` IS NOT NULL THEN toFloat(row.`weight:float`) ELSE toFloat(row.`length:float`)/50 END;
