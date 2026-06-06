# Enriched Test Cases

## TC-001 - Successful sign-in with valid credentials
- **Module:** Login
- **Direct Link:** http://localhost:8080/login
- **Requires Auth:** False

### Steps
1. Enter 'admin@parabank.com' in Email/Username field
2. Enter 'Admin123!@#' in Password field
3. Click Sign In

### Test Data
```json
{
  "email": "admin@parabank.com",
  "password": "Admin123!@#"
}
```

## TC-008 - Authentication failure with unregistered credentials
- **Module:** Login
- **Direct Link:** http://localhost:8080/login
- **Requires Auth:** False

### Steps
1. Enter 'unregistered@example.com' in Email/Username
2. Enter 'Password1!' in Password
3. Click Sign In

### Test Data
```json
{
  "email": "unregistered@example.com",
  "password": "Password1!"
}
```

## TC-009 - Password at exact minimum length (8 chars) succeeds
- **Module:** Login
- **Direct Link:** http://localhost:8080/login
- **Requires Auth:** False

### Steps
1. Enter 'admin@parabank.com' in Email/Username
2. Enter 'Admin123!@#' in Password
3. Click Sign In

### Test Data
```json
{
  "email": "admin@parabank.com",
  "password": "Admin123!@#"
}
```

## TC-014 - Failed login clears Password but preserves Email/Username
- **Module:** Login
- **Direct Link:** http://localhost:8080/login
- **Requires Auth:** False

### Steps
1. Enter 'admin@parabank.com' in Email/Username
2. Enter 'WrongPass1!' in Password
3. Click Sign In

### Test Data
```json
{
  "email": "admin@parabank.com",
  "password": "WrongPass1!"
}
```

## TC-001 - Complete registration happy path
- **Module:** Register
- **Direct Link:** http://localhost:8080/register
- **Requires Auth:** False

### Steps
1. Enter 'John' in First Name field
2. Enter 'Doe' in Last Name field
3. Enter '123 Main Street' in Street Address field
4. Enter 'Springfield' in City field
5. Select 'IL' from State dropdown
6. Enter '62701' in ZIP Code field
7. Enter '(555) 123-4567' in Phone Number field
8. Enter '***-**-1234' in SSN field
9. Enter 'admin@parabank.com' in Username/Email field
10. Enter 'Admin123!@#' in Password field
11. Enter 'Admin123!@#' in Confirm Password field
12. Click Register

### Test Data
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "street_address": "123 Main Street",
  "city": "Springfield",
  "state": "IL",
  "zip": "62701",
  "phone": "(555) 123-4567",
  "ssn": "***-**-1234",
  "username": "admin@parabank.com",
  "password": "Admin123!@#"
}
```

## TC-006 - Submit with ALL required fields empty
- **Module:** Register
- **Direct Link:** http://localhost:8080/register
- **Requires Auth:** False

### Steps
1. Leave all fields blank
2. Click Register

### Test Data
```json
{}
```

## TC-010 - Confirm Password does not match Password
- **Module:** Register
- **Direct Link:** http://localhost:8080/register
- **Requires Auth:** False

### Steps
1. Enter 'Admin123!@#' in Password field
2. Enter 'Admin123!@#X' in Confirm Password field (a different value)
3. Enter 'John' in First Name field
4. Enter 'Doe' in Last Name field
5. Enter '123 Main Street' in Street Address field
6. Enter 'Springfield' in City field
7. Select 'IL' from State dropdown
8. Enter '62701' in ZIP Code field
9. Enter '(555) 123-4567' in Phone Number field
10. Enter '***-**-1234' in SSN field
11. Enter 'admin@parabank.com' in Username/Email field
12. Click Register

### Test Data
```json
{
  "password": "Admin123!@#",
  "confirm_password": "Admin123!@#X",
  "first_name": "John",
  "last_name": "Doe",
  "street_address": "123 Main Street",
  "city": "Springfield",
  "state": "IL",
  "zip": "62701",
  "phone": "(555) 123-4567",
  "ssn": "***-**-1234",
  "username": "admin@parabank.com"
}
```

## TC-017 - 10-digit phone auto-formats to (123) 456-7890 and registration succeeds
- **Module:** Register
- **Direct Link:** http://localhost:8080/register
- **Requires Auth:** False

### Steps
1. Enter 'John' in First Name field
2. Enter 'Doe' in Last Name field
3. Enter '123 Main Street' in Street Address field
4. Enter 'Springfield' in City field
5. Select 'IL' from State dropdown
6. Enter '62701' in ZIP Code field
7. Enter raw digits '5551234567' (no punctuation) in Phone Number field
8. Observe the Phone Number field updates to '(555) 123-4567'
9. Enter '***-**-1234' in SSN field
10. Enter 'admin@parabank.com' in Username/Email field
11. Enter 'Admin123!@#' in Password field
12. Enter 'Admin123!@#' in Confirm Password field
13. Click Register

### Test Data
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "street_address": "123 Main Street",
  "city": "Springfield",
  "state": "IL",
  "zip": "62701",
  "phone_raw": "5551234567",
  "phone_formatted": "(555) 123-4567",
  "ssn": "***-**-1234",
  "username": "admin@parabank.com",
  "password": "Admin123!@#"
}
```

