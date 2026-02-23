# ParaBank

**Base URL:** http://localhost:3000
**Generated:** 2026-02-19T22:54:06.230861

## Summary

| Metric | Count |
|--------|-------|
| **Total Tests** | 166 |

### By Type

| Type | Count |
|------|-------|
| Positive | 42 |
| Negative | 103 |
| Edge Case | 21 |

### By Priority

| Priority | Count |
|----------|-------|
| High | 35 |
| Medium | 104 |
| Low | 27 |

### Post-Verification Coverage

| Metric | Count |
|--------|-------|
| Tests Needing Verification | 18 |
| Full Coverage | 7 |
| Partial Coverage | 5 |
| No Coverage | 6 |

### Execution Plans

| Metric | Value |
|--------|-------|
| Total Plans | 18 |
| Automated Steps | 18 |
| Manual Steps | 7 |
| Automation Rate | 72.0% |

---

## Test Cases

### Login

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| LOGIN-001 | Successful login with valid email and password | None | 1. Enter a valid email address in the Email/Username input field<br>2. Enter a valid password in the Password input field<br>3. Click the Sign In button | Signed in successfully and redirects to Accounts Overview | High |
| LOGIN-002 | Successful login with valid username and password | None | 1. Enter a valid username in the Email/Username input field<br>2. Enter a valid password in the Password input field<br>3. Click the Sign In button | Signed in successfully and redirects to Accounts Overview | High |
| LOGIN-012 | Verify Register link is present | None | 1. Check if the Register link is present on the page | Register link is present | Low |
| LOGIN-013 | Verify Forgot Password? link is present | None | 1. Check if the Forgot Password? link is present on the page | Forgot Password? link is present | Low |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| LOGIN-003 | Email field empty | None | 1. Leave the Email/Username input field empty<br>2. Enter a valid password in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-004 | Password field empty | None | 1. Enter a valid email address in the Email/Username input field<br>2. Leave the Password input field empty<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-005 | Invalid email format | None | 1. Enter an invalid email format in the Email/Username input field<br>2. Enter a valid password in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-006 | Password less than 8 characters | None | 1. Enter a valid email address in the Email/Username input field<br>2. Enter a password with less than 8 characters in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-007 | Password missing uppercase character | None | 1. Enter a valid email address in the Email/Username input field<br>2. Enter a password missing an uppercase character in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-008 | Password missing lowercase character | None | 1. Enter a valid email address in the Email/Username input field<br>2. Enter a password missing a lowercase character in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-009 | Password missing number | None | 1. Enter a valid email address in the Email/Username input field<br>2. Enter a password missing a number in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-010 | Password missing special character | None | 1. Enter a valid email address in the Email/Username input field<br>2. Enter a password missing a special character in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |
| LOGIN-011 | Incorrect email and password combination | None | 1. Enter an incorrect email address in the Email/Username input field<br>2. Enter an incorrect password in the Password input field<br>3. Click the Sign In button | Error message displayed: 'Incorrect email or password. Please try again', clears the password field | Medium |

---

### Register

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| REGIST-001 | Successful account registration with all valid inputs | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Account created successfully — please sign in | High |
| REGIST-002 | ZIP Code in 5+4 format | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5+4 format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Account created successfully — please sign in | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| REGIST-003 | First Name field empty | None | 1. Leave First Name field empty<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: First Name is required | Medium |
| REGIST-004 | Last Name field empty | None | 1. Enter valid first name<br>2. Leave Last Name field empty<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Last Name is required | Medium |
| REGIST-005 | Street Address field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Leave Street Address field empty<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Street Address is required | Medium |
| REGIST-006 | City field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Leave City field empty<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: City is required | Medium |
| REGIST-007 | State not selected | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Do not select a state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: State is required | Medium |
| REGIST-008 | ZIP Code field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Leave ZIP Code field empty<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: ZIP Code is required | Medium |
| REGIST-009 | Phone Number field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Leave Phone Number field empty<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Phone Number is required | Medium |
| REGIST-010 | Phone Number format invalid | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter phone number in invalid format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Phone Number must follow (123) 456-7890 format | Medium |
| REGIST-011 | Social Security Number field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Leave Social Security Number field empty<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Social Security Number is required | Medium |
| REGIST-012 | Social Security Number format invalid | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter Social Security Number in invalid format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Social Security Number must follow 123-45-6789 format | Medium |
| REGIST-013 | Username field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Leave Username field empty<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Username is required | Medium |
| REGIST-014 | Username not in email format | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter username not in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Username must be valid email format | Medium |
| REGIST-015 | Password field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Leave Password field empty<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Password is required | Medium |
| REGIST-016 | Password less than 8 characters | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter password with less than 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: Password must be at least 8 characters | Medium |
| REGIST-017 | Confirm Password field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Leave Confirm Password field empty<br>12. Click Register button | Error displayed: Confirm Password is required | Medium |
| REGIST-018 | Confirm Password does not match Password | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter valid ZIP Code in 5 digits format<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter non-matching confirm password<br>12. Click Register button | Error displayed: Confirm Password must match Password | Medium |
| REGIST-019 | ZIP Code less than 5 digits | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Select valid state from dropdown<br>6. Enter ZIP Code with less than 5 digits<br>7. Enter valid phone number in (123) 456-7890 format<br>8. Enter valid Social Security Number in 123-45-6789 format<br>9. Enter valid username in email format<br>10. Enter valid password with at least 8 characters<br>11. Enter matching confirm password<br>12. Click Register button | Error displayed: ZIP Code must be 5 digits or 5+4 format | Medium |

