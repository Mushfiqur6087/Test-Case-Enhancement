# Enriched Test Cases

**Application:** http://localhost:8080  
**TC File:** `input/parabank/Test_Cases.md`  
**Mock Data:** `input/parabank/Mock_Data.md`  

---

## Summary

| Metric | Count |
|--------|-------|
| Total Input | 50 |
| ✅ Kept | 49 |
| 🗑 Dropped | 1 |
| LLM Calls | 13 |

---

## Login

### ✅ Kept — TC-001 — Successful sign-in with valid credentials
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/login](http://localhost:8080/login) | **Requires Auth:** No

**Preconditions:** User is unauthenticated on the Login page; a registered user exists with email admin@parabank.com and password Admin123!@#  

**Steps:**
- 1. Enter 'admin@parabank.com' in Email/Username field
- 2. Enter 'Admin123!@#' in Password field
- 3. Click Sign In

**Expected Result:** Flash message "Signed in successfully." appears; user is redirected to Accounts Overview page  

**Test Data:**
- `email`: admin@parabank.com
- `password`: Admin123!@#

**Notes:** Placeholders replaced with the seeded user's credentials. No steps changed.  

---

### ✅ Kept — TC-008 — Authentication failure with unregistered credentials
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/login](http://localhost:8080/login) | **Requires Auth:** No

**Preconditions:** User is on the Login page; credentials entered are not present in the database  

**Steps:**
- 1. Enter 'ELC123456789' in Email/Username field
- 2. Enter 'GAS987654321' in Password field
- 3. Click Sign In

**Expected Result:** Page displays "Incorrect email or password. Please try again."; Password field is cleared; user stays on Login page; retry is allowed  

**Test Data:**
- `email_not_registered`: ELC123456789
- `password_meeting_policy`: GAS987654321

**Notes:** Used seeded payee account numbers (ELC123456789 and GAS987654321) as concrete credential values that are present in mock data but are not registered users, satisfying the precondition of unregistered credentials.  

---

### ✅ Kept — TC-009 — Password at exact minimum length (8 chars) succeeds
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/login](http://localhost:8080/login) | **Requires Auth:** No

**Preconditions:** A registered user exists with an 8-character password containing uppercase, lowercase, number, and special character. (If no such seeded user exists, register a test user prior to executing this case, e.g. email: eightchar@example.com, password: Abc1!def)  

**Steps:**
- 1. Enter 'eightchar@example.com' in Email/Username field
- 2. Enter 'Abc1!def' in Password field
- 3. Click Sign In

**Expected Result:** Form submits; "Signed in successfully." flash appears; redirect to Accounts Overview  

**Test Data:**
- `email`: eightchar@example.com
- `password`: Abc1!def

**Notes:** Seeded data does not include a user with an 8-character password. The precondition was updated to require creating/registering a temporary user (example provided) before running this test so the login step can validate the 8-character boundary.  

---

### ✅ Kept — TC-014 — Failed login clears Password but preserves Email/Username
**Type:** Edge/State | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/login](http://localhost:8080/login) | **Requires Auth:** No

**Preconditions:** A registered user exists; entered password will be incorrect  

**Steps:**
- 1. Enter 'admin@parabank.com' in Email/Username field
- 2. Enter 'WrongPass1!' in Password field
- 3. Click Sign In

**Expected Result:** Error "Incorrect email or password." is shown; Password field is cleared; Email/Username retains the entered value; form allows retry  

**Test Data:**
- `email`: admin@parabank.com
- `incorrect_password`: WrongPass1!

**Notes:** Placeholders replaced with the seeded user's email and a concrete incorrect password. No steps required rewriting.  

---

## Register

### ✅ Kept — TC-001 — Complete registration happy path
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/register](http://localhost:8080/register) | **Requires Auth:** No

**Preconditions:** User is not authenticated; Registration page is open  

**Steps:**
- 1. Enter 'John' in First Name, 'Doe' in Last Name, '123 Main Street' in Street Address, and 'Springfield' in City
- 2. Select 'IL' from State dropdown
- 3. Enter '62701' in ZIP (5-digit)
- 4. Enter '(555) 123-4567' in Phone
- 5. Enter '***-**-1234' in SSN
- 6. Enter 'admin@parabank.com' in Username / Email
- 7. Enter 'Admin123!@#' in Password and re-enter 'Admin123!@#' in Confirm Password
- 8. Click the Register button

**Expected Result:** "Account created successfully — please sign in" is shown; user is redirected to the Login page  

**Test Data:**
- `first_name`: John
- `last_name`: Doe
- `street_address`: 123 Main Street
- `city`: Springfield
- `state`: IL
- `zip`: 62701
- `phone`: (555) 123-4567
- `ssn`: ***-**-1234
- `username`: admin@parabank.com
- `password`: Admin123!@#
- `confirm_password`: Admin123!@#

**Notes:** Verification result: valid. All referenced UI elements exist. Post-submit success message and redirect are runtime behaviors and were not verified by the static DOM check.  

---

### ✅ Kept — TC-006 — Submit with ALL required fields empty
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/register](http://localhost:8080/register) | **Requires Auth:** No

**Preconditions:** User is on the Registration page  

**Steps:**
- 1. Leave all registration fields blank (First Name, Last Name, Street Address, City, State, ZIP, Phone, SSN, Username, Password, Confirm Password)
- 2. Click the Register button

**Expected Result:** Every required field (First Name, Last Name, Street Address, City, State, ZIP, Phone, SSN, Username, Password, Confirm Password) displays an inline "required" validation error; form does not submit; no account is created  

**Notes:** Verification result: valid. All required fields and the Register button exist on the page. The presence and content of runtime validation messages are dynamic and were not verified by the static DOM snapshot.  

---

### ✅ Kept — TC-010 — Confirm Password does not match Password
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/register](http://localhost:8080/register) | **Requires Auth:** No

**Preconditions:** User is on the Registration page  

**Steps:**
- 1. Enter 'Admin123!@#' in Password
- 2. Enter 'Admin123!@' (different value) in Confirm Password
- 3. Enter 'John' in First Name, 'Doe' in Last Name, '123 Main Street' in Street Address, 'Springfield' in City, select 'IL' for State, enter '62701' for ZIP, enter '(555) 123-4567' for Phone, and enter '***-**-1234' for SSN; enter 'admin@parabank.com' in Username
- 4. Click the Register button

**Expected Result:** Confirm Password displays inline error "must match Password"; form does not submit; account is not created  

**Test Data:**
- `password`: Admin123!@#
- `confirm_password`: Admin123!@
- `first_name`: John
- `last_name`: Doe
- `street_address`: 123 Main Street
- `city`: Springfield
- `state`: IL
- `zip`: 62701
- `phone`: (555) 123-4567
- `ssn`: ***-**-1234
- `username`: admin@parabank.com

**Notes:** Verification result: valid. All fields required for the mismatch-password negative test are present. The inline error message and submission outcome are runtime behaviors not verifiable from the static DOM snapshot.  

---

### ✅ Kept — TC-017 — 10-digit phone auto-formats to (123) 456-7890 and registration succeeds
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/register](http://localhost:8080/register) | **Requires Auth:** No

**Preconditions:** Registration page is loaded  

**Steps:**
- 1. Enter 'John' in First Name, 'Doe' in Last Name, '123 Main Street' in Street Address, and 'Springfield' in City; select 'IL' for State; enter '62701' for ZIP; enter '***-**-1234' for SSN; enter 'admin@parabank.com' in Username; enter 'Admin123!@#' in Password and Confirm Password
- 2. Enter the 10 raw digits '5551234567' (no punctuation) in Phone Number field
- 3. Observe that the Phone Number field updates/auto-formats to '(555) 123-4567'
- 4. Click the Register button

**Expected Result:** Phone Number auto-formats to '(555) 123-4567'; form submits; "Account created successfully — please sign in" is shown; redirect to Login  

**Test Data:**
- `first_name`: John
- `last_name`: Doe
- `street_address`: 123 Main Street
- `city`: Springfield
- `state`: IL
- `zip`: 62701
- `phone_raw`: 5551234567
- `phone_formatted`: (555) 123-4567
- `ssn`: ***-**-1234
- `username`: admin@parabank.com
- `password`: Admin123!@#
- `confirm_password`: Admin123!@#

**Notes:** Verification result: valid. All relevant UI elements exist. The runtime behavior of auto-formatting and the post-submit success/redirect are dynamic and were not verified by the static DOM snapshot.  

---

## Accounts Overview

### ✅ Kept — TC-003 — Account numbers are masked showing only last four digits
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/dashboard](http://localhost:8080/dashboard) | **Requires Auth:** Yes

**Preconditions:** User 'admin' is logged in; at least one account exists with known last 4 digits  

**Steps:**
- 1. Navigate to Accounts Overview
- 2. Inspect the Account Number column for each row

**Expected Result:** Each Account Number is displayed as '****5001', showing only the last 4 digits  

**Test Data:**
- `username`: admin
- `last4`: 5001
- `account_mask`: ****5001

**Notes:** Verified against seeded data: account masking present. Used Checking account last 4 digits (5001) as the concrete example for the <last4> placeholder.  

---

### ✅ Kept — TC-008 — Unauthenticated access to Accounts Overview redirects to Login
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/dashboard](http://localhost:8080/dashboard) | **Requires Auth:** No

**Preconditions:** User is not authenticated  

**Steps:**
- 1. Navigate directly to the Accounts Overview URL (http://localhost:8080/dashboard)

**Expected Result:** Access is blocked; user is redirected to the Login page; Accounts Table and Welcome message are not visible  

**Test Data:**
- `url`: http://localhost:8080/dashboard

**Notes:** DOM-check snapshot used for verification showed a logged-in state, so the redirect could not be validated from that snapshot. The test itself remains valid for an unauthenticated session; ensure the test runs with no auth context to validate the redirect.  

---

### 🗑 Dropped — TC-012 — Zero and negative Current Balance values displayed and summed correctly
**Type:** Edge/Data | **Priority:** Medium | **Verified:** ⚠️ Invalid Steps  
**URL:** [http://localhost:8080/dashboard](http://localhost:8080/dashboard) | **Requires Auth:** Yes

> 🗑 **Dropped:** Requires at least one zero-balance account which is not present in the seeded data and cannot reasonably be created via normal UI flows; test cannot be executed against current seed and is therefore dropped.

---

## Open New Account

### ✅ Kept — TC-001 — Open a Checking account at minimum deposit
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/open-account](http://localhost:8080/open-account) | **Requires Auth:** Yes

**Preconditions:** User is logged in; a funding account exists with balance ≥ $25 (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Navigate to Open New Account (http://localhost:8080/open-account)
- 2. Select Checking as Account Type
- 3. Enter 25 in Initial Deposit Amount
- 4. Select funding account ****5001 (Checking, $5,847.52) from the Funding Account dropdown
- 5. Click Open Account

**Expected Result:** "Account opened successfully!" is shown; user is redirected to Accounts Overview  

**Test Data:**
- `account_type`: Checking
- `initial_deposit`: 25
- `funding_account`: ****5001 (Checking, $5,847.52)

**Notes:** Steps use the seeded Checking account ****5001 as the funding source which has sufficient funds for the $25 minimum deposit.  

---

### ✅ Kept — TC-011 — Funding account has insufficient balance for requested deposit
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/open-account](http://localhost:8080/open-account) | **Requires Auth:** Yes

**Preconditions:** User is on the Open New Account page and signed in; funding accounts available include Savings ****5002 ($25,678.90) and Checking ****5001 ($5,847.52).  

**Steps:**
- 1. Select Checking as Account Type
- 2. Enter 30000 in Initial Deposit Amount (amount ≥ $25 but exceeding the chosen funding account's balance)
- 3. Select funding account ****5002 (Savings, $25,678.90) from the Funding Account dropdown
- 4. Click Open Account

**Expected Result:** Funding Source Account dropdown shows inline error about insufficient balance; form does not submit; no account is created  

**Test Data:**
- `account_type`: Checking
- `initial_deposit`: 30000
- `funding_account`: ****5002 (Savings, $25,678.90)

**Issues:**
- Test note: The seeded data does not include a very low positive-balance account; to reproduce an insufficient-funds error we selected Savings ****5002 and entered a deposit (30000) that exceeds its balance.

**Notes:** Chose Savings ****5002 and deposit 30000 to trigger the insufficient-balance validation against seeded balances.  

---

### ✅ Kept — TC-016 — Funding account balance exactly equals deposit amount — boundary succeeds
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ⚠️ Invalid Steps  
**URL:** [http://localhost:8080/open-account](http://localhost:8080/open-account) | **Requires Auth:** Yes

**Preconditions:** User is on the Open New Account page; a funding account with a known balance is available (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Select Checking as Account Type (meets minimum)
- 2. Enter Initial Deposit Amount = 5847.52
- 3. Select funding account ****5001 (Checking, $5,847.52) from the Funding Account dropdown
- 4. Click Open Account

**Expected Result:** Form submits; "Account opened successfully!" is shown; redirect to Accounts Overview  

**Test Data:**
- `account_type`: Checking
- `initial_deposit`: 5847.52
- `funding_account`: ****5001 (Checking, $5,847.52)

**Issues:**
- Original step 3 required selecting a funding account with balance = X; verification found no generic X-match in the DOM. Available funding accounts have known balances ($5,847.52 and $25,678.90).

**Notes:** Rewrote steps to set X to a real seeded balance (5847.52) and to select the matching funding account ****5001. The verification result was 'invalid_steps' because the original abstract step asked for an account with balance = X that did not match actual options; steps were updated to use an explicit seeded balance so the step is executable.  

---

### ✅ Kept — TC-018 — Switching Account Type invalidates a previously valid deposit amount
**Type:** Edge/Interaction | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/open-account](http://localhost:8080/open-account) | **Requires Auth:** Yes

**Preconditions:** User is on Open New Account; a funding account with balance ≥ $25 is available (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Select Checking as Account Type
- 2. Enter 25 in Initial Deposit Amount (Checking minimum)
- 3. Select funding account ****5001 (Checking, $5,847.52) from the Funding Account dropdown
- 4. Change Account Type to Savings without altering the Initial Deposit Amount

**Expected Result:** Real-time validation triggers; Initial Deposit Amount shows inline error that the amount is below the $100 Savings minimum; submission is blocked  

**Test Data:**
- `initial_account_type`: Checking
- `changed_account_type`: Savings
- `initial_deposit`: 25
- `funding_account`: ****5001 (Checking, $5,847.52)
- `savings_minimum`: 100

**Notes:** Uses seeded Checking ****5001 as funding source and verifies real-time validation when switching to Savings with an unchanged $25 deposit (below the $100 Savings minimum).  

---

## Transfer Funds

### ✅ Kept — TC-002 — External transfer with matching account numbers succeeds
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/transfer](http://localhost:8080/transfer) | **Requires Auth:** Yes

**Preconditions:** User is logged in; source account has sufficient funds (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Navigate to Transfer Funds
- 2. Select External Account
- 3. Enter 500.00 in Amount field
- 4. Select ****5001 (Checking, $5,847.52) as the source account
- 5. Enter ELC123456789 in External Account Number field
- 6. Enter ELC123456789 in Confirm External Account Number field
- 7. Click Transfer

**Expected Result:** "Transfer completed successfully." with a transaction ID is displayed  

**Test Data:**
- `amount`: 500.00
- `source_account`: ****5001 (Checking, $5,847.52)
- `external_account_number`: ELC123456789
- `confirm_external_account_number`: ELC123456789

**Notes:** External Account Number and Confirm fields are conditional and may appear only after selecting the External Account radio; the verification snapshot noted the trigger exists but those fields were not present in the static DOM. Steps use the seeded external account number ELC123456789.  

---

### ✅ Kept — TC-009 — Transfer amount exceeds available balance
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/transfer](http://localhost:8080/transfer) | **Requires Auth:** Yes

**Preconditions:** User is logged in; source account has a known balance (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Select My ParaBank Account
- 2. Enter 6000.00 in Amount field (exceeds source account balance of $5,847.52)
- 3. Select ****5001 (Checking, $5,847.52) as the source account
- 4. Select ****5002 (Savings, $25,678.90) as the destination account
- 5. Click Transfer

**Expected Result:** Page displays "Insufficient funds"; form does not submit; no transaction is created  

**Test Data:**
- `amount`: 6000.00
- `source_account`: ****5001 (Checking, $5,847.52)
- `destination_account`: ****5002 (Savings, $25,678.90)

**Notes:** No DOM changes required. This negative outcome is a backend/runtime validation and cannot be observed from the static snapshot; test uses an amount larger than the seeded checking balance to trigger the insufficient-funds response.  

---

### ✅ Kept — TC-011 — External account number and confirmation do not match
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/transfer](http://localhost:8080/transfer) | **Requires Auth:** Yes

**Preconditions:** User is on Transfer Funds page and logged in.  

**Steps:**
- 1. Select External Account
- 2. Enter 100.00 in Amount field and select ****5001 (Checking, $5,847.52) as the source account
- 3. Enter ELC123456789 in External Account Number field
- 4. Enter GAS987654321 in Confirm External Account Number field
- 5. Click Transfer

**Expected Result:** Error "Account numbers do not match." is displayed; form does not submit; no transaction is created  

**Test Data:**
- `amount`: 100.00
- `source_account`: ****5001 (Checking, $5,847.52)
- `external_account_number_A`: ELC123456789
- `external_account_number_B`: GAS987654321

**Notes:** External Account Number and Confirm fields are conditional; verification snapshot confirmed the External Account radio exists but these fields were not visible in the static DOM. Steps use two different seeded external account numbers to trigger the mismatch validation.  

---

### ✅ Kept — TC-012 — Transfer amount exactly equals available balance succeeds
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/transfer](http://localhost:8080/transfer) | **Requires Auth:** Yes

**Preconditions:** User is logged in; source account has a known available balance (Checking ****5001, $5,847.52); a different destination account exists (Savings ****5002).  

**Steps:**
- 1. Select My ParaBank Account
- 2. Select ****5001 (Checking, $5,847.52) as the source account
- 3. Select ****5002 (Savings, $25,678.90) as the destination account
- 4. Enter 5847.52 in Amount field (the exact available balance of the source account)
- 5. Click Transfer

**Expected Result:** "Transfer completed successfully." with a transaction ID; source account balance reduced to zero  

**Test Data:**
- `amount`: 5847.52
- `source_account`: ****5001 (Checking, $5,847.52)
- `destination_account`: ****5002 (Savings, $25,678.90)

**Notes:** No DOM rewrites needed. Verifying the post-submit balance change and success message requires runtime execution; steps use the exact seeded checking balance to exercise the boundary condition.  

---

### ✅ Kept — TC-018 — Browser Back after successful transfer does not create a duplicate
**Type:** Edge/Interaction | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/transfer](http://localhost:8080/transfer) | **Requires Auth:** Yes

**Preconditions:** User is logged in; source account has at least 2× the transfer amount available (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Complete a successful transfer of 2000.00 from ****5001 (Checking, $5,847.52) to ****5002 (Savings, $25,678.90); note the displayed transaction ID
- 2. Press browser Back
- 3. Click Transfer again without changing inputs

**Expected Result:** Second submission is blocked; only one transaction ID exists in history; no duplicate transfer occurs  

**Test Data:**
- `initial_transfer_amount`: 2000.00
- `source_account`: ****5001 (Checking, $5,847.52)
- `destination_account`: ****5002 (Savings, $25,678.90)

**Notes:** This interaction (browser Back and duplicate-submission protection) cannot be fully validated from the static DOM snapshot. The test uses a 2000.00 transfer amount which is <= half the seeded checking balance to satisfy the precondition (source has at least 2× the transfer amount).  

---

## Payments

### ✅ Kept — TC-001 — Submit bill payment happy path
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/bill-pay](http://localhost:8080/bill-pay) | **Requires Auth:** Yes

**Preconditions:** User is logged in; source account has funds ≥ payment amount (use Checking ****5001 with $5,847.52).  

**Steps:**
- 1. Navigate to Bill Payment
- 2. Fill in Payee Name: 'Electric Company'
- 3. Fill in Street Address: '456 Power Street'
- 4. Fill in City: 'Springfield'
- 5. Select State: 'IL'
- 6. Fill in ZIP: '62701'
- 7. Fill in Phone: '(555) 987-6543'
- 8. Enter 'ELC123456789' in Payee Account Number
- 9. Enter 'ELC123456789' in Confirm Account Number
- 10. Enter Payment Amount: '100.00'
- 11. Select source account: '****5001 (Checking, $5,847.52)'
- 12. Click Pay

**Expected Result:** "Payment submitted successfully." with a reference code is shown; source account balance updates to reflect the debit (Checking ****5001 decreases by $100.00)  

**Test Data:**
- `payee_name`: Electric Company
- `street`: 456 Power Street
- `city`: Springfield
- `state`: IL
- `zip`: 62701
- `phone`: (555) 987-6543
- `payee_account`: ELC123456789
- `payment_amount`: 100.00
- `source_account`: ****5001 (Checking, $5,847.52)

**Notes:** Replaced placeholders with seeded payee 'Electric Company' (ELC123456789) and used Checking ****5001 with balance $5,847.52 as the source account. Payment amount chosen as $100.00 to satisfy '≥ payment amount' precondition.  

---

### ✅ Kept — TC-008 — Payee account number and confirmation do not match
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/bill-pay](http://localhost:8080/bill-pay) | **Requires Auth:** Yes

**Preconditions:** User is logged in; all other required fields are filled with valid values except the account confirmation which will be intentionally different.  

**Steps:**
- 1. Navigate to Bill Payment
- 2. Enter 'ELC123456789' in Payee Account Number
- 3. Enter 'GAS987654321' in Confirm Account Number
- 4. Click Pay

**Expected Result:** Inline error "Account numbers do not match" is shown; form does not submit; no payment is created  

**Test Data:**
- `payee_account_A`: ELC123456789
- `payee_account_B`: GAS987654321

**Notes:** Replaced <account number A> and <different account number B> with seeded payee account numbers ELC123456789 and GAS987654321 respectively. Assumes all other fields were pre-filled per precondition.  

---

### ✅ Kept — TC-009 — Insufficient funds in selected source account
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/bill-pay](http://localhost:8080/bill-pay) | **Requires Auth:** Yes

**Preconditions:** User is logged in; selected source account balance is less than the entered payment amount.  

**Steps:**
- 1. Navigate to Bill Payment
- 2. Select the source account '****5001 (Checking, $5,847.52)'
- 3. Enter Payment Amount: '10000.00'
- 4. Click Pay

**Expected Result:** Inline error "Insufficient funds" is shown; form does not submit; no payment is created; balances unchanged  

**Test Data:**
- `source_account`: ****5001 (Checking, $5,847.52)
- `payment_amount`: 10000.00

**Notes:** Selected Checking ****5001 (balance $5,847.52) and used a payment amount $10,000.00 to trigger the insufficient funds condition.  

---

### ✅ Kept — TC-012 — Payment amount exactly equals available funds succeeds
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/bill-pay](http://localhost:8080/bill-pay) | **Requires Auth:** Yes

**Preconditions:** User is logged in; a source account exists with available funds exactly equal to the intended payment amount (Checking ****5001 has $5,847.52).  

**Steps:**
- 1. Navigate to Bill Payment
- 2. Enter Payment Amount: '5847.52' (exact available balance of the source account)
- 3. Select source account: '****5001 (Checking, $5,847.52)'
- 4. Click Pay

**Expected Result:** "Payment submitted successfully." with a reference code is shown; source account balance becomes zero; payment appears in transaction history  

**Test Data:**
- `payment_amount`: 5847.52
- `source_account`: ****5001 (Checking, $5,847.52)

**Notes:** Used seeded Checking account ****5001 with exact balance 5,847.52 to perform the boundary test where payment equals available funds.  

---

### ✅ Kept — TC-016 — Browser Back after successful payment does not create duplicate
**Type:** Edge/Interaction | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/bill-pay](http://localhost:8080/bill-pay) | **Requires Auth:** Yes

**Preconditions:** User is logged in; source account has at least 2× the payment amount available (Savings ****5002 has $25,678.90).  

**Steps:**
- 1. Navigate to Bill Payment
- 2. Fill in Payee Name: 'Internet Provider'
- 3. Enter Payee Account Number: 'INT555444333' and Confirm Account Number: 'INT555444333'
- 4. Enter Payment Amount: '10000.00'
- 5. Select source account: '****5002 (Savings, $25,678.90)'
- 6. Click Pay
- 7. Confirm success message and record the reference code shown
- 8. Press browser Back
- 9. On the returned form, click Pay again

**Expected Result:** Second submission is blocked; only one payment appears in transaction history; account balance reflects a single deduction  

**Test Data:**
- `payee_name`: Internet Provider
- `payee_account`: INT555444333
- `payment_amount`: 10000.00
- `source_account`: ****5002 (Savings, $25,678.90)

**Notes:** Used seeded Savings ****5002 (balance $25,678.90) and payee 'Internet Provider' (INT555444333). Payment amount $10,000.00 is less than half the savings balance, meeting the 2× requirement in precondition.  

---

## Request Loan

### ✅ Kept — TC-002 — Request Auto Loan with collateral and approval (Positive | High)
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/loan](http://localhost:8080/loan) | **Requires Auth:** Yes

**Preconditions:** Credit engine configured for approval; use collateral account ****5002 (Savings, $25,678.90) which is ≥ 20% of the requested loan amount.  

**Steps:**
- 1. Navigate to Request Loan
- 2. Select 'Auto' as Loan Type
- 3. Enter '15000' in Loan Amount
- 4. Enter '2000' in Down Payment
- 5. Select collateral account '****5002 (Savings, $25,678.90)'
- 6. Click 'Request Loan'

**Expected Result:** "Loan approved and created successfully!" with account details; Loan Details panel shows Loan Type, Amount, Down Payment, and Collateral Account  

**Test Data:**
- `loan_type`: Auto
- `loan_amount`: 15000
- `down_payment`: 2000
- `collateral_account`: ****5002 (Savings, $25,678.90)

**Notes:** UI elements referenced by the steps were confirmed present in the DOM. External preconditions (credit engine behavior and final approval) are not verifiable from the page snapshot; test assumes the credit engine is configured for approval as stated in the preconditions.  

---

### ✅ Kept — TC-007 — Loan amount below type-specific minimum is rejected (Negative | High)
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/loan](http://localhost:8080/loan) | **Requires Auth:** Yes

**Preconditions:** User is on the Request Loan page.  

**Steps:**
- 1. Select 'Personal' as Loan Type
- 2. Enter '500' in Loan Amount
- 3. Enter '50' in Down Payment
- 4. Click 'Request Loan'

**Expected Result:** Inline error on Loan Amount: "must be between 1000 and 50000"; form does not submit; no loan is created  

**Test Data:**
- `loan_type`: Personal
- `loan_amount`: 500
- `down_payment`: 50

**Notes:** All referenced controls (loan type, loan amount, down payment, submit) are present per DOM verification. The numeric validation outcome is runtime behavior.  

---

### ✅ Kept — TC-010 — Down payment below 10 of loan amount is rejected (Negative | High)
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/loan](http://localhost:8080/loan) | **Requires Auth:** Yes

**Preconditions:** User is on the Request Loan page; Loan Type is selected.  

**Steps:**
- 1. Enter '10000' in Loan Amount
- 2. Enter '500' in Down Payment
- 3. Click 'Request Loan'

**Expected Result:** Inline error on Down Payment: "must be ≥ 10% of Loan Amount"; form does not submit; no loan is created  

**Test Data:**
- `loan_amount`: 10000
- `down_payment`: 500
- `loan_type`: Auto

**Notes:** Controls required to perform this test are present per DOM verification. The precondition that a loan type is already selected is retained; test_data indicates 'Auto' as the selected type if needed.  

---

### ✅ Kept — TC-017 — Down payment exactly equals 10 of loan amount passes validation (Edge/Boundary | Medium)
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/loan](http://localhost:8080/loan) | **Requires Auth:** Yes

**Preconditions:** User is on the Request Loan page.  

**Steps:**
- 1. Select 'Home' as Loan Type
- 2. Enter '100000' in Loan Amount
- 3. Enter '10000' in Down Payment
- 4. Click 'Request Loan'

**Expected Result:** No validation error on Down Payment; form proceeds to credit engine evaluation  

**Test Data:**
- `loan_type`: Home
- `loan_amount`: 100000
- `down_payment`: 10000

**Notes:** All referenced UI controls exist per DOM verification. The check that exact 10% passes validation is runtime logic and should be asserted by the test harness.  

---

### ✅ Kept — TC-021 — Collateral account balance one unit below 20 of loan amount is blocked (Edge/Boundary | Medium)
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/loan](http://localhost:8080/loan) | **Requires Auth:** Yes

**Preconditions:** A collateral account exists whose balance is exactly one unit ($1.00) below 20% of the entered loan amount. Using account ****5002 (Savings, $25,678.90) which is $1.00 less than 20% of 128,399.50 (20% = $25,679.90).  

**Steps:**
- 1. Select 'Auto' as Loan Type
- 2. Enter '128399.50' in Loan Amount
- 3. Enter '10000' in Down Payment
- 4. Select the under-collateralised account '****5002 (Savings, $25,678.90)'
- 5. Click 'Request Loan'

**Expected Result:** Inline error on Collateral Account: insufficient balance (< 20% of Loan Amount); request is not sent to the credit engine  

**Test Data:**
- `loan_type`: Auto
- `loan_amount`: 128399.50
- `down_payment`: 10000
- `collateral_account`: ****5002 (Savings, $25,678.90)

**Notes:** All referenced UI elements are present per DOM verification. The precondition that an account sits exactly $1.00 below the 20% threshold is satisfied by constructing the loan amount so 20% equals $25,679.90 while the seeded savings balance is $25,678.90.  

---

## Update Contact Info

### ✅ Kept — TC-004 — Update First and Last Name and save successfully
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/profile](http://localhost:8080/profile) | **Requires Auth:** Yes

**Preconditions:** User is logged in and on the Customer Profile page  

**Steps:**
- 1. Enter 'John' in First Name
- 2. Enter 'Doe' in Last Name
- 3. Click Update Profile

**Expected Result:** "Profile updated successfully." is shown; form displays the new First Name and Last Name values  

**Test Data:**
- `first_name`: John
- `last_name`: Doe

**Notes:** Verification: All interactive controls referenced by the steps exist on the Profile page. The post-submit success message is dynamic and was not inspected by the static DOM check.  

---

### ✅ Kept — TC-005 — Leave required field (First Name) blank and submit
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/profile](http://localhost:8080/profile) | **Requires Auth:** Yes

**Preconditions:** Form is pre-filled; user is authenticated  

**Steps:**
- 1. Clear the First Name field
- 2. Leave all other fields unchanged
- 3. Click Update Profile

**Expected Result:** Inline error on First Name: "required"; form does not submit; "Profile updated successfully." is not shown  

**Test Data:**
- `first_name_original`: John

**Notes:** Verification: Required-field negative test references existing inputs and submit button. Inline error behavior is dynamic and was not verifiable from the static DOM.  

---

### ✅ Kept — TC-007 — Invalid phone number format
**Type:** Negative | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/profile](http://localhost:8080/profile) | **Requires Auth:** Yes

**Preconditions:** Form is pre-filled; user is authenticated  

**Steps:**
- 1. Replace Phone Number with '(555) 987-6543'
- 2. Click Update Profile

**Expected Result:** Phone Number field highlights with inline error about invalid format; form does not submit; profile is not updated  

**Test Data:**
- `phone`: (555) 987-6543

**Notes:** Verification: Phone number field and submit button exist on the page. Format validation and error highlighting are runtime behaviors and were not checked by the static DOM scan.  

---

### ✅ Kept — TC-012 — Entering only whitespace into Last Name is treated as missing
**Type:** Edge/Input | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/profile](http://localhost:8080/profile) | **Requires Auth:** Yes

**Preconditions:** User is on the Customer Profile page with the form pre-filled  

**Steps:**
- 1. Clear Last Name and enter only whitespace characters
- 2. Click Update Profile

**Expected Result:** Submission is blocked; Last Name is highlighted with inline error indicating the field must be present (whitespace-only counts as empty)  

**Test Data:**
- `last_name_whitespace`:    

**Notes:** Verification: Last Name input and submit button exist. Enforcement of whitespace-as-empty is server/client validation and not visible in the static DOM check.  

---

## Manage Cards

### ✅ Kept — TC-001 — Submit card request with complete address and account in good standing (Positive | High)
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/cards](http://localhost:8080/cards) | **Requires Auth:** Yes

**Preconditions:** User is logged in; an account in good standing is available (Checking ****5001, $5,847.52).  

**Steps:**
- 1. Select 'Debit' as Card Type
- 2. Select account '****5001 (Checking, $5,847.52)' from Account to Link
- 3. Enter '123 Main Street' in Shipping Address line 1
- 4. Enter 'Springfield' in City
- 5. Enter 'IL' in State
- 6. Enter '62701' in Zip Code
- 7. Enter '(555) 123-4567' in Phone
- 8. Click Request Card

**Expected Result:** "Card request submitted successfully." is shown with a visible tracking ID  

**Test Data:**
- `card_type`: Debit
- `account`: ****5001 (Checking, $5,847.52)
- `shipping_address_line1`: 123 Main Street
- `city`: Springfield
- `state`: IL
- `zip`: 62701
- `phone`: (555) 123-4567

**Notes:** Placeholders filled with seeded user and account data. No step rewrites required; UI elements for card request were confirmed present.  

---

### ✅ Kept — TC-008 — Selected account is not in good standing (Negative | High)
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/cards](http://localhost:8080/cards) | **Requires Auth:** Yes

**Preconditions:** User is logged in; an account that is NOT in good standing exists and is selectable (Credit Card ****5003, balance -$1,534.67).  

**Steps:**
- 1. Select 'Debit' as Card Type
- 2. Select account '****5003 (Credit Card, -$1,534.67)' from Account to Link
- 3. Enter '123 Main Street' in Shipping Address line 1
- 4. Enter 'Springfield' in City
- 5. Enter 'IL' in State
- 6. Enter '62701' in Zip Code
- 7. Enter '(555) 123-4567' in Phone
- 8. Click Request Card

**Expected Result:** Inline error "selected account must be in good standing" is shown; Request Card does not submit; no ticket is created  

**Test Data:**
- `card_type`: Debit
- `account`: ****5003 (Credit Card, -$1,534.67)
- `shipping_address_line1`: 123 Main Street
- `city`: Springfield
- `state`: IL
- `zip`: 62701
- `phone`: (555) 123-4567

**Notes:** Used seeded negative-balance account (ID 12345003, ****5003) to satisfy the precondition. No UI step changes were needed; elements exist per verification.  

---

### ✅ Kept — TC-010 — Travel Notice with Start Date after End Date is rejected (Negative | Medium)
**Type:** Negative | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/cards](http://localhost:8080/cards) | **Requires Auth:** Yes

**Preconditions:** User is logged in; an existing card is selected in Card Controls (card ending 5001).  

**Steps:**
- 1. Select card ending '5001' in Card Controls
- 2. Click Add Travel Notice
- 3. Enter '2024-06-10' in Start Date (a date later than End Date)
- 4. Enter '2024-06-05' in End Date
- 5. Click Update Controls

**Expected Result:** Inline error "Start_Date ≤ End_Date when both provided" is shown; Update Controls does not submit; travel notice is not saved  

**Test Data:**
- `card_last4`: 5001
- `start_date`: 2024-06-10
- `end_date`: 2024-06-05

**Notes:** Used card ending 5001 from seeded cards. Dates chosen to produce Start_Date > End_Date; UI elements required were confirmed present in verification.  

---

### ✅ Kept — TC-014 — Travel Notice where Start Date equals End Date is accepted (Edge/Boundary | Medium)
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/cards](http://localhost:8080/cards) | **Requires Auth:** Yes

**Preconditions:** User is logged in; an existing card is selected in Card Controls (card ending 5001).  

**Steps:**
- 1. Select card ending '5001' in Card Controls
- 2. Click Add Travel Notice
- 3. Enter '2024-06-10' in Start Date
- 4. Enter '2024-06-10' in End Date
- 5. Click Update Controls

**Expected Result:** "Card controls updated successfully." is shown; travel notice entry reflects Start Date = End Date = 2024-06-10  

**Test Data:**
- `card_last4`: 5001
- `date`: 2024-06-10

**Notes:** Used card ending 5001. Chose identical Start and End dates (2024-06-10) to test boundary acceptance; UI elements present per verification.  

---

## Investments

### ✅ Kept — TC-001 — Execute Buy trade with sufficient buying power
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/investments](http://localhost:8080/investments) | **Requires Auth:** Yes

**Preconditions:** User is logged in as admin; funding account ****5001 (Checking) has sufficient buying power to cover the trade  

**Steps:**
- 1. Enter 'admin@parabank.com' in Email/Username field
- 2. Enter 'Admin123!@#' in Password field
- 3. Click Sign In
- 4. Navigate to Investments
- 5. Select 'Buy' from Action
- 6. Enter 'VTSAX' in Fund Symbol and select 'Vanguard Total Stock Market Index' from autocomplete
- 7. Enter '10' in Quantity field
- 8. Select funding account '****5001 (Checking, $5,847.52)'
- 9. Click Execute Trade

**Expected Result:** "Trade executed successfully." is displayed with an order ID; Portfolio Snapshot reflects the updated holding for VTSAX (quantity increased by 10 and market value increased accordingly).  

**Test Data:**
- `email`: admin@parabank.com
- `password`: Admin123!@#
- `fund_symbol`: VTSAX
- `fund_name`: Vanguard Total Stock Market Index
- `quantity`: 10
- `funding_account`: ****5001 (Checking, $5,847.52)

**Notes:** Placeholders replaced with seeded user and account/fund data. No step rewrites were required; verification indicated all UI elements exist.  

---

### ✅ Kept — TC-013 — Sell with quantity exceeding share balance is blocked
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/investments](http://localhost:8080/investments) | **Requires Auth:** Yes

**Preconditions:** User is logged in as admin; user's current holdings are known (VTIAX = 75.0 shares, VTSAX = 150.5 shares)  

**Steps:**
- 1. Enter 'admin@parabank.com' in Email/Username field
- 2. Enter 'Admin123!@#' in Password field
- 3. Click Sign In
- 4. Navigate to Investments
- 5. Select 'Sell' from Action
- 6. Enter 'VTIAX' in Fund Symbol and select 'Vanguard Total International Stock Index' from autocomplete
- 7. Enter '100' in Quantity field (greater than current holding of 75.0 shares)
- 8. Select destination account '****5001 (Checking, $5,847.52)'
- 9. Click Execute Trade

**Expected Result:** Inline error indicating insufficient share balance for the Sell (e.g. "Insufficient shares to complete this sale"); form does not submit; holdings remain unchanged.  

**Test Data:**
- `email`: admin@parabank.com
- `password`: Admin123!@#
- `fund_symbol`: VTIAX
- `fund_name`: Vanguard Total International Stock Index
- `quantity`: 100
- `destination_account`: ****5001 (Checking, $5,847.52)

**Notes:** Placeholders replaced with seeded user, holding and account values. No step rewrites were required; verification indicated necessary UI controls are present.  

---

### ✅ Kept — TC-014 — Recurring plan with Start Date in the past is rejected
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/investments](http://localhost:8080/investments) | **Requires Auth:** Yes

**Preconditions:** User is logged in as admin; Recurring Investment Plan form is visible on Investments page  

**Steps:**
- 1. Enter 'admin@parabank.com' in Email/Username field
- 2. Enter 'Admin123!@#' in Password field
- 3. Click Sign In
- 4. Navigate to Investments
- 5. In the Recurring Investment Plan form, enter 'VBTLX' in Fund Symbol and select 'Vanguard Total Bond Market Index' from autocomplete
- 6. Enter '100' in Contribution Amount field
- 7. Select 'Monthly' as Frequency
- 8. Enter '2024-01-01' in Start Date (a past date)
- 9. Select funding account '****5002 (Savings, $25,678.90)'
- 10. Click Create Plan

**Expected Result:** Inline error shown on Start Date field: "Start date must be in the future"; plan is not created and no recurring_plan record is added.  

**Test Data:**
- `email`: admin@parabank.com
- `password`: Admin123!@#
- `fund_symbol`: VBTLX
- `fund_name`: Vanguard Total Bond Market Index
- `contribution_amount`: 100
- `frequency`: Monthly
- `start_date`: 2024-01-01
- `funding_account`: ****5002 (Savings, $25,678.90)

**Notes:** Placeholders filled from seeded data. Verification showed the recurring plan form elements exist; no DOM-based step changes required.  

---

### ✅ Kept — TC-023 — Buy trade with funding account having exactly sufficient buying power succeeds
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/investments](http://localhost:8080/investments) | **Requires Auth:** Yes

**Preconditions:** User is logged in as admin; test will select a quantity such that total cost equals the chosen funding account's available buying power  

**Steps:**
- 1. Enter 'admin@parabank.com' in Email/Username field
- 2. Enter 'Admin123!@#' in Password field
- 3. Click Sign In
- 4. Navigate to Investments
- 5. Select 'Buy' from Action
- 6. Enter 'VTSAX' in Fund Symbol and select 'Vanguard Total Stock Market Index' from autocomplete
- 7. Enter '52.0010673' in Quantity field (quantity calculated so total cost equals $5,847.52)
- 8. Select funding account '****5001 (Checking, $5,847.52)'
- 9. Click Execute Trade

**Expected Result:** "Trade executed successfully." is displayed with an order ID; holdings update accordingly (the buy depletes the funding account buying power to zero and the portfolio reflects the added shares).  

**Test Data:**
- `email`: admin@parabank.com
- `password`: Admin123!@#
- `fund_symbol`: VTSAX
- `fund_name`: Vanguard Total Stock Market Index
- `quantity`: 52.0010673
- `funding_account`: ****5001 (Checking, $5,847.52)
- `computed_total_cost`: 5847.52
- `price_per_share`: 112.45

**Notes:** Placeholders replaced using seeded fund prices and account balances. Quantity was computed (5847.52 / 112.45 ≈ 52.0010673) to make total cost equal the funding account balance; verification shows required UI elements exist.  

---

## Account Statements

### ✅ Kept — TC-002 — Generate statement for a custom date range (Positive | High)
**Type:** Positive | **Priority:** High | **Verified:** ⚠️ Invalid Steps  
**URL:** [http://localhost:8080/statements](http://localhost:8080/statements) | **Requires Auth:** Yes

**Preconditions:** User is logged in; Account Statements page is open  

**Steps:**
- 1. Enter '2024-01-11' in Start Date field
- 2. Enter '2024-01-14' in End Date field
- 3. Select account '****5001 (Checking, $5,847.52)' from Account selector
- 4. Click 'Generate Statement'

**Expected Result:** Transactions table shows only transactions within the date range; "Statement generated successfully." is shown  

**Test Data:**
- `start_date`: 2024-01-11
- `end_date`: 2024-01-14
- `account`: ****5001 (Checking, $5,847.52)

**Notes:** Step 1 originally instructed to 'Select Custom date range' from a Statement Period control. The DOM does not contain any Statement Period selector or a 'Custom date range' option — only Start Date and End Date inputs exist. Rewrote the step to enter the Start Date directly into the Start Date field. Other steps unchanged.  

---

### ✅ Kept — TC-007 — Custom date range with Start Date after End Date is rejected (Negative | High)
**Type:** Negative | **Priority:** High | **Verified:** ⚠️ Invalid Steps  
**URL:** [http://localhost:8080/statements](http://localhost:8080/statements) | **Requires Auth:** Yes

**Preconditions:** User is logged in; Account Statements page is open  

**Steps:**
- 1. Enter '2024-01-15' in Start Date field (a date after the End Date)
- 2. Enter '2024-01-10' in End Date field
- 3. Select account '****5001 (Checking, $5,847.52)' from Account selector
- 4. Click 'Generate Statement'

**Expected Result:** Inline error on Start Date and/or End Date: "Start_Date must be on or before End_Date"; no statement is generated  

**Test Data:**
- `start_date`: 2024-01-15
- `end_date`: 2024-01-10
- `account`: ****5001 (Checking, $5,847.52)

**Notes:** Step 1 previously required selecting a 'Custom date range' option that does not exist in the DOM. Replaced that action with directly entering the Start Date into the Start Date input so the test matches the live page structure. Other steps unchanged.  

---

### ✅ Kept — TC-011 — Custom range where Start Date equals End Date is accepted (Edge/Boundary | Medium)
**Type:** Edge/Boundary | **Priority:** Medium | **Verified:** ⚠️ Invalid Steps  
**URL:** [http://localhost:8080/statements](http://localhost:8080/statements) | **Requires Auth:** Yes

**Preconditions:** User is logged in; Account Statements page is open  

**Steps:**
- 1. Enter '2024-01-13' in Start Date field
- 2. Enter '2024-01-13' in End Date field
- 3. Select account '****5001 (Checking, $5,847.52)' from Account selector
- 4. Click 'Generate Statement'

**Expected Result:** "Statement generated successfully." is shown; transactions for that single day are retrieved and displayed  

**Test Data:**
- `start_date`: 2024-01-13
- `end_date`: 2024-01-13
- `account`: ****5001 (Checking, $5,847.52)

**Notes:** Step 1 originally instructed to 'Select Custom date range' which is not present in the DOM. Adjusted the step to directly fill the Start Date field (and kept the rest of the steps unchanged) so the test matches the actual page elements.  

---

## Security Settings

### ✅ Kept — TC-001 — Change password with valid current password and strong new password
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/security](http://localhost:8080/security) | **Requires Auth:** Yes

**Preconditions:** User 'admin' is logged in and the Security Settings page is open. The user's current password is known.  

**Steps:**
- 1. Expand the Change Password panel
- 2. Enter 'Admin123!@#' in Current Password
- 3. Enter 'Admin123!@#' in New Password (meets policy)
- 4. Enter 'Admin123!@#' in Confirm New Password
- 5. Click Change Password

**Expected Result:** "Password changed successfully." success notification is displayed  

**Test Data:**
- `username`: admin
- `current_password`: Admin123!@#
- `new_password`: Admin123!@#

**Notes:** Placeholders were replaced with seeded mock data. Both current and new password values use the seeded plaintext password 'Admin123!@#' (the mock dataset contains only this explicit password). Verification run indicated all required UI elements are present; the post-submit notification is a runtime outcome and not validated by the static DOM-check.  

---

### ✅ Kept — TC-006 — Incorrect current password prevents password change
**Type:** Negative | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/security](http://localhost:8080/security) | **Requires Auth:** Yes

**Preconditions:** User 'admin' is logged in and the Security Settings page is open.  

**Steps:**
- 1. Enter 'admin' in Current Password
- 2. Enter 'Admin123!@#' in New Password (meets policy)
- 3. Enter 'Admin123!@#' in Confirm New Password
- 4. Click Change Password

**Expected Result:** Inline error on Current Password: "current password is incorrect"; form does not submit; credentials are not updated  

**Test Data:**
- `username`: admin
- `incorrect_current_password`: admin
- `new_password`: Admin123!@#

**Notes:** Replaced placeholders with mock-data values. Used the seeded username 'admin' as an incorrect current-password value to ensure the input is a concrete value from the mock dataset. Verification run confirmed the required inputs and button exist on the page; the inline error is a runtime behavior.  

---

### ✅ Kept — TC-010 — Browser Back after successful password change blocks resubmission with old password
**Type:** Edge/Interaction | **Priority:** Medium | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/security](http://localhost:8080/security) | **Requires Auth:** Yes

**Preconditions:** User 'admin' has just successfully changed their password on the Security Settings page (change completed as part of a prior step using the seeded password values).  

**Steps:**
- 1. After "Password changed successfully." is shown, press browser Back
- 2. Without changing any fields (Current Password still contains the old password), click Change Password again

**Expected Result:** Second submission is blocked; Current Password field shows verification error (old password is now incorrect); no further credential change occurs  

**Test Data:**
- `username`: admin
- `old_password`: Admin123!@#
- `new_password`: Admin123!@#

**Notes:** No placeholders in steps required substitution beyond using seeded password values for test_data. The test assumes the prior successful change used the seeded password value(s). The verification run confirmed the presence of the Current Password input and Change Password button; runtime browser-back behavior and subsequent verification are not validated by the static DOM-check.  

---

## Support Center

### ✅ Kept — TC-001 — Send secure message with required Message Body only
**Type:** Positive | **Priority:** High | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/support](http://localhost:8080/support) | **Requires Auth:** Yes

**Preconditions:** User is logged in; Support Center page is open  

**Steps:**
- 1. Enter 'Please provide a statement for account ****5001.' in Message Body
- 2. Click Send Message

**Expected Result:** 'Message sent successfully.' with a visible ticket ID is shown  

**Test Data:**
- `message_body`: Please provide a statement for account ****5001.

**Notes:** No step changes required. Message body uses the seeded masked account number ****5001 to make the message concrete.  

---

### ✅ Kept — TC-016 — Attachment with double extension (allowed/disallowed) is blocked
**Type:** Edge/Input | **Priority:** Low | **Verified:** ✅ Valid  
**URL:** [http://localhost:8080/support](http://localhost:8080/support) | **Requires Auth:** Yes

**Preconditions:** User is on the Support Center page; Secure Message form is visible  

**Steps:**
- 1. Enter 'Attachment validation - ****5001' in Subject and enter 'Testing double extension attachment for account ****5001.' in Message Body
- 2. Select a file named 'document.pdf.exe' using the Attachment control
- 3. Click Send Message

**Expected Result:** Submission is blocked; Attachment control displays inline error that the file type is not allowed; no ticket is created  

**Test Data:**
- `subject`: Attachment validation - ****5001
- `message_body`: Testing double extension attachment for account ****5001.
- `attachment_filename`: document.pdf.exe

**Notes:** No DOM-driven step changes required. Subject and message body were made concrete using the seeded masked account ****5001. The file-rejection behavior is a post-submit validation and cannot be asserted via static DOM alone (as noted in verification).  

---