## TC-003 - Account numbers are masked showing only last four digits
- **Module:** Accounts Overview
- **Direct Link:** http://localhost:8080/accounts-overview
- **Requires Auth:** True

### Steps
1. Navigate to Accounts Overview (http://localhost:8080/accounts-overview)
2. Inspect the Account Number column for each row

### Test Data
```json
{
  "last4": "5001",
  "masked_account": "****5001",
  "username": "admin",
  "password": "Admin123!@#"
}
```

## TC-008 - Unauthenticated access to Accounts Overview redirects to Login
- **Module:** Accounts Overview
- **Direct Link:** http://localhost:8080/accounts-overview
- **Requires Auth:** False

### Steps
1. If currently signed in, click 'Sign Out' to log out
2. Navigate directly to the Accounts Overview URL: http://localhost:8080/accounts-overview
3. Observe whether the user is redirected to the Login page (http://localhost:8080/login) and confirm the Accounts Table and Welcome message are not visible

### Test Data
```json
{
  "accounts_url": "http://localhost:8080/accounts-overview",
  "login_url": "http://localhost:8080/login",
  "username": "admin"
}
```

## TC-012 - Zero and negative Current Balance values displayed and summed correctly
- **Module:** Accounts Overview
- **Direct Link:** http://localhost:8080/accounts-overview
- **Requires Auth:** True

### Steps
1. Navigate to Accounts Overview
2. Locate rows with zero and negative balances
3. Observe each row's display and the Total Balance footer

### Test Data
```json
{}
```

## TC-001 - Open a Checking account at minimum deposit
- **Module:** Open New Account
- **Direct Link:** http://localhost:8080/open-new-account
- **Requires Auth:** True

### Steps
1. Navigate to http://localhost:8080/open-new-account (Open New Account page)
2. Select 'Checking' as Account Type
3. Enter '25' in Initial Deposit Amount
4. Select funding account '****5001 (Checking, $5,847.52)' from the Funding Source dropdown
5. Click 'Open Account'

### Test Data
```json
{
  "account_type": "Checking",
  "initial_deposit": "25",
  "funding_account": "****5001 (Checking)",
  "funding_account_balance": "5847.52",
  "user_email": "admin@parabank.com",
  "username": "admin"
}
```

## TC-011 - Funding account has insufficient balance for requested deposit
- **Module:** Open New Account
- **Direct Link:** http://localhost:8080/open-new-account
- **Requires Auth:** True

### Steps
1. Select 'Checking' as Account Type
2. Enter '6000' in Initial Deposit Amount (amount exceeding the selected funding account balance)
3. Select the under-funded account '****5001 (Checking, $5,847.52)' from the Funding Source dropdown
4. Click 'Open Account'

### Test Data
```json
{
  "account_type": "Checking",
  "initial_deposit": "6000",
  "funding_account": "****5001 (Checking)",
  "funding_account_balance": "5847.52",
  "user_email": "admin@parabank.com",
  "username": "admin"
}
```

## TC-016 - Funding account balance exactly equals deposit amount — boundary succeeds
- **Module:** Open New Account
- **Direct Link:** http://localhost:8080/open-new-account
- **Requires Auth:** True

### Steps
1. Select 'Checking' as Account Type (meets Checking minimum of $25)
2. Enter '5847.52' in Initial Deposit Amount (X)
3. Select the funding account '****5001 (Checking, $5,847.52)' which has balance = 5847.52
4. Click 'Open Account'

### Test Data
```json
{
  "account_type": "Checking",
  "initial_deposit": "5847.52",
  "funding_account": "****5001 (Checking)",
  "funding_account_balance": "5847.52",
  "user_email": "admin@parabank.com",
  "username": "admin"
}
```

## TC-018 - Switching Account Type invalidates a previously valid deposit amount
- **Module:** Open New Account
- **Direct Link:** http://localhost:8080/open-new-account
- **Requires Auth:** True

### Steps
1. Select 'Checking' as Account Type
2. Enter '25' in Initial Deposit Amount (Checking minimum)
3. Select a valid funding account '****5001 (Checking, $5,847.52)'
4. Change Account Type to 'Savings' without altering the Initial Deposit Amount

### Test Data
```json
{
  "account_type_initial": "Checking",
  "account_type_after": "Savings",
  "initial_deposit": "25",
  "funding_account": "****5001 (Checking)",
  "funding_account_balance": "5847.52",
  "user_email": "admin@parabank.com",
  "username": "admin"
}
```

## TC-002 - External transfer with matching account numbers succeeds
- **Module:** Transfer Funds
- **Direct Link:** http://localhost:8080/transfer-funds
- **Requires Auth:** True

### Steps
1. Navigate to Transfer Funds page
2. Select the 'External Account' radio option
3. Enter '500.00' in the Amount field
4. Select '****5001 (Checking, $5,847.52)' as the Source Account
5. Enter 'ELC123456789' in External Account Number and 'ELC123456789' in Confirm External Account Number
6. Click 'Transfer'

### Test Data
```json
{
  "amount": "500.00",
  "source_account": "****5001 (Checking, $5,847.52)",
  "external_account_number": "ELC123456789"
}
```

## TC-009 - Transfer amount exceeds available balance
- **Module:** Transfer Funds
- **Direct Link:** http://localhost:8080/transfer-funds
- **Requires Auth:** True

### Steps
1. Select 'My ParaBank Account' option
2. Enter '10000.00' in the Amount field (exceeding the source account balance)
3. Select '****5001 (Checking, $5,847.52)' as the Source Account
4. Select '****5002 (Savings, $25,678.90)' as the Destination Account
5. Click 'Transfer'

### Test Data
```json
{
  "amount": "10000.00",
  "source_account": "****5001 (Checking, $5,847.52)",
  "destination_account": "****5002 (Savings, $25,678.90)"
}
```

## TC-011 - External account number and confirmation do not match
- **Module:** Transfer Funds
- **Direct Link:** http://localhost:8080/transfer-funds
- **Requires Auth:** True

### Steps
1. Select the 'External Account' radio option
2. Enter '1500.00' in the Amount field and select '****5001 (Checking, $5,847.52)' as the Source Account
3. Enter 'GAS987654321' in External Account Number
4. Enter 'INT555444333' in Confirm External Account Number
5. Click 'Transfer'

### Test Data
```json
{
  "amount": "1500.00",
  "source_account": "****5001 (Checking, $5,847.52)",
  "external_account_number_A": "GAS987654321",
  "external_account_number_B": "INT555444333"
}
```

## TC-012 - Transfer amount exactly equals available balance succeeds
- **Module:** Transfer Funds
- **Direct Link:** http://localhost:8080/transfer-funds
- **Requires Auth:** True

### Steps
1. Select 'My ParaBank Account' option
2. Select '****5001 (Checking, $5,847.52)' as the Source Account
3. Select '****5002 (Savings, $25,678.90)' as the Destination Account
4. Enter '5847.52' in the Amount field (the exact available balance)
5. Click 'Transfer'

### Test Data
```json
{
  "amount": "5847.52",
  "source_account": "****5001 (Checking, $5,847.52)",
  "destination_account": "****5002 (Savings, $25,678.90)"
}
```

## TC-018 - Browser Back after successful transfer does not create a duplicate
- **Module:** Transfer Funds
- **Direct Link:** http://localhost:8080/transfer-funds
- **Requires Auth:** True

### Steps
1. Complete a successful transfer of '2500.00' from '****5001 (Checking, $5,847.52)' to '****5002 (Savings, $25,678.90)'; note the transaction ID displayed
2. Press the browser Back button
3. Click 'Transfer' again without changing any inputs

### Test Data
```json
{
  "amount": "2500.00",
  "source_account": "****5001 (Checking, $5,847.52)",
  "destination_account": "****5002 (Savings, $25,678.90)"
}
```

## TC-001 - Submit bill payment happy path
- **Module:** Payments
- **Direct Link:** http://localhost:8080/bill-pay
- **Requires Auth:** True

### Steps
1. Navigate to Bill Payment (http://localhost:8080/bill-pay).
2. Fill in Payee Name with 'Electric Company'.
3. Fill in Street Address with '456 Power Street'.
4. Fill in City with 'Springfield'.
5. Fill in State with 'IL'.
6. Fill in ZIP with '62701'.
7. Fill in Phone with '(555) 987-6543'.
8. Enter payee account number 'ELC123456789' in Payee Account Number.
9. Enter 'ELC123456789' in Confirm Account Number.
10. Enter Payment Amount '200.00'.
11. Select source account '****5001 (Checking, $5,847.52)'.
12. Click Pay.

### Test Data
```json
{
  "payee_name": "Electric Company",
  "payee_street": "456 Power Street",
  "payee_city": "Springfield",
  "payee_state": "IL",
  "payee_zip": "62701",
  "payee_phone": "(555) 987-6543",
  "payee_account": "ELC123456789",
  "payment_amount": "200.00",
  "source_account": "****5001 (Checking, $5,847.52)"
}
```

## TC-008 - Payee account number and confirmation do not match
- **Module:** Payments
- **Direct Link:** http://localhost:8080/bill-pay
- **Requires Auth:** True

### Steps
1. Enter 'ELC123456789' in Payee Account Number.
2. Enter 'GAS987654321' in Confirm Account Number.
3. Click Pay.

### Test Data
```json
{
  "account_number_A": "ELC123456789",
  "account_number_B": "GAS987654321"
}
```

## TC-009 - Insufficient funds in selected source account
- **Module:** Payments
- **Direct Link:** http://localhost:8080/bill-pay
- **Requires Auth:** True

### Steps
1. Select the under-funded source account '****5003 (Credit Card, -$1,534.67)'.
2. Enter a payment amount '100.00' (greater than the account's available balance).
3. Click Pay.

### Test Data
```json
{
  "source_account": "****5003 (Credit Card, -$1,534.67)",
  "payment_amount": "100.00"
}
```

## TC-012 - Payment amount exactly equals available funds succeeds
- **Module:** Payments
- **Direct Link:** http://localhost:8080/bill-pay
- **Requires Auth:** True

### Steps
1. Enter Payment Amount '5847.52'.
2. Select source account '****5001 (Checking, $5,847.52)'.
3. Click Pay.

### Test Data
```json
{
  "payment_amount": "5847.52",
  "source_account": "****5001 (Checking, $5,847.52)"
}
```

## TC-016 - Browser Back after successful payment does not create duplicate
- **Module:** Payments
- **Direct Link:** http://localhost:8080/bill-pay
- **Requires Auth:** True

### Steps
1. Submit a valid payment of '10000.00' to payee 'Internet Provider' (account 'INT555444333') using source account '****5002 (Savings, $25,678.90)'; confirm success and note reference code.
2. Press browser Back to return to the Bill Pay form.
3. Click Pay again on the returned form.

### Test Data
```json
{
  "payment_amount": "10000.00",
  "payee_name": "Internet Provider",
  "payee_account": "INT555444333",
  "source_account": "****5002 (Savings, $25,678.90)"
}
```

## TC-002 - Request Auto Loan with collateral and approval
- **Module:** Request Loan
- **Direct Link:** http://localhost:8080/request-loan
- **Requires Auth:** True

### Steps
1. Navigate to Request Loan page
2. Select 'Auto' loan type
3. Enter '40000' in Loan Amount
4. Enter '5000' in Down Payment
5. Select collateral account '****5002 (Savings, $25,678.90)'
6. Click 'Request Loan'

### Test Data
```json
{
  "loan_type": "Auto",
  "loan_amount": 40000,
  "down_payment": 5000,
  "collateral_account": "****5002 (Savings, $25,678.90)"
}
```

## TC-007 - Loan amount below type-specific minimum is rejected
- **Module:** Request Loan
- **Direct Link:** http://localhost:8080/request-loan
- **Requires Auth:** True

### Steps
1. Select 'Personal' loan type
2. Enter '500' in Loan Amount
3. Enter '60' in Down Payment
4. Click 'Request Loan'

### Test Data
```json
{
  "loan_type": "Personal",
  "loan_amount": 500,
  "down_payment": 60
}
```

## TC-010 - Down payment below 10% of loan amount is rejected
- **Module:** Request Loan
- **Direct Link:** http://localhost:8080/request-loan
- **Requires Auth:** True

### Steps
1. Enter '10000' in Loan Amount
2. Enter '500' in Down Payment
3. Click 'Request Loan'

### Test Data
```json
{
  "loan_amount": 10000,
  "down_payment": 500
}
```

## TC-017 - Down payment exactly equals 10% of loan amount passes validation
- **Module:** Request Loan
- **Direct Link:** http://localhost:8080/request-loan
- **Requires Auth:** True

### Steps
1. Select 'Home' loan type
2. Enter '250000' in Loan Amount
3. Enter '25000' in Down Payment
4. Click 'Request Loan'

### Test Data
```json
{
  "loan_type": "Home",
  "loan_amount": 250000,
  "down_payment": 25000
}
```

## TC-021 - Collateral account balance one unit below 20% of loan amount is blocked
- **Module:** Request Loan
- **Direct Link:** http://localhost:8080/request-loan
- **Requires Auth:** True

### Steps
1. Select 'Auto' loan type
2. Enter '29242.60' in Loan Amount
3. Enter '5000' in Down Payment
4. Select the under-collateralised account '****5001 (Checking, $5,847.52)'
5. Click 'Request Loan'

### Test Data
```json
{
  "loan_type": "Auto",
  "loan_amount": 29242.6,
  "down_payment": 5000,
  "collateral_account": "****5001 (Checking, $5,847.52)"
}
```

## TC-004 - Update First and Last Name and save successfully
- **Module:** Update Contact Info
- **Direct Link:** http://localhost:8080/profile
- **Requires Auth:** True

### Steps
1. Enter 'John' in First Name
2. Enter 'Doe' in Last Name
3. Click Update Profile

### Test Data
```json
{
  "first_name": "John",
  "last_name": "Doe"
}
```

## TC-005 - Leave required field (First Name) blank and submit
- **Module:** Update Contact Info
- **Direct Link:** http://localhost:8080/profile
- **Requires Auth:** True

### Steps
1. Clear the First Name field
2. Leave all other fields unchanged
3. Click Update Profile

### Test Data
```json
{
  "original_first_name": "John",
  "original_last_name": "Doe"
}
```

## TC-007 - Invalid phone number format
- **Module:** Update Contact Info
- **Direct Link:** http://localhost:8080/profile
- **Requires Auth:** True

### Steps
1. Replace Phone Number with '***-**-1234'
2. Click Update Profile

### Test Data
```json
{
  "invalid_phone": "***-**-1234"
}
```

## TC-012 - Entering only whitespace into Last Name is treated as missing
- **Module:** Update Contact Info
- **Direct Link:** http://localhost:8080/profile
- **Requires Auth:** True

### Steps
1. Clear Last Name and enter only whitespace characters (three spaces)
2. Click Update Profile

### Test Data
```json
{
  "last_name_whitespace": "   "
}
```

## TC-001 - Submit card request with complete address and account in good standing
- **Module:** Manage Cards
- **Direct Link:** http://localhost:8080/manage-cards
- **Requires Auth:** True

### Steps
1. Navigate to http://localhost:8080/manage-cards (or open Manage Cards from the main menu).
2. Enter 'admin' in the Username field
3. Enter 'Admin123!@#' in the Password field
4. Click 'Sign In'
5. Select 'Debit' from the Card Type dropdown
6. Select '****5001 (Checking, $5,847.52)' from the Account to Link dropdown
7. Enter '123 Main Street' in Shipping Address Line 1
8. Enter 'Springfield' in Shipping City
9. Enter 'IL' in Shipping State
10. Enter '62701' in Shipping Zip Code
11. Enter '(555) 123-4567' in Shipping Phone
12. Click 'Request Card'

### Test Data
```json
{
  "username": "admin",
  "password": "Admin123!@#",
  "card_type": "Debit",
  "linked_account": "****5001 (Checking, $5,847.52)",
  "shipping_address_line1": "123 Main Street",
  "shipping_city": "Springfield",
  "shipping_state": "IL",
  "shipping_zip": "62701",
  "shipping_phone": "(555) 123-4567"
}
```

## TC-008 - Selected account is not in good standing
- **Module:** Manage Cards
- **Direct Link:** http://localhost:8080/manage-cards
- **Requires Auth:** True

### Steps
1. Navigate to http://localhost:8080/manage-cards (or open Manage Cards from the main menu).
2. Enter 'admin' in the Username field
3. Enter 'Admin123!@#' in the Password field
4. Click 'Sign In'
5. Select 'Credit' from the Card Type dropdown
6. Select '****5003 (Credit Card, -$1,534.67)' from the Account to Link dropdown
7. Enter '123 Main Street' in Shipping Address Line 1
8. Enter 'Springfield' in Shipping City
9. Enter 'IL' in Shipping State
10. Enter '62701' in Shipping Zip Code
11. Enter '(555) 123-4567' in Shipping Phone
12. Click 'Request Card'

### Test Data
```json
{
  "username": "admin",
  "password": "Admin123!@#",
  "card_type": "Credit",
  "linked_account": "****5003 (Credit Card, -$1,534.67)",
  "shipping_address_line1": "123 Main Street",
  "shipping_city": "Springfield",
  "shipping_state": "IL",
  "shipping_zip": "62701",
  "shipping_phone": "(555) 123-4567"
}
```

## TC-010 - Travel Notice with Start Date after End Date is rejected
- **Module:** Manage Cards
- **Direct Link:** http://localhost:8080/manage-cards
- **Requires Auth:** True

### Steps
1. Navigate to http://localhost:8080/manage-cards and open Card Controls for card ending in 5001
2. Enter 'admin' in the Username field
3. Enter 'Admin123!@#' in the Password field
4. Click 'Sign In'
5. Click 'Add Travel Notice' (or 'New Travel Notice')
6. Enter '2024-06-10' in the Start Date field
7. Enter '2024-06-05' in the End Date field (Start Date is later than End Date)
8. Click 'Update Controls'

### Test Data
```json
{
  "username": "admin",
  "password": "Admin123!@#",
  "card_last4": "5001",
  "start_date": "2024-06-10",
  "end_date": "2024-06-05"
}
```

## TC-014 - Travel Notice where Start Date equals End Date is accepted
- **Module:** Manage Cards
- **Direct Link:** http://localhost:8080/manage-cards
- **Requires Auth:** True

### Steps
1. Navigate to http://localhost:8080/manage-cards and open Card Controls for card ending in 5001
2. Enter 'admin' in the Username field
3. Enter 'Admin123!@#' in the Password field
4. Click 'Sign In'
5. Click 'Add Travel Notice' (or 'New Travel Notice')
6. Enter '2024-06-05' in the Start Date field
7. Enter '2024-06-05' in the End Date field (same date D in both fields)
8. Click 'Update Controls'

### Test Data
```json
{
  "username": "admin",
  "password": "Admin123!@#",
  "card_last4": "5001",
  "date_D": "2024-06-05"
}
```

## TC-001 - Execute Buy trade with sufficient buying power
- **Module:** Investments
- **Direct Link:** http://localhost:8080/investments
- **Requires Auth:** True

### Steps
1. Navigate to Investments page (http://localhost:8080/investments)
2. Select 'Buy' from Action
3. Enter 'VTSAX' in Fund Symbol and select 'Vanguard Total Stock Market Index (VTSAX)' from the autocomplete
4. Enter quantity '10' in Quantity field
5. Select funding account '****5002 (Savings, $25,678.90)' from Funding Account dropdown
6. Click 'Execute Trade'

### Test Data
```json
{
  "fund_symbol": "VTSAX",
  "quantity": "10",
  "funding_account": "****5002 (Savings, $25,678.90)"
}
```

## TC-013 - Sell with quantity exceeding share balance is blocked
- **Module:** Investments
- **Direct Link:** http://localhost:8080/investments
- **Requires Auth:** True

### Steps
1. Navigate to Investments page (http://localhost:8080/investments)
2. Select 'Sell' from Action
3. Enter 'VTSAX' in Fund Symbol
4. Enter quantity '151' (greater than current holding of 150.5) in Quantity field
5. Select destination account '****5001 (Checking, $5,847.52)' from Destination Account dropdown
6. Click 'Execute Trade'

### Test Data
```json
{
  "fund_symbol": "VTSAX",
  "quantity": "151",
  "destination_account": "****5001 (Checking, $5,847.52)",
  "current_shares": "150.5"
}
```

## TC-014 - Recurring plan with Start Date in the past is rejected
- **Module:** Investments
- **Direct Link:** http://localhost:8080/investments
- **Requires Auth:** True

### Steps
1. Enter 'VTIAX' in Fund Symbol and select 'Vanguard Total International Stock Index (VTIAX)' from autocomplete
2. Enter contribution amount '1000.00' in Contribution Amount
3. Select 'Monthly' from Frequency
4. Enter start date '2024-01-15' (a date in the past) in Start Date field
5. Select funding account '****5001 (Checking, $5,847.52)' from Funding Account dropdown
6. Click 'Create Plan'

### Test Data
```json
{
  "fund_symbol": "VTIAX",
  "contribution_amount": "1000.00",
  "frequency": "Monthly",
  "start_date": "2024-01-15",
  "funding_account": "****5001 (Checking, $5,847.52)"
}
```

## TC-023 - Buy trade with funding account having exactly sufficient buying power succeeds
- **Module:** Investments
- **Direct Link:** http://localhost:8080/investments
- **Requires Auth:** True

### Steps
1. Navigate to Investments page (http://localhost:8080/investments)
2. Select 'Buy' from Action
3. Enter 'VTSAX' in Fund Symbol and select 'Vanguard Total Stock Market Index (VTSAX)' from autocomplete
4. Enter quantity '52.001067' in Quantity field (calculated so total cost ≈ $5,847.52, matching the funding account buying power)
5. Select funding account '****5001 (Checking, $5,847.52)' from Funding Account dropdown
6. Click 'Execute Trade'

### Test Data
```json
{
  "fund_symbol": "VTSAX",
  "quantity": "52.001067",
  "funding_account": "****5001 (Checking, $5,847.52)",
  "calculated_total_cost": "5847.52",
  "fund_price_used": "112.45"
}
```

## TC-002 - Generate statement for a custom date range
- **Module:** Account Statements
- **Direct Link:** http://localhost:8080/statements
- **Requires Auth:** True

### Steps
1. Enter '2024-01-11' in Start Date field
2. Enter '2024-01-14' in End Date field
3. Select account '****5001 (Checking)'
4. Click 'Generate Statement'

### Test Data
```json
{
  "start_date": "2024-01-11",
  "end_date": "2024-01-14",
  "account": "****5001 (Checking)"
}
```

## TC-007 - Custom date range with Start Date after End Date is rejected
- **Module:** Account Statements
- **Direct Link:** http://localhost:8080/statements
- **Requires Auth:** True

### Steps
1. Enter '2024-01-15' in Start Date field
2. Enter '2024-01-10' in End Date field
3. Select account '****5001 (Checking)'
4. Click 'Generate Statement'

### Test Data
```json
{
  "start_date": "2024-01-15",
  "end_date": "2024-01-10",
  "account": "****5001 (Checking)"
}
```

## TC-011 - Custom range where Start Date equals End Date is accepted
- **Module:** Account Statements
- **Direct Link:** http://localhost:8080/statements
- **Requires Auth:** True

### Steps
1. Enter '2024-01-13' in Start Date field
2. Enter '2024-01-13' in End Date field
3. Select account '****5001 (Checking)'
4. Click 'Generate Statement'

### Test Data
```json
{
  "date": "2024-01-13",
  "account": "****5001 (Checking)"
}
```

## TC-001 - Change password with valid current password and strong new password
- **Module:** Security Settings
- **Direct Link:** http://localhost:8080/security-settings
- **Requires Auth:** True

### Steps
1. Expand the Change Password panel
2. Enter 'Admin123!@#' in Current Password
3. Enter 'AdminNewPass!1' in New Password (meets policy)
4. Enter 'AdminNewPass!1' in Confirm New Password
5. Click Change Password

### Test Data
```json
{
  "username": "admin",
  "current_password": "Admin123!@#",
  "new_password": "AdminNewPass!1"
}
```

## TC-006 - Incorrect current password prevents password change
- **Module:** Security Settings
- **Direct Link:** http://localhost:8080/security-settings
- **Requires Auth:** True

### Steps
1. Enter 'WrongPassword!1' in Current Password
2. Enter 'AdminNewPass!1' in New Password (meets policy)
3. Enter 'AdminNewPass!1' in Confirm New Password
4. Click Change Password

### Test Data
```json
{
  "username": "admin",
  "incorrect_current_password": "WrongPassword!1",
  "new_password": "AdminNewPass!1"
}
```

## TC-010 - Browser Back after successful password change blocks resubmission with old password
- **Module:** Security Settings
- **Direct Link:** http://localhost:8080/security-settings
- **Requires Auth:** True

### Steps
1. After "Password changed successfully." is shown, press browser Back
2. Without changing any fields (Current Password still contains 'Admin123!@#'), click Change Password again

### Test Data
```json
{
  "username": "admin",
  "old_password": "Admin123!@#",
  "new_password": "AdminNewPass!1"
}
```

## TC-001 - Send secure message with required Message Body only
- **Module:** Support Center
- **Direct Link:** http://localhost:8080/support-center
- **Requires Auth:** True

### Steps
1. Enter 'Online Purchase - Amazon' in Message Body
2. Click Send Message

### Test Data
```json
{
  "message_body": "Online Purchase - Amazon"
}
```

## TC-016 - Attachment with double extension (allowed + disallowed) is blocked
- **Module:** Support Center
- **Direct Link:** http://localhost:8080/support-center
- **Requires Auth:** True

### Steps
1. Enter 'Internet Provider' in Subject and 'Grocery Store - Walmart' in Message Body
2. Select a file with a double-extension filename (e.g., document.pdf.exe)
3. Click Send Message

### Test Data
```json
{
  "subject": "Internet Provider",
  "message_body": "Grocery Store - Walmart",
  "attachment_filename": "document.pdf.exe"
}
```