---

### Accounts Overview

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ACCOVE-001 | Verify welcome message displays user's name | User is logged in | 1. Check the welcome message at the top of the dashboard | Welcome message displays the logged-in user's name | High |
| ACCOVE-002 | Verify all accounts are displayed for the user | User has multiple accounts | 1. Check the accounts table for all user accounts | All accounts belonging to the user are displayed in the table | High |
| ACCOVE-003 | Verify account numbers are masked except last 4 digits | Accounts are displayed in the table | 1. Check the account number column in the accounts table | Account numbers are masked, showing only the last 4 digits | High |
| ACCOVE-004 | Verify accounts are ordered by creation date | User has multiple accounts | 1. Check the order of accounts in the table by open date | Accounts are ordered by creation date, earliest first | High |
| ACCOVE-005 | Verify current balance is displayed for each account | Accounts are displayed in the table | 1. Check the current balance column in the accounts table | Current balance is displayed for each account | High |
| ACCOVE-006 | Verify total balance is displayed in the footer | User has accounts with balances | 1. Check the footer of the dashboard for total balance | Total balance of all accounts is displayed in the footer | Medium |
| ACCOVE-007 | Verify account status shows as active | Accounts are displayed in the table | 1. Check the account status column in the accounts table | Account status shows as 'Active' with a badge | Medium |

---

### Open New Account

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ONA-001 | Open Checking Account with valid deposit and funding source | User is on the Open New Account page | 1. Select 'Checking' account type<br>2. Enter a valid deposit amount greater than or equal to $25<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | 'Account opened successfully!' message is displayed and user is redirected to accounts overview | High |
| ONA-002 | Open Savings Account with valid deposit and funding source | User is on the Open New Account page | 1. Select 'Savings' account type<br>2. Enter a valid deposit amount greater than or equal to $100<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | 'Account opened successfully!' message is displayed and user is redirected to accounts overview | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ONA-003 | Account type not selected | User is on the Open New Account page | 1. Leave account type unselected<br>2. Enter a valid deposit amount<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | Real-time validation error is displayed indicating account type must be selected | Medium |
| ONA-004 | Deposit amount field empty | User is on the Open New Account page | 1. Select an account type<br>2. Leave deposit amount field empty<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | Real-time validation error is displayed indicating deposit amount is required | Medium |
| ONA-005 | Deposit amount below minimum for Checking | User is on the Open New Account page | 1. Select 'Checking' account type<br>2. Enter a deposit amount less than $25<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | Real-time validation error is displayed indicating deposit amount must be at least $25 | Medium |
| ONA-006 | Deposit amount below minimum for Savings | User is on the Open New Account page | 1. Select 'Savings' account type<br>2. Enter a deposit amount less than $100<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | Real-time validation error is displayed indicating deposit amount must be at least $100 | Medium |
| ONA-007 | Funding source account not selected | User is on the Open New Account page | 1. Select an account type<br>2. Enter a valid deposit amount<br>3. Leave funding source account unselected<br>4. Click on 'Open Account' button | Real-time validation error is displayed indicating funding source account must be selected | Medium |
| ONA-008 | Funding source account with insufficient balance | User is on the Open New Account page | 1. Select an account type<br>2. Enter a valid deposit amount<br>3. Select a funding source account with insufficient balance<br>4. Click on 'Open Account' button | Real-time validation error is displayed indicating insufficient funds in the funding source account | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ONA-009 | Deposit amount exactly at minimum for Checking | User is on the Open New Account page | 1. Select 'Checking' account type<br>2. Enter a deposit amount exactly $25<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | 'Account opened successfully!' message is displayed and user is redirected to accounts overview | Low |
| ONA-010 | Deposit amount exactly at minimum for Savings | User is on the Open New Account page | 1. Select 'Savings' account type<br>2. Enter a deposit amount exactly $100<br>3. Select a funding source account with sufficient balance<br>4. Click on 'Open Account' button | 'Account opened successfully!' message is displayed and user is redirected to accounts overview | Low |

---

