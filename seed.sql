-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Drop tables if they exist to ensure clean state
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS billers;
DROP TABLE IF EXISTS accounts;
-- Create Accounts Table
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) NOT NULL DEFAULT 'PKR',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create Contacts Table
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES accounts(id),
    name VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    bank VARCHAR(100) DEFAULT 'Procom Bank',
    account_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create Transactions Table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES accounts(id),
    amount DECIMAL(15, 2) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    category VARCHAR(50) NOT NULL,
    -- TRANSFER, BILL_PAY, FOOD, SHOPPING, SALARY, etc.
    description TEXT,
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create Cards Table
CREATE TABLE cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES accounts(id),
    pan VARCHAR(19) NOT NULL,
    -- Storing full PAN for demo simplicity
    is_virtual BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    -- ACTIVE, FROZEN
    daily_limit DECIMAL(15, 2) DEFAULT 50000.00,
    expiry VARCHAR(5) DEFAULT '12/28',
    cvv VARCHAR(3) DEFAULT '123',
    pin VARCHAR(4) DEFAULT '1234',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create Billers Table
CREATE TABLE billers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES accounts(id),
    provider_slug VARCHAR(50) NOT NULL,
    -- k_electric, sui_gas, etc.
    consumer_number VARCHAR(50) NOT NULL,
    nickname VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Programs to Seed Data
-- Create a main user account
DO $$
DECLARE main_user_id UUID;
BEGIN
INSERT INTO accounts (id, balance, currency, status)
VALUES (
        '59031ae8-8e9c-4700-8e43-ae090dcc1cb5',
        150000.00,
        'PKR',
        'ACTIVE'
    ) -- Hardcoded ID for consistency
RETURNING id INTO main_user_id;
-- Contacts
INSERT INTO contacts (user_id, name, nickname, bank, account_number)
VALUES (
        main_user_id,
        'Ali Khan',
        'Sigma',
        'Procom Bank',
        'PK99HBL00098765432'
    ),
    (
        main_user_id,
        'Sara Ahmed',
        'Sis',
        'Meezan Bank',
        'PK88MEZN00012345678'
    ),
    (
        main_user_id,
        'John Doe',
        'Boss',
        'HBL',
        'PK77HBL00055555555'
    );
-- Cards
INSERT INTO cards (
        user_id,
        pan,
        is_virtual,
        status,
        daily_limit,
        expiry,
        cvv,
        pin
    )
VALUES (
        main_user_id,
        '4000123456789010',
        FALSE,
        'ACTIVE',
        100000.00,
        '12/29',
        '456',
        '1122'
    ),
    -- Physical Visa
    (
        main_user_id,
        '5000987654321098',
        TRUE,
        'ACTIVE',
        25000.00,
        '06/28',
        '789',
        '3344'
    ),
    -- Virtual Mastercard
    (
        main_user_id,
        '4000555566667777',
        FALSE,
        'FROZEN',
        50000.00,
        '01/27',
        '111',
        '5566'
    );
-- Frozen Physical
-- Billers
INSERT INTO billers (
        user_id,
        provider_slug,
        consumer_number,
        nickname
    )
VALUES (
        main_user_id,
        'k_electric',
        '0400012345678',
        'Home Electricity'
    ),
    (
        main_user_id,
        'sui_gas',
        '1234567890',
        'Home Gas'
    ),
    (
        main_user_id,
        'ptcl',
        '02135551234',
        'Home Internet'
    );
-- Transactions (Past Month)
INSERT INTO transactions (
        user_id,
        amount,
        type,
        category,
        description,
        date
    )
VALUES (
        main_user_id,
        250000.00,
        'CREDIT',
        'SALARY',
        'Monthly Salary',
        NOW() - INTERVAL '1 month'
    ),
    (
        main_user_id,
        5000.00,
        'DEBIT',
        'FOOD',
        'KFC Dinner',
        NOW() - INTERVAL '28 days'
    ),
    (
        main_user_id,
        12000.00,
        'DEBIT',
        'BILL_PAY',
        'K-Electric Bill Payment',
        NOW() - INTERVAL '25 days'
    ),
    (
        main_user_id,
        3000.00,
        'DEBIT',
        'TRANSPORT',
        'Uber Ride',
        NOW() - INTERVAL '24 days'
    ),
    (
        main_user_id,
        15000.00,
        'DEBIT',
        'SHOPPING',
        'Grocery Shopping at Carrefour',
        NOW() - INTERVAL '20 days'
    ),
    (
        main_user_id,
        500.00,
        'DEBIT',
        'FOOD',
        'Coffee',
        NOW() - INTERVAL '18 days'
    ),
    (
        main_user_id,
        2000.00,
        'DEBIT',
        'ENTERTAINMENT',
        'Netflix Subscription',
        NOW() - INTERVAL '15 days'
    ),
    (
        main_user_id,
        10000.00,
        'DEBIT',
        'TRANSFER',
        'Transfer to Ali Khan',
        NOW() - INTERVAL '10 days'
    ),
    (
        main_user_id,
        4500.00,
        'DEBIT',
        'FOOD',
        'Pizza Hut',
        NOW() - INTERVAL '5 days'
    ),
    (
        main_user_id,
        8000.00,
        'DEBIT',
        'SHOPPING',
        'Daraz Order',
        NOW() - INTERVAL '2 days'
    ),
    (
        main_user_id,
        1000.00,
        'DEBIT',
        'TRANSPORT',
        'Careem Ride',
        NOW() - INTERVAL '1 day'
    );
END $$;