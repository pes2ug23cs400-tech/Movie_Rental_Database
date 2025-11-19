CREATE DATABASE movie_rental_db;
USE movie_rental_db;

-- Customers table from your ERD
CREATE TABLE Customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    address TEXT,
    membership_tier_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (membership_tier_id) REFERENCES Membership_Tiers(id) 
);
ALTER TABLE customers
ADD COLUMN phone VARCHAR(50) AFTER email;
ALTER TABLE customers
ADD COLUMN rental_limit INT AFTER membership_tier_id;

UPDATE customers
SET membership_tier_id = 2
WHERE id = 1;

UPDATE customers
SET membership_tier_id = 3
WHERE id = 2;

UPDATE customers
SET membership_tier_id = 1
WHERE id = 3;

alter table customers add column  age int after phone;
SELECT * FROM customers;

ALTER TABLE Customers
DROP COLUMN membership_tier_id; 

ALTER TABLE Customers
ADD COLUMN membership_tier_id INT;


ALTER TABLE Customers
ADD CONSTRAINT fk_membership
FOREIGN KEY (membership_tier_id) 
REFERENCES Membership_Tiers(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

ALTER TABLE Customers
DROP FOREIGN KEY fk_membership;



CREATE VIEW Customer_Rentals AS
SELECT 
    c.id AS customer_id,
    c.first_name,
    c.last_name,
    r.id AS rental_id,
    r.rental_date,
    r.due_date,
    r.return_date,
    r.late_fee
FROM Customers c
LEFT JOIN Rentals r
ON c.id = r.customer_id;

select * from Customer_Rentals;


SELECT 
    c.id AS customer_id,
    c.first_name,
    c.last_name,
    COUNT(r.id) AS total_rentals
FROM Customers c
JOIN Rentals r
    ON c.id = r.customer_id
WHERE r.rental_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY c.id, c.first_name, c.last_name
HAVING COUNT(r.id) > 2;




ALTER TABLE customers
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
-- Movies table from your ERD
CREATE TABLE Movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    genre_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   
);
alter table customers add column age int after phone;
ALTER TABLE customers
DROP COLUMN age;

select * from customers;
desc Movies;
select * from Movies;
ALTER TABLE movies
ADD COLUMN release_year INT AFTER description;
ALTER TABLE movies
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
ALTER TABLE movies
ADD COLUMN format_id INT,
ADD FOREIGN KEY (format_id) REFERENCES formats(id);

-- Step 1: Delete rental items linked to that movie
DELETE FROM rental_items
WHERE inventory_id IN (SELECT id FROM inventory WHERE movie_id = 1);

-- Step 2: Delete inventory linked to that movie
DELETE FROM inventory WHERE movie_id = 1;
select * from inventory;
INSERT INTO inventory (available_copies, total_copies, movie_id)
VALUES (5, 5, 3);


-- Step 3: Finally, delete the movie
DELETE FROM movies WHERE id = 4;

INSERT INTO movies (title, description, release_year, genre_id, format_id)
VALUES ('Inception', 'Mind-bending thriller', 2010, 4, 1);




-- Rental_Terms table from your ERD (Renamed to Rentals for simplicity)
CREATE TABLE Rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rental_date DATETIME NOT NULL,
    return_date DATETIME,
    due_date DATETIME NOT NULL,
    customer_id INT NOT NULL,
    staff_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
--  FOREIGN KEY (staff_id) REFERENCES staff(id) 
);

ALTER TABLE rentals
ADD COLUMN late_fee DECIMAL(5, 2) DEFAULT 0.00 AFTER due_date;
SELECT * FROM inventory WHERE id = 2;

-- Independent tables (no foreign keys to other tables in this list)
-- =================================================================

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);
INSERT INTO roles (name, description) VALUES
('Manager', 'Has full administrative access and can manage staff.'),
('Staff', 'Regular employee who handles rentals and customer service.');

CREATE TABLE genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

INSERT INTO genres (name, description) VALUES
('Action', 'High-octane, stunt-driven films.'),
('Comedy', 'Light-hearted films designed to make you laugh.'),
('Drama', 'Serious, plot-driven narratives.'),
('Sci-Fi', 'Futuristic concepts, science, and technology.'),
('Horror', 'Films designed to frighten and scare.');

CREATE TABLE formats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);
INSERT INTO formats (name, description) VALUES
('Blu-ray', 'High-definition physical disc format.'),
('DVD', 'Standard-definition physical disc format.'),
('Digital', 'Digital streaming or download access.');