### Transfer Funds

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| TRAFUN-001 | Successful internal transfer between different accounts | User has sufficient funds in the source account | 1. Select 'Internal Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Select a different account from the Source Account dropdown<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button | Transfer completed successfully with a transaction ID | High |
| TRAFUN-002 | Successful external transfer with matching account numbers | User has sufficient funds in the source account | 1. Select 'External Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Select an account from the Source Account dropdown<br>4. Enter a valid account number in the Account Number input<br>5. Re-enter the same account number in the Confirm Account Number input<br>6. Click on 'Transfer' button | Transfer completed successfully with a transaction ID | High |
| TRAFUN-003 | Verify balance update after successful transfer | User has sufficient funds in the source account | 1. Select 'Internal Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Select a different account from the Source Account dropdown<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button<br>6. Check the balance of the source account | Balance of the source account is reduced by the transfer amount | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| TRAFUN-004 | Insufficient funds in source account | User does not have sufficient funds in the source account | 1. Select 'Internal Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Select a different account from the Source Account dropdown<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button | Error message indicating insufficient funds | High |
| TRAFUN-005 | Transfer Amount field empty | None | 1. Select 'Internal Transfer' radio button<br>2. Leave the Transfer Amount field empty<br>3. Select a different account from the Source Account dropdown<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button | Error message indicating the Transfer Amount field is required | Medium |
| TRAFUN-006 | Source Account dropdown empty | None | 1. Select 'Internal Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Leave the Source Account dropdown unselected<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button | Error message indicating the Source Account is required | Medium |
| TRAFUN-007 | Transfer to the same account | None | 1. Select 'Internal Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Select the same account in both Source and Destination Account dropdowns<br>4. Click on 'Transfer' button | Error message indicating that transfer to the same account is not allowed | Medium |
| TRAFUN-008 | Account numbers do not match for external transfer | None | 1. Select 'External Transfer' radio button<br>2. Enter a valid positive amount in the Transfer Amount field<br>3. Select an account from the Source Account dropdown<br>4. Enter a valid account number in the Account Number input<br>5. Enter a different account number in the Confirm Account Number input<br>6. Click on 'Transfer' button | Error message indicating account numbers do not match | Medium |
| TRAFUN-009 | Transfer amount is zero | None | 1. Select 'Internal Transfer' radio button<br>2. Enter zero in the Transfer Amount field<br>3. Select a different account from the Source Account dropdown<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button | Error message indicating transfer amount must be positive | Medium |
| TRAFUN-010 | Transfer amount is negative | None | 1. Select 'Internal Transfer' radio button<br>2. Enter a negative amount in the Transfer Amount field<br>3. Select a different account from the Source Account dropdown<br>4. Select a different account from the Destination Account dropdown<br>5. Click on 'Transfer' button | Error message indicating transfer amount must be positive | Medium |

---

### Bill Pay

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| BILPAY-001 | Successful bill payment with valid inputs | User is logged in and has sufficient balance | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a positive numeric Payment Amount<br>10. Select a Source Account with sufficient balance<br>11. Click the Pay button | Payment submitted successfully with reference code and balances updated | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| BILPAY-002 | Payee Name field empty | None | 1. Leave the Payee Name field empty<br>2. Enter valid data in all other fields<br>3. Click the Pay button | Error message displayed indicating Payee Name is required | Medium |
| BILPAY-003 | Street Address field empty | None | 1. Enter a valid Payee Name<br>2. Leave the Street Address field empty<br>3. Enter valid data in all other fields<br>4. Click the Pay button | Error message displayed indicating Street Address is required | Medium |
| BILPAY-004 | City field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Leave the City field empty<br>4. Enter valid data in all other fields<br>5. Click the Pay button | Error message displayed indicating City is required | Medium |
| BILPAY-005 | State field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Leave the State field empty<br>5. Enter valid data in all other fields<br>6. Click the Pay button | Error message displayed indicating State is required | Medium |
| BILPAY-006 | ZIP Code field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Leave the ZIP Code field empty<br>6. Enter valid data in all other fields<br>7. Click the Pay button | Error message displayed indicating ZIP Code is required | Medium |
| BILPAY-007 | Phone Number field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Leave the Phone Number field empty<br>7. Enter valid data in all other fields<br>8. Click the Pay button | Error message displayed indicating Phone Number is required | Medium |
| BILPAY-008 | Payee Account Number field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Leave the Payee Account Number field empty<br>8. Enter valid data in all other fields<br>9. Click the Pay button | Error message displayed indicating Payee Account Number is required | Medium |
| BILPAY-009 | Confirm Account Number field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Leave the Confirm Account Number field empty<br>9. Enter valid data in all other fields<br>10. Click the Pay button | Error message displayed indicating Confirm Account Number is required | Medium |
| BILPAY-010 | Account numbers do not match | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Enter a different number in Confirm Account Number<br>9. Enter valid data in all other fields<br>10. Click the Pay button | Error message displayed indicating 'Account numbers do not match' | Medium |
| BILPAY-011 | Payment Amount field empty | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Leave the Payment Amount field empty<br>10. Select a Source Account<br>11. Click the Pay button | Error message displayed indicating Payment Amount is required | Medium |
| BILPAY-012 | Payment Amount is non-numeric | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a non-numeric value in Payment Amount<br>10. Select a Source Account<br>11. Click the Pay button | Error message displayed indicating Payment Amount must be numeric | Medium |
| BILPAY-013 | Payment Amount is negative | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a negative value in Payment Amount<br>10. Select a Source Account<br>11. Click the Pay button | Error message displayed indicating Payment Amount must be positive | Medium |
| BILPAY-014 | Source Account not selected | None | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a positive numeric Payment Amount<br>10. Leave the Source Account dropdown unselected<br>11. Click the Pay button | Error message displayed indicating Source Account is required | Medium |
| BILPAY-015 | Insufficient funds in Source Account | User is logged in with insufficient balance in selected Source Account | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a positive numeric Payment Amount<br>10. Select a Source Account with insufficient balance<br>11. Click the Pay button | Error message displayed indicating 'Insufficient funds' | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| BILPAY-016 | Payment Amount at exact boundary | User is logged in and has exact balance for the payment amount | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a Payment Amount equal to the balance in Source Account<br>10. Select the Source Account<br>11. Click the Pay button | Payment submitted successfully with reference code and balances updated | Low |
| BILPAY-017 | Payment Amount just below boundary | User is logged in and has slightly more balance than the payment amount | 1. Enter a valid Payee Name<br>2. Enter a valid Street Address<br>3. Enter a valid City<br>4. Enter a valid State<br>5. Enter a valid ZIP Code<br>6. Enter a valid Phone Number<br>7. Enter a valid Payee Account Number<br>8. Re-enter the same Payee Account Number in Confirm Account Number<br>9. Enter a Payment Amount just below the balance in Source Account<br>10. Select the Source Account<br>11. Click the Pay button | Payment submitted successfully with reference code and balances updated | Low |

