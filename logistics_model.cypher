// === CREACIÓN DE ENTIDADES ===

// Drivers (User:Driver)
CREATE (d1:User:Driver {
    first_name: 'Juan',
    last_name: 'Pérez',
    email: 'juan.perez@logistics.com',
    password_hash: '$2b$12$example_hash_1',
    available: true,
    working_hours: 'morning'
});
CREATE (d2:User:Driver {
    first_name: 'María',
    last_name: 'García',
    email: 'maria.garcia@logistics.com',
    password_hash: '$2b$12$example_hash_2',
    available: true,
    working_hours: 'afternoon'
});
CREATE (d3:User:Driver {
    first_name: 'Carlos',
    last_name: 'López',
    email: 'carlos.lopez@logistics.com',
    password_hash: '$2b$12$example_hash_3',
    available: false,
    working_hours: 'night'
});

// Admins (User:Admin)
CREATE (a1:User:Admin {
    first_name: 'Ana',
    last_name: 'Rodríguez',
    email: 'ana.rodriguez@logistics.com',
    password_hash: '$2b$12$example_hash_admin_1',
    role: 'super_admin'
});
CREATE (a2:User:Admin {
    first_name: 'Roberto',
    last_name: 'Martín',
    email: 'roberto.martin@logistics.com',
    password_hash: '$2b$12$example_hash_admin_2',
    role: 'operations_manager'
});

// Vehicles
CREATE (v1:Vehicle {
    capacity_kg: 1000,
    volume_m3: 15.5,
    type: 'van',
    available: true
});
CREATE (v2:Vehicle {
    capacity_kg: 2500,
    volume_m3: 25.0,
    type: 'truck',
    available: true
});
CREATE (v3:Vehicle {
    capacity_kg: 50,
    volume_m3: 1.2,
    type: 'motorcycle',
    available: false
});

// Trips
CREATE (t1:Trip {
    date: datetime('2024-01-15T08:00:00'),
    started_at: datetime('2024-01-15T08:00:00'),
    ended_at: datetime('2024-01-15T12:30:00'),
    total_distance: 45.5,
    total_time: 270
});
CREATE (t2:Trip {
    date: datetime('2024-01-15T14:00:00'),
    started_at: datetime('2024-01-15T14:00:00'),
    ended_at: null,
    total_distance: 32.1,
    total_time: null
});
CREATE (t3:Trip {
    date: datetime('2024-01-16T09:15:00'),
    started_at: datetime('2024-01-16T09:15:00'),
    ended_at: datetime('2024-01-16T11:45:00'),
    total_distance: 28.7,
    total_time: 150
});

// Deliveries
CREATE (del1:Delivery {
    date: datetime('2024-01-15T10:30:00'),
    delivered: true,
    package_info: 'Documentos importantes',
    priority: 'high'
});
CREATE (del2:Delivery {
    date: datetime('2024-01-15T12:15:00'),
    delivered: true,
    package_info: 'Equipos electrónicos',
    priority: 'medium'
});
CREATE (del3:Delivery {
    date: datetime('2024-01-15T16:00:00'),
    delivered: false,
    package_info: 'Medicamentos',
    priority: 'urgent'
});
CREATE (del4:Delivery {
    date: datetime('2024-01-16T10:45:00'),
    delivered: true,
    package_info: 'Ropa y accesorios',
    priority: 'low'
});

// Points (asumiendo que ya existen algunos points del mapa)
CREATE (p1:Point {
    lat: -34.6037,
    lon: -58.3816,
    numeracion: '1234',
    name: 'Local Centro',
    tipo: 'Local'
});
CREATE (p2:Point {
    lat: -34.6118,
    lon: -58.3960,
    numeracion: '5678',
    name: 'Centro de Distribución Norte',
    tipo: 'CentroDeDistribucion'
});
CREATE (p3:Point {
    lat: -34.5900,
    lon: -58.3700,
    numeracion: '9012',
    name: 'Local Palermo',
    tipo: 'Local'
});

// Clientes
CREATE (c1:Client {
    first_name: 'Pedro',
    last_name: 'González',
    email: 'pedro.gonzalez@email.com'
});
CREATE (c2:Client {
    first_name: 'Laura',
    last_name: 'Fernández',
    email: 'laura.fernandez@email.com'
});

// === CREACIÓN DE RELACIONES ===