CREATE TABLE membership_tiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rental_limit INT,
    rental_period_days INT,
    price DECIMAL(10, 2) NOT NULL
);
INSERT INTO membership_tiers (name, description, rental_limit, rental_period_days, price) VALUES
('Basic', 'Access to our standard library.', 3, 7, 9.99),
('Premium', 'Includes new releases and extended loan periods.', 5, 14, 19.99),
('Gold', 'Unlimited rentals and access to our entire catalog.', 10, 30, 29.99);
SELECT * FROM membership_tiers;

CREATE TABLE payment_gateways (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(100),
    api_key VARCHAR(255),
    active BOOLEAN DEFAULT TRUE
);

-- Dependent tables (with foreign keys)
-- =================================================================

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    available_copies INT NOT NULL DEFAULT 0,
    total_copies INT NOT NULL DEFAULT 0,
    last_inventory_change TIMESTAMP,
    movie_id INT,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

CREATE TABLE external_movie_db (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT,
    external_id VARCHAR(255),
    external_db_id VARCHAR(255),
    source VARCHAR(100),
    fetched_at TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT,
    customer_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    status VARCHAR(50),
    payment_gateway_id INT,
    FOREIGN KEY (rental_id) REFERENCES rentals(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (payment_gateway_id) REFERENCES payment_gateways(id)
);

CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    role_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

ALTER TABLE staff ADD COLUMN password_hash VARCHAR(128) NOT NULL;

CREATE TABLE inventory_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    changed_by_staff_id INT,
    change_type VARCHAR(50),
    change_amount INT,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    inventory_id INT,
    FOREIGN KEY (changed_by_staff_id) REFERENCES staff(id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(id)
);

CREATE TABLE movie_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    rating INT,
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    movie_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

CREATE TABLE rental_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT,
    inventory_id INT,
    rental_start TIMESTAMP,
    returned BOOLEAN DEFAULT FALSE,
    returned_at TIMESTAMP,
    late_fee DECIMAL(5, 2),
    FOREIGN KEY (rental_id) REFERENCES rentals(id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(id)
);
select * from rental_items;

-- inventory_update--trigger
DELIMITER //
CREATE TRIGGER trg_inventory_update
BEFORE UPDATE ON inventory
FOR EACH ROW
BEGIN
    SET NEW.last_inventory_change = NOW();
END //
DELIMITER ;
select * from inventory;
SHOW TRIGGERS;


select * from inventory;
UPDATE inventory
SET available_copies = available_copies + 5,
    total_copies = total_copies + 5
WHERE id = 3;


SELECT id, available_copies, last_inventory_change
FROM inventory
WHERE id = 3;









-- (a) Calculate late fee for a rental--function
DELIMITER //
CREATE FUNCTION fn_calculate_late_fee(rentalId INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE days_late INT;
    DECLARE fee DECIMAL(10,2);

    SELECT DATEDIFF(return_date, due_date)
      INTO days_late
      FROM rentals
     WHERE id = rentalId;

    IF days_late > 0 THEN
        SET fee = days_late * 10.00;  -- 10 /day
    ELSE
        SET fee = 0.00;
    END IF;

    RETURN fee;
END //
DELIMITER ;

SHOW FUNCTION STATUS WHERE Name = 'fn_calculate_late_fee';



SHOW FUNCTION STATUS WHERE Db = DATABASE();

-- Rental data insert for testing late fee
INSERT INTO rentals (rental_date, due_date, return_date)
VALUES 
('2025-10-15', '2025-10-20', '2025-10-22'),
('2025-10-17', '2025-10-25', '2025-10-24'),
('2025-10-18', '2025-10-18', '2025-10-18');
-- End of test data


SELECT fn_calculate_late_fee(1) AS 'Late Fee'; -- Expected 20.00
SELECT fn_calculate_late_fee(2) AS 'Late Fee'; -- Expected 0.00
SELECT fn_calculate_late_fee(3) AS 'Late Fee'; -- Expected 0.00


DESC rentals;









-- Rent a Movie-- 1.Rental creation  2.Rental item creation 3.Inventory update

DELIMITER //
CREATE PROCEDURE sp_return_movie(IN p_rental_item_id INT)
BEGIN
    DECLARE r_id INT;
    DECLARE fee DECIMAL(10,2);

    SELECT rental_id INTO r_id
    FROM rental_items
    WHERE id = p_rental_item_id;

    SET fee = fn_calculate_late_fee(r_id);

    -- Update rental item
    UPDATE rental_items
    SET returned = TRUE, returned_at = NOW(), late_fee = fee
    WHERE id = p_rental_item_id;

    -- Update main rental
    UPDATE rentals
    SET return_date = NOW(), late_fee = fee
    WHERE id = r_id;

    -- Restore stock
    UPDATE inventory
    SET available_copies = available_copies + 1
    WHERE id = (SELECT inventory_id FROM rental_items WHERE id = p_rental_item_id);
END //
DELIMITER ;
SHOW PROCEDURE STATUS WHERE Db = DATABASE();



CALL sp_rent_movie(1, 3, 1);

SELECT * FROM rentals;
SELECT * FROM rental_items;

SELECT id, name FROM membership_tiers;

# deleted duplicates unique constraint conflict in the membership_tiers table.

SET SQL_SAFE_UPDATES = 0;

DELETE FROM membership_tiers
WHERE name = 'Basic'
  AND id NOT IN (
    SELECT * FROM (
      SELECT MIN(id)
      FROM membership_tiers
      WHERE name = 'Basic'
    ) AS temp
  );

SET SQL_SAFE_UPDATES = 1;


ALTER TABLE customers MODIFY password_hash VARCHAR(255);

DESCRIBE customers;

ALTER TABLE customers ADD COLUMN password_hash VARCHAR(128);

DESC movies;
ALTER TABLE movies ADD COLUMN poster_url VARCHAR(255) NULL;


UPDATE movies 
SET poster_url = 'https://offscreen.com/images/articles/_resized/15_5_Inception1.jpg'
WHERE id = 3;

UPDATE movies 
SET poster_url = 'https://image.tmdb.org/t/p/original/deXPWnrz30bLpgijKilODqEgISg.jpg'
WHERE id = 2;


SELECT id, title, poster_url FROM movies;

ALTER TABLE payments CHANGE COLUMN payment_method method VARCHAR(50);

ALTER TABLE rentals 
MODIFY COLUMN due_date DATETIME NOT NULL;

DESCRIBE rentals;

USE movie_rental_db;

ALTER TABLE rentals 
MODIFY COLUMN due_date DATETIME NOT NULL;

-- Add a server-side default for the rental due_date
ALTER TABLE rentals
MODIFY COLUMN due_date DATETIME NOT NULL DEFAULT (NOW() + INTERVAL 7 DAY);
ALTER TABLE rentals MODIFY COLUMN due_date DATETIME NOT NULL;


-- This tells MySQL: if no due_date is provided, automatically set it to 7 days from now.
ALTER TABLE rentals
MODIFY COLUMN due_date DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL 7 DAY);
desc rentals;

SHOW TRIGGERS LIKE 'rentals';
SHOW TRIGGERS;
DROP TRIGGER IF EXISTS trg_set_due_date;

ALTER TABLE rental_items
ADD COLUMN movie_id INT AFTER rental_id,
ADD CONSTRAINT fk_rental_items_movie FOREIGN KEY (movie_id) REFERENCES movies(id);


select * from movies;
UPDATE movies 
SET poster_url = "https://images.hdqwalls.com/download/deadpool-and-wolverine-unforgettable-collaboration-cf-1080x1920.jpg"
WHERE id = 5;

UPDATE movies 
SET description="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O., but his tragic past may doom the project and his team to disaster."
WHERE id = 3;

INSERT INTO movies (title, release_year, description, poster_url, genre_id,format_id)
VALUES (
  'Sachin: A Billion Dreams',
  2017,
  'A biographical film based on the life of Indian cricketer Sachin Tendulkar, showcasing his journey from a young prodigy to a national icon.',
  'https://th.bing.com/th/id/OIP.rFPm6HPZXh-CQzXY_VtNUQHaEK?w=108&h=108&c=1&bgcl=12e45d&r=0&o=7&cb=ucfimgc1&dpr=1.5&pid=ImgRC&rm=3',
  6,3
);

ALTER TABLE movies
ADD COLUMN price DECIMAL(6,2) DEFAULT 99.00;

select * from movies;
UPDATE movies SET price = 120.00 WHERE id=2;
UPDATE movies SET price = 150.00 WHERE id=3;
UPDATE movies SET price = 180.00 WHERE id=5;
UPDATE movies SET price = 100.00 WHERE id=6;



select * from rentals;



SELECT id, rental_id, movie_id, returned, returned_at FROM rental_items;

UPDATE rental_items SET returned = 1 WHERE rental_id = 4;
UPDATE rentals SET return_date = NOW() WHERE id = 4;



SET SQL_SAFE_UPDATES = 0;

SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM rental_items;
DELETE FROM rentals;
DELETE FROM payments;
SET FOREIGN_KEY_CHECKS = 1;

SET SQL_SAFE_UPDATES = 1;

ALTER TABLE rentals AUTO_INCREMENT = 1;
ALTER TABLE rental_items AUTO_INCREMENT = 1;
ALTER TABLE payments AUTO_INCREMENT = 1;

UPDATE inventory SET available_copies = total_copies;


SELECT * FROM rentals;
SELECT * FROM rental_items;
SELECT * FROM payments;
select * from movies;

select * from genres;

select* from customers;


	