---

### Request Loan

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| REQLOA-001 | Apply for a loan with valid inputs | None | 1. Select a valid loan type<br>2. Enter a valid loan amount within the specified range<br>3. Enter a valid down payment less than the loan amount<br>4. Select a valid collateral account with sufficient funds<br>5. Click the Apply button | Loan approved and created successfully! | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| REQLOA-002 | Loan Amount field empty | None | 1. Select a valid loan type<br>2. Leave the Loan Amount field empty<br>3. Enter a valid down payment<br>4. Select a valid collateral account<br>5. Click the Apply button | Error message indicating Loan Amount is required | Medium |
| REQLOA-003 | Down Payment Amount field empty | None | 1. Select a valid loan type<br>2. Enter a valid loan amount<br>3. Leave the Down Payment Amount field empty<br>4. Select a valid collateral account<br>5. Click the Apply button | Error message indicating Down Payment Amount is required | Medium |
| REQLOA-004 | Collateral Account field empty | None | 1. Select a valid loan type<br>2. Enter a valid loan amount<br>3. Enter a valid down payment<br>4. Leave the Collateral Account field empty<br>5. Click the Apply button | Error message indicating Collateral Account is required | Medium |
| REQLOA-005 | Loan amount outside specified range | None | 1. Select a valid loan type<br>2. Enter a loan amount outside the specified range<br>3. Enter a valid down payment<br>4. Select a valid collateral account<br>5. Click the Apply button | Error message indicating loan amount must be within the specified range | Medium |
| REQLOA-006 | Down payment greater than loan amount | None | 1. Select a valid loan type<br>2. Enter a valid loan amount<br>3. Enter a down payment greater than the loan amount<br>4. Select a valid collateral account<br>5. Click the Apply button | Error message indicating down payment must be less than loan amount | Medium |
| REQLOA-007 | Insufficient collateral funds | None | 1. Select a valid loan type<br>2. Enter a valid loan amount<br>3. Enter a valid down payment<br>4. Select a collateral account with insufficient funds<br>5. Click the Apply button | Denial shows 'Inadequate collateral value' | Medium |
| REQLOA-008 | Collateral value less than 20% requirement | None | 1. Select a valid loan type<br>2. Enter a valid loan amount<br>3. Enter a valid down payment<br>4. Select a collateral account where collateral value is less than 20% of loan amount<br>5. Click the Apply button | Denial shows 'Inadequate collateral value' | Medium |
| REQLOA-009 | Loan application denied due to insufficient credit history | None | 1. Select a valid loan type<br>2. Enter a valid loan amount<br>3. Enter a valid down payment<br>4. Select a valid collateral account<br>5. Click the Apply button | Denial shows 'Insufficient credit history' | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| REQLOA-010 | Loan amount exactly at the boundary value | None | 1. Select a valid loan type<br>2. Enter a loan amount exactly at the boundary value<br>3. Enter a valid down payment<br>4. Select a valid collateral account<br>5. Click the Apply button | Loan approved and created successfully! | Low |
| REQLOA-011 | Loan amount just below the boundary value | None | 1. Select a valid loan type<br>2. Enter a loan amount just below the boundary value<br>3. Enter a valid down payment<br>4. Select a valid collateral account<br>5. Click the Apply button | Loan approved and created successfully! | Low |

---

### Update Contact Info

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| UCI-001 | Update profile with valid data | Form is pre-populated with current user data | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Profile updated successfully | High |
| UCI-002 | Form pre-populated with current user data | User is logged in | 1. Verify first name field is pre-populated<br>2. Verify last name field is pre-populated<br>3. Verify street address field is pre-populated<br>4. Verify city field is pre-populated<br>5. Verify state field is pre-populated<br>6. Verify ZIP code field is pre-populated<br>7. Verify phone number field is pre-populated | All fields are pre-populated with current user data | Medium |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| UCI-003 | First Name field empty | None | 1. Leave first name field empty<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Inline error banner displayed for first name field | Medium |
| UCI-004 | Last Name field empty | None | 1. Enter valid first name<br>2. Leave last name field empty<br>3. Enter valid street address<br>4. Enter valid city<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Inline error banner displayed for last name field | Medium |
| UCI-005 | Street Address field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Leave street address field empty<br>4. Enter valid city<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Inline error banner displayed for street address field | Medium |
| UCI-006 | City field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Leave city field empty<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Inline error banner displayed for city field | Medium |
| UCI-007 | State field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Leave state field empty<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Inline error banner displayed for state field | Medium |
| UCI-008 | ZIP Code field empty | None | 1. Enter valid first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Enter valid state<br>6. Leave ZIP code field empty<br>7. Enter valid phone number<br>8. Click Update Profile button | Inline error banner displayed for ZIP code field | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| UCI-009 | Maximum length for first name | None | 1. Enter maximum length first name<br>2. Enter valid last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Profile updated successfully | Low |
| UCI-010 | Maximum length for last name | None | 1. Enter valid first name<br>2. Enter maximum length last name<br>3. Enter valid street address<br>4. Enter valid city<br>5. Enter valid state<br>6. Enter valid ZIP code<br>7. Enter valid phone number<br>8. Click Update Profile button | Profile updated successfully | Low |

