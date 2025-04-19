
CREATE DATABASE IF NOT EXISTS car_workshop;
USE car_workshop;
CREATE TABLE mechanic (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL);
CREATE TABLE client (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, address TEXT NOT NULL, phone VARCHAR(15) NOT NULL, car_license VARCHAR(20) NOT NULL, car_engine VARCHAR(20) NOT NULL);
CREATE TABLE appointment (id INT AUTO_INCREMENT PRIMARY KEY, client_id INT NOT NULL, mechanic_id INT NOT NULL, appointment_date DATE NOT NULL, FOREIGN KEY (client_id) REFERENCES client(id), FOREIGN KEY (mechanic_id) REFERENCES mechanic(id));
INSERT INTO mechanic (name) VALUES ('Doraemon'), ('Nobita'), ('Suniyo'), ('Suzuka'), ('Gian');
