CREATE (d1:User:Driver {
    id: 'driver_001',
    first_name: 'Juan',
    last_name: 'Pérez',
    email: 'juan.perez@logistics.com',
    password_hash: '$2b$12$example_hash_1',
    available: true,
    working_hours: 'morning'
});
CREATE (d2:User:Driver {
    id: 'driver_002',
    first_name: 'María',
    last_name: 'García',
    email: 'maria.garcia@logistics.com',
    password_hash: '$2b$12$example_hash_2',
    available: true,
    working_hours: 'afternoon'
});
CREATE (d3:User:Driver {
    id: 'driver_003',
    first_name: 'Carlos',
    last_name: 'López',
    email: 'carlos.lopez@logistics.com',
    password_hash: '$2b$12$example_hash_3',
    available: false,
    working_hours: 'night'
});
CREATE (a1:User:Admin {
    id: 'admin_001',
    first_name: 'Ana',
    last_name: 'Rodríguez',
    email: 'ana.rodriguez@logistics.com',
    password_hash: '$2b$12$example_hash_admin_1',
    role: 'super_admin'
});
CREATE (a2:User:Admin {
    id: 'admin_002',
    first_name: 'Roberto',
    last_name: 'Martín',
    email: 'roberto.martin@logistics.com',
    password_hash: '$2b$12$example_hash_admin_2',
    role: 'operations_manager'
});
CREATE (t1:Trip {
    id: 'trip_001',
    started_at: datetime('2024-01-15T08:00:00'),
    ended_at: datetime('2024-01-15T12:30:00'),
    total_distance: 45.5,
    total_time: 270
});
CREATE (t2:Trip {
    id: 'trip_002',
    started_at: datetime('2024-01-15T14:00:00'),
    ended_at: null,
    total_distance: 32.1,
    total_time: null
});
CREATE (t3:Trip {
    id: 'trip_003',
    started_at: datetime('2024-01-16T09:15:00'),
    ended_at: datetime('2024-01-16T11:45:00'),
    total_distance: 28.7,
    total_time: 150
});
CREATE (del1:Delivery {
    id: 'delivery_001',
    delivered_at: datetime('2024-01-15T10:30:00')
});
CREATE (del2:Delivery {
    id: 'delivery_002',
    delivered_at: datetime('2024-01-15T12:15:00')
});
CREATE (del3:Delivery {
    id: 'delivery_003',
    delivered_at: null
});
CREATE (del4:Delivery {
    id: 'delivery_004',
    delivered_at: datetime('2024-01-16T10:45:00')
});

MATCH (d:User:Driver {id: 'driver_001'}), (t:Trip {id: 'trip_001'})
CREATE (d)-[:EXECUTED]->(t);
MATCH (d:User:Driver {id: 'driver_002'}), (t:Trip {id: 'trip_002'})
CREATE (d)-[:EXECUTED]->(t);
MATCH (d:User:Driver {id: 'driver_001'}), (t:Trip {id: 'trip_003'})
CREATE (d)-[:EXECUTED]->(t);
MATCH (t:Trip {id: 'trip_001'}), (del:Delivery {id: 'delivery_001'})
CREATE (t)-[:CONTAINS]->(del);
MATCH (t:Trip {id: 'trip_001'}), (del:Delivery {id: 'delivery_002'})
CREATE (t)-[:CONTAINS]->(del);
MATCH (t:Trip {id: 'trip_002'}), (del:Delivery {id: 'delivery_003'})
CREATE (t)-[:CONTAINS]->(del);
MATCH (t:Trip {id: 'trip_003'}), (del:Delivery {id: 'delivery_004'})
CREATE (t)-[:CONTAINS]->(del);
MATCH (d:User:Driver {id: 'driver_001'}), (del:Delivery {id: 'delivery_001'})
CREATE (d)-[:DELIVERS]->(del);
MATCH (d:User:Driver {id: 'driver_001'}), (del:Delivery {id: 'delivery_002'})
CREATE (d)-[:DELIVERS]->(del);
MATCH (d:User:Driver {id: 'driver_002'}), (del:Delivery {id: 'delivery_003'})
CREATE (d)-[:DELIVERS]->(del);
MATCH (d:User:Driver {id: 'driver_001'}), (del:Delivery {id: 'delivery_004'})
CREATE (d)-[:DELIVERS]->(del);
MATCH (del:Delivery {id: 'delivery_001'}), (p:Point {id: '286994676'})
CREATE (del)-[:TO]->(p);
MATCH (a:User:Admin {id: 'admin_001'}), (p:Point {id: '286994676'})
CREATE (a)-[:OWNS]->(p);


CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT trip_id_unique IF NOT EXISTS FOR (t:Trip) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT delivery_id_unique IF NOT EXISTS FOR (d:Delivery) REQUIRE d.id IS UNIQUE;


CREATE INDEX point_id_index IF NOT EXISTS FOR (p:Point) ON (p.id);
CREATE INDEX point_coordinates_index IF NOT EXISTS FOR (p:Point) ON (p.lat, p.lon);
CREATE INDEX point_tipo_index IF NOT EXISTS FOR (p:Point) ON (p.tipo);
CREATE INDEX street_weight_index IF NOT EXISTS FOR ()-[s:STREET]-() ON (s.weight);
CREATE INDEX street_length_index IF NOT EXISTS FOR ()-[s:STREET]-() ON (s.length);
CREATE INDEX street_maxspeed_index IF NOT EXISTS FOR ()-[s:STREET]-() ON (s.maxspeed);
CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id);
CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email);
CREATE INDEX driver_available_index IF NOT EXISTS FOR (d:Driver) ON (d.available);
CREATE INDEX admin_role_index IF NOT EXISTS FOR (a:Admin) ON (a.role);
CREATE INDEX trip_id_index IF NOT EXISTS FOR (t:Trip) ON (t.id);
CREATE INDEX trip_dates_index IF NOT EXISTS FOR (t:Trip) ON (t.started_at);
CREATE INDEX trip_ended_index IF NOT EXISTS FOR (t:Trip) ON (t.ended_at);
CREATE INDEX delivery_id_index IF NOT EXISTS FOR (d:Delivery) ON (d.id);
CREATE INDEX delivery_delivered_index IF NOT EXISTS FOR (d:Delivery) ON (d.delivered_at);

CREATE (v1:Vehicle {
    id: 'vehicle_001',
    plate: 'ABC-123',
    type: 'van',
    capacity: 1000,
    available: true
});
CREATE (v2:Vehicle {
    id: 'vehicle_002',
    plate: 'DEF-456',
    type: 'truck',
    capacity: 2500,
    available: true
});
CREATE (v3:Vehicle {
    id: 'vehicle_003',
    plate: 'GHI-789',
    type: 'motorcycle',
    capacity: 50,
    available: false
});

MATCH (t:Trip {id: 'trip_001'}), (v:Vehicle {id: 'vehicle_001'})
CREATE (t)-[:USE]->(v);
MATCH (t:Trip {id: 'trip_002'}), (v:Vehicle {id: 'vehicle_002'})
CREATE (t)-[:USE]->(v);
MATCH (t:Trip {id: 'trip_003'}), (v:Vehicle {id: 'vehicle_003'})
CREATE (t)-[:USE]->(v);

MATCH (del:Delivery {id: 'delivery_001'}), (p:Point {id: '286994676'})
CREATE (del)-[:FROM]->(p);
MATCH (del:Delivery {id: 'delivery_002'}), (p:Point {id: '286994676'})
CREATE (del)-[:FROM]->(p);
MATCH (del:Delivery {id: 'delivery_003'}), (p:Point {id: '286994676'})
CREATE (del)-[:FROM]->(p);
MATCH (del:Delivery {id: 'delivery_004'}), (p:Point {id: '286994676'})
CREATE (del)-[:FROM]->(p);

CREATE CONSTRAINT vehicle_id_unique IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT vehicle_plate_unique IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.plate IS UNIQUE;
CREATE INDEX vehicle_id_index IF NOT EXISTS FOR (v:Vehicle) ON (v.id);
CREATE INDEX vehicle_plate_index IF NOT EXISTS FOR (v:Vehicle) ON (v.plate);
CREATE INDEX vehicle_available_index IF NOT EXISTS FOR (v:Vehicle) ON (v.available);
CREATE INDEX vehicle_type_index IF NOT EXISTS FOR (v:Vehicle) ON (v.type);