---

### Manage Cards

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| MANCAR-001 | Submit card request with valid inputs | User is on the Request New Card page | 1. Select a card type from the Card Type selection<br>2. Select an account from the Account to Link dropdown<br>3. Enter a complete shipping address in the Shipping Address input<br>4. Click the Request Card button | Card request submitted successfully with tracking ID | High |
| MANCAR-002 | Update card controls with valid inputs | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a valid new spending limit<br>3. Add a valid travel notice<br>4. Toggle the card status<br>5. Click the Update Controls button | Card controls updated successfully | High |
| MANCAR-011 | Verify card type selection displays available card types | User is on the Request New Card page | 1. Click on the Card Type selection | Available card types are displayed in the dropdown | Low |
| MANCAR-012 | Verify account to link dropdown displays available accounts | User is on the Request New Card page | 1. Click on the Account to Link dropdown | Available accounts are displayed in the dropdown | Low |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| MANCAR-003 | Submit card request with valid card type and account, but empty shipping address | User is on the Request New Card page | 1. Select a card type from the Card Type selection<br>2. Select an account from the Account to Link dropdown<br>3. Leave the Shipping Address input empty<br>4. Click the Request Card button | Error message indicating that the shipping address is required | Medium |
| MANCAR-004 | Submit card request with valid card type and shipping address, but no account selected | User is on the Request New Card page | 1. Select a card type from the Card Type selection<br>2. Leave the Account to Link dropdown unselected<br>3. Enter a complete shipping address in the Shipping Address input<br>4. Click the Request Card button | Error message indicating that an account selection is required | Medium |
| MANCAR-005 | Submit card request with all fields empty | User is on the Request New Card page | 1. Leave the Card Type selection unselected<br>2. Leave the Account to Link dropdown unselected<br>3. Leave the Shipping Address input empty<br>4. Click the Request Card button | Error messages indicating that all fields are required | Medium |
| MANCAR-006 | New spending limit field empty | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Leave the new spending limit field empty<br>3. Add a valid travel notice<br>4. Toggle the card status<br>5. Click the Update Controls button | Validation error appears inline indicating the spending limit is required | Medium |
| MANCAR-007 | Travel notice field empty | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a valid new spending limit<br>3. Leave the travel notice field empty<br>4. Toggle the card status<br>5. Click the Update Controls button | Validation error appears inline indicating the travel notice is required | Medium |
| MANCAR-008 | Invalid numeric limit for spending limit | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter an invalid numeric value in the new spending limit field<br>3. Add a valid travel notice<br>4. Toggle the card status<br>5. Click the Update Controls button | Validation error appears inline indicating the spending limit must be a valid number | Medium |
| MANCAR-009 | Invalid date range for travel notice | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a valid new spending limit<br>3. Add an invalid date range in the travel notice<br>4. Toggle the card status<br>5. Click the Update Controls button | Validation error appears inline indicating the date range is invalid | Medium |
| MANCAR-010 | Invalid card status transition | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a valid new spending limit<br>3. Add a valid travel notice<br>4. Attempt an invalid card status transition<br>5. Click the Update Controls button | Validation error appears inline indicating the card status transition is not allowed | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| MANCAR-013 | Submit card request with maximum length shipping address | User is on the Request New Card page | 1. Select a card type from the Card Type selection<br>2. Select an account from the Account to Link dropdown<br>3. Enter a maximum length shipping address in the Shipping Address input<br>4. Click the Request Card button | Card request submitted successfully with tracking ID | Low |
| MANCAR-014 | Boundary test for spending limit at exact limit | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a spending limit at the exact boundary value<br>3. Add a valid travel notice<br>4. Toggle the card status<br>5. Click the Update Controls button | Card controls updated successfully | Low |
| MANCAR-015 | Boundary test for spending limit just below limit | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a spending limit just below the boundary value<br>3. Add a valid travel notice<br>4. Toggle the card status<br>5. Click the Update Controls button | Card controls updated successfully | Low |
| MANCAR-016 | Boundary test for travel notice with same start and end date | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a valid new spending limit<br>3. Add a travel notice with the same start and end date<br>4. Toggle the card status<br>5. Click the Update Controls button | Card controls updated successfully | Low |
| MANCAR-017 | Boundary test for future date in travel notice | User is on the Manage Cards page with an existing card selected | 1. Select an existing card from the dropdown<br>2. Enter a valid new spending limit<br>3. Add a travel notice with a future date<br>4. Toggle the card status<br>5. Click the Update Controls button | Card controls updated successfully | Low |