// Driver EXECUTED Trip
CREATE (d1)-[:EXECUTED]->(t1);
CREATE (d2)-[:EXECUTED]->(t2);
CREATE (d1)-[:EXECUTED]->(t3);

// Trip USES Vehicle
CREATE (t1)-[:USES]->(v1);
CREATE (t2)-[:USES]->(v2);
CREATE (t3)-[:USES]->(v3);

// Trip CONTAINS Delivery
CREATE (t1)-[:CONTAINS]->(del1);
CREATE (t1)-[:CONTAINS]->(del2);
CREATE (t2)-[:CONTAINS]->(del3);
CREATE (t3)-[:CONTAINS]->(del4);

// Delivery TO Point (con distance)
CREATE (del1)-[:TO {distance: 12.5}]->(p1);
CREATE (del2)-[:TO {distance: 8.3}]->(p2);
CREATE (del3)-[:TO {distance: 15.7}]->(p1);
CREATE (del4)-[:TO {distance: 6.2}]->(p3);

// Cliente HAS Point
CREATE (c1)-[:HAS]->(p1);
CREATE (c2)-[:HAS]->(p2);

// Admin OWNS Point (con created_at)
CREATE (a1)-[:OWNS {created_at: datetime('2024-01-01T00:00:00')}]->(p1);
CREATE (a1)-[:OWNS {created_at: datetime('2024-01-01T00:00:00')}]->(p2);
CREATE (a2)-[:OWNS {created_at: datetime('2024-01-02T00:00:00')}]->(p3);

// Point STREET Point (con propiedades)
CREATE (p1)-[:STREET {distance: 2.5, name: 'Av. Corrientes', length: 2500, maxspeed: 60, weight: 1.0}]->(p3);
CREATE (p3)-[:STREET {distance: 1.8, name: 'Av. Santa Fe', length: 1800, maxspeed: 50, weight: 1.2}]->(p2);
CREATE (p2)-[:STREET {distance: 3.2, name: 'Av. Cabildo', length: 3200, maxspeed: 70, weight: 0.8}]->(p1);

// === CONSTRAINTS ===

CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT cliente_email_unique IF NOT EXISTS FOR (c:Cliente) REQUIRE c.email IS UNIQUE;

// === ÍNDICES ===

// Índices para Point (asumiendo que ya existen del mapa)
CREATE INDEX point_coordinates_index IF NOT EXISTS FOR (p:Point) ON (p.lat, p.lon);
CREATE INDEX point_tipo_index IF NOT EXISTS FOR (p:Point) ON (p.tipo);
CREATE INDEX point_name_index IF NOT EXISTS FOR (p:Point) ON (p.name);

// Índices para relaciones STREET (asumiendo que ya existen del mapa)
CREATE INDEX street_weight_index IF NOT EXISTS FOR ()-[s:STREET]-() ON (s.weight);
CREATE INDEX street_length_index IF NOT EXISTS FOR ()-[s:STREET]-() ON (s.length);
CREATE INDEX street_maxspeed_index IF NOT EXISTS FOR ()-[s:STREET]-() ON (s.maxspeed);

// Índices para User
CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email);
CREATE INDEX driver_available_index IF NOT EXISTS FOR (d:Driver) ON (d.available);
CREATE INDEX admin_role_index IF NOT EXISTS FOR (a:Admin) ON (a.role);

// Índices para Trip
CREATE INDEX trip_date_index IF NOT EXISTS FOR (t:Trip) ON (t.date);
CREATE INDEX trip_started_index IF NOT EXISTS FOR (t:Trip) ON (t.started_at);
CREATE INDEX trip_ended_index IF NOT EXISTS FOR (t:Trip) ON (t.ended_at);

// Índices para Delivery
CREATE INDEX delivery_date_index IF NOT EXISTS FOR (d:Delivery) ON (d.date);
CREATE INDEX delivery_delivered_index IF NOT EXISTS FOR (d:Delivery) ON (d.delivered);
CREATE INDEX delivery_priority_index IF NOT EXISTS FOR (d:Delivery) ON (d.priority);

// Índices para Vehicle
CREATE INDEX vehicle_available_index IF NOT EXISTS FOR (v:Vehicle) ON (v.available);
CREATE INDEX vehicle_type_index IF NOT EXISTS FOR (v:Vehicle) ON (v.type);

// Índices para Cliente
CREATE INDEX cliente_email_index IF NOT EXISTS FOR (c:Cliente) ON (c.email);
