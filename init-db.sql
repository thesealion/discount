CREATE TABLE codes (
    brand VARCHAR(20),
    code VARCHAR(10),
    used BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(brand, code)
);