---

### Investments

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| INVEST-001 | Execute trade successfully with valid inputs | User is on the Execute Trade page | 1. Select 'Buy' action<br>2. Enter a valid fund symbol<br>3. Enter a valid quantity greater than 0<br>4. Select a valid funding account<br>5. Click the 'Execute Trade' button | Trade executed successfully with an order ID displayed | High |
| INVEST-002 | Create recurring investment plan successfully with valid inputs | None | 1. Enter a valid fund symbol<br>2. Enter a valid contribution amount meeting the minimum requirement<br>3. Select a valid frequency<br>4. Enter a valid future start date<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Plan created successfully | High |
| INVEST-013 | Verify funding/destination account dropdown displays correctly | User is on the Execute Trade page | 1. Check the funding/destination account dropdown | Dropdown displays all available accounts correctly | Low |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| INVEST-003 | Execute trade with missing quantity | User is on the Execute Trade page | 1. Select 'Buy' action<br>2. Enter a valid fund symbol<br>3. Leave the quantity field empty<br>4. Select a valid funding account<br>5. Click the 'Execute Trade' button | Error message displayed indicating quantity is required | Medium |
| INVEST-004 | Execute trade with quantity less than or equal to zero | User is on the Execute Trade page | 1. Select 'Buy' action<br>2. Enter a valid fund symbol<br>3. Enter a quantity of 0<br>4. Select a valid funding account<br>5. Click the 'Execute Trade' button | Error message displayed indicating quantity must be greater than 0 | Medium |
| INVEST-005 | Execute trade with invalid fund symbol | User is on the Execute Trade page | 1. Select 'Buy' action<br>2. Enter an invalid fund symbol<br>3. Enter a valid quantity greater than 0<br>4. Select a valid funding account<br>5. Click the 'Execute Trade' button | Error message displayed indicating the fund symbol is invalid | Medium |
| INVEST-006 | Execute trade with insufficient buying power | User is on the Execute Trade page | 1. Select 'Buy' action<br>2. Enter a valid fund symbol<br>3. Enter a valid quantity greater than 0<br>4. Select a funding account with insufficient balance<br>5. Click the 'Execute Trade' button | Error message displayed indicating insufficient buying power | Medium |
| INVEST-007 | Execute trade with insufficient share balance | User is on the Execute Trade page | 1. Select 'Sell' action<br>2. Enter a valid fund symbol<br>3. Enter a valid quantity greater than 0<br>4. Select a destination account with insufficient shares<br>5. Click the 'Execute Trade' button | Error message displayed indicating insufficient share balance | Medium |
| INVEST-008 | Contribution Amount field empty | None | 1. Enter a valid fund symbol<br>2. Leave the Contribution Amount field empty<br>3. Select a valid frequency<br>4. Enter a valid future start date<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Error message displayed indicating Contribution Amount is required | Medium |
| INVEST-009 | Contribution Amount below minimum requirement | None | 1. Enter a valid fund symbol<br>2. Enter a contribution amount below the minimum requirement<br>3. Select a valid frequency<br>4. Enter a valid future start date<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Error message displayed indicating Contribution Amount must meet minimum | Medium |
| INVEST-010 | Start Date field empty | None | 1. Enter a valid fund symbol<br>2. Enter a valid contribution amount meeting the minimum requirement<br>3. Select a valid frequency<br>4. Leave the Start Date field empty<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Error message displayed indicating Start Date is required | Medium |
| INVEST-011 | Start Date not in the future | None | 1. Enter a valid fund symbol<br>2. Enter a valid contribution amount meeting the minimum requirement<br>3. Select a valid frequency<br>4. Enter a start date that is not in the future<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Error message displayed indicating Start Date must be in the future | Medium |
| INVEST-012 | Funding account with inadequate balance | None | 1. Enter a valid fund symbol<br>2. Enter a valid contribution amount meeting the minimum requirement<br>3. Select a valid frequency<br>4. Enter a valid future start date<br>5. Select a funding account with inadequate balance<br>6. Click the Create Plan button | Error message displayed indicating inadequate funding balance | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| INVEST-014 | Exact minimum contribution amount | None | 1. Enter a valid fund symbol<br>2. Enter a contribution amount exactly at the minimum requirement<br>3. Select a valid frequency<br>4. Enter a valid future start date<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Plan created successfully | Low |
| INVEST-015 | Contribution Amount just below minimum requirement | None | 1. Enter a valid fund symbol<br>2. Enter a contribution amount just below the minimum requirement<br>3. Select a valid frequency<br>4. Enter a valid future start date<br>5. Select a valid funding account with adequate balance<br>6. Click the Create Plan button | Error message displayed indicating Contribution Amount must meet minimum | Low |

---

