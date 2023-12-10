DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS user;

CREATE TABLE restaurants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  rating NULL,
  min_order_amount DECIMAL(10, 2)
);

CREATE TABLE restaurant_photos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  restaurant_id INTEGER,
  photo_path TEXT,
  FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);