### Account Statements

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ACCSTA-001 | Generate statement for a selected month and year | User is on the account statements page | 1. Select a valid account from the Account dropdown<br>2. Select a specific month and year from the Statement Period<br>3. Click on the Generate Statement button | Statement generated successfully | High |
| ACCSTA-002 | Generate statement for a custom date range | User is on the account statements page | 1. Select a valid account from the Account dropdown<br>2. Select a valid start date and end date from the Statement Period<br>3. Click on the Generate Statement button | Statement generated successfully | High |
| ACCSTA-003 | Opt into paperless statements with valid email | None | 1. Check the checkbox to opt into paperless statements<br>2. Enter a valid email address in the Email Address input<br>3. Click the Save Preference button | e-Statement preference updated | High |
| ACCSTA-004 | Verify email field presence when opting into paperless statements | None | 1. Check the checkbox to opt into paperless statements | Email Address input is displayed and required | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ACCSTA-005 | Account dropdown field empty | User is on the account statements page | 1. Leave the Account dropdown unselected<br>2. Select a specific month and year from the Statement Period<br>3. Click on the Generate Statement button | Unable to generate statement — please try again later | Medium |
| ACCSTA-006 | Email field required when opting into paperless statements | None | 1. Check the checkbox to opt into paperless statements<br>2. Leave the Email Address input empty<br>3. Click the Save Preference button | Email field highlighted with guidance on failure | Medium |
| ACCSTA-007 | Invalid email format when opting into paperless statements | None | 1. Check the checkbox to opt into paperless statements<br>2. Enter an invalid email format in the Email Address input<br>3. Click the Save Preference button | Email field highlighted with guidance on failure | Medium |
| ACCSTA-008 | Opt into paperless statements without checking the checkbox | None | 1. Leave the checkbox for paperless statements unchecked<br>2. Enter a valid email address in the Email Address input<br>3. Click the Save Preference button | No changes made to e-Statement preference | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| ACCSTA-009 | Generate statement with same start and end date | User is on the account statements page | 1. Select a valid account from the Account dropdown<br>2. Select the same date for both start and end date in the Statement Period<br>3. Click on the Generate Statement button | Statement generated successfully | Low |
| ACCSTA-010 | Generate statement with future date range | User is on the account statements page | 1. Select a valid account from the Account dropdown<br>2. Select a future start date and end date from the Statement Period<br>3. Click on the Generate Statement button | Unable to generate statement — please try again later | Low |

---

### Security Settings

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| SECSET-001 | Change password successfully | User is logged in and on the Security Settings page | 1. Enter the correct current password<br>2. Enter a new password that meets the strong-password policy<br>3. Enter the same new password in the Confirm New Password field<br>4. Click the Change Password button | Password changed successfully. | High |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| SECSET-002 | Current password incorrect | User is on the Security Settings page | 1. Enter an incorrect current password<br>2. Enter a valid new password<br>3. Enter the same new password in the Confirm New Password field<br>4. Click the Change Password button | Validation error indicating the current password is incorrect. | High |
| SECSET-003 | New Password and Confirm New Password mismatch | User is on the Security Settings page | 1. Enter the correct current password<br>2. Enter a valid new password<br>3. Enter a different password in the Confirm New Password field<br>4. Click the Change Password button | Validation error indicating the passwords do not match. | High |
| SECSET-004 | Current Password field empty | User is on the Security Settings page | 1. Leave the Current Password field empty<br>2. Enter a valid new password<br>3. Enter the same new password in the Confirm New Password field<br>4. Click the Change Password button | Validation error highlighting the Current Password field. | Medium |
| SECSET-005 | New Password field empty | User is on the Security Settings page | 1. Enter the correct current password<br>2. Leave the New Password field empty<br>3. Enter a valid password in the Confirm New Password field<br>4. Click the Change Password button | Validation error highlighting the New Password field. | Medium |
| SECSET-006 | Confirm New Password field empty | User is on the Security Settings page | 1. Enter the correct current password<br>2. Enter a valid new password<br>3. Leave the Confirm New Password field empty<br>4. Click the Change Password button | Validation error highlighting the Confirm New Password field. | Medium |
| SECSET-007 | New password does not meet policy | User is on the Security Settings page | 1. Enter the correct current password<br>2. Enter a new password that does not meet the strong-password policy<br>3. Enter the same new password in the Confirm New Password field<br>4. Click the Change Password button | Validation error indicating the new password does not meet the policy. | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| SECSET-008 | New password exactly 8 characters | User is on the Security Settings page | 1. Enter the correct current password<br>2. Enter a new password that is exactly 8 characters long and meets the strong-password policy<br>3. Enter the same new password in the Confirm New Password field<br>4. Click the Change Password button | Password changed successfully. | Low |
| SECSET-009 | New password just below 8 characters | User is on the Security Settings page | 1. Enter the correct current password<br>2. Enter a new password that is 7 characters long<br>3. Enter the same new password in the Confirm New Password field<br>4. Click the Change Password button | Validation error indicating the new password does not meet the policy. | Low |

---

### Support Center

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| SUPCEN-001 | Send secure message with valid inputs | User is logged in and on the Send Secure Message page | 1. Enter a valid subject in the Subject input<br>2. Select a category from the Category dropdown<br>3. Enter a valid message in the Message Body<br>4. Click the Send Message button | Message sent successfully with a ticket ID displayed | High |
| SUPCEN-002 | Submit callback request successfully with valid inputs | None | 1. Select a valid reason from the Reason for Call dropdown<br>2. Enter a valid date that is at least the next business day in the Preferred Date input<br>3. Enter a valid time window in the Preferred Time Window input<br>4. Enter a valid phone number in the Phone Number input<br>5. Click the Request Callback button | Callback request submitted and email confirmation sent | High |
| SUPCEN-003 | Send secure message with valid inputs and attachment | User is logged in and on the Send Secure Message page | 1. Enter a valid subject in the Subject input<br>2. Select a category from the Category dropdown<br>3. Enter a valid message in the Message Body<br>4. Attach a valid file using the Attachment input<br>5. Click the Send Message button | Message sent successfully with a ticket ID displayed | Medium |
| SUPCEN-012 | Verify form elements display correctly | User is logged in and on the Send Secure Message page | 1. Verify the Subject input is displayed<br>2. Verify the Category dropdown is displayed<br>3. Verify the Message Body is displayed<br>4. Verify the Attachment input is displayed<br>5. Verify the Send Message button is displayed | All form elements are displayed correctly | Low |

#### ❌ Negative Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| SUPCEN-004 | Subject field empty | User is logged in and on the Send Secure Message page | 1. Leave the Subject input empty<br>2. Select a category from the Category dropdown<br>3. Enter a valid message in the Message Body<br>4. Click the Send Message button | Inline guidance displayed indicating the Subject field is required | Medium |
| SUPCEN-005 | Message Body field empty | User is logged in and on the Send Secure Message page | 1. Enter a valid subject in the Subject input<br>2. Select a category from the Category dropdown<br>3. Leave the Message Body empty<br>4. Click the Send Message button | Inline guidance displayed indicating the Message Body is required | Medium |
| SUPCEN-006 | Reason for Call field empty | None | 1. Leave the Reason for Call dropdown empty<br>2. Enter a valid date that is at least the next business day in the Preferred Date input<br>3. Enter a valid time window in the Preferred Time Window input<br>4. Enter a valid phone number in the Phone Number input<br>5. Click the Request Callback button | Inline validation error for empty Reason for Call field | Medium |
| SUPCEN-007 | Preferred Date field empty | None | 1. Select a valid reason from the Reason for Call dropdown<br>2. Leave the Preferred Date input empty<br>3. Enter a valid time window in the Preferred Time Window input<br>4. Enter a valid phone number in the Phone Number input<br>5. Click the Request Callback button | Inline validation error for empty Preferred Date field | Medium |
| SUPCEN-008 | Preferred Date is not at least the next business day | None | 1. Select a valid reason from the Reason for Call dropdown<br>2. Enter a date that is today or a past date in the Preferred Date input<br>3. Enter a valid time window in the Preferred Time Window input<br>4. Enter a valid phone number in the Phone Number input<br>5. Click the Request Callback button | Inline validation error for Preferred Date not being at least the next business day | Medium |
| SUPCEN-009 | Preferred Time Window field empty | None | 1. Select a valid reason from the Reason for Call dropdown<br>2. Enter a valid date that is at least the next business day in the Preferred Date input<br>3. Leave the Preferred Time Window input empty<br>4. Enter a valid phone number in the Phone Number input<br>5. Click the Request Callback button | Inline validation error for empty Preferred Time Window field | Medium |
| SUPCEN-010 | Phone Number field empty | None | 1. Select a valid reason from the Reason for Call dropdown<br>2. Enter a valid date that is at least the next business day in the Preferred Date input<br>3. Enter a valid time window in the Preferred Time Window input<br>4. Leave the Phone Number input empty<br>5. Click the Request Callback button | Inline validation error for empty Phone Number field | Medium |
| SUPCEN-011 | Invalid Phone Number format | None | 1. Select a valid reason from the Reason for Call dropdown<br>2. Enter a valid date that is at least the next business day in the Preferred Date input<br>3. Enter a valid time window in the Preferred Time Window input<br>4. Enter an invalid phone number format in the Phone Number input<br>5. Click the Request Callback button | Inline validation error for invalid Phone Number format | Medium |

#### 🔄 Edge Case Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| SUPCEN-013 | Send secure message with maximum length subject | User is logged in and on the Send Secure Message page | 1. Enter a subject with maximum allowed characters in the Subject input<br>2. Select a category from the Category dropdown<br>3. Enter a valid message in the Message Body<br>4. Click the Send Message button | Message sent successfully with a ticket ID displayed | Low |
| SUPCEN-014 | Send secure message with maximum length message body | User is logged in and on the Send Secure Message page | 1. Enter a valid subject in the Subject input<br>2. Select a category from the Category dropdown<br>3. Enter a message with maximum allowed characters in the Message Body<br>4. Click the Send Message button | Message sent successfully with a ticket ID displayed | Low |

---

### Logout

#### ✅ Functional Tests

| TC ID | Test Case | Preconditions | Steps | Expected Result | Priority |
|-------|-----------|---------------|-------|-----------------|----------|
| LOGOUT-001 | Successful logout redirects to login page | User is logged in | 1. Click on the 'Log Out' button | User is redirected to the login page | High |
| LOGOUT-002 | Successful logout ends user session | User is logged in | 1. Click on the 'Log Out' button | User session is ended | High |
| LOGOUT-003 | Successful logout clears sensitive data | User is logged in | 1. Click on the 'Log Out' button | Sensitive data is cleared | High |
| LOGOUT-004 | Accessing protected page after logout redirects to login | User is logged out | 1. Attempt to access a protected page | User is redirected to the login page | High |

---

