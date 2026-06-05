# Spec Verification Report

| | |
|---|---|
| **URL** | http://localhost:8080 |
| **Spec file** | `datasets/parabank/Parabank.md` |
| **Date** | 2026-06-05 |
| **Overall score** | **89 / 100** |

## Summary

| Verdict | Count |
|---------|-------|
| ✅ Pass    | 12 |
| ⚠️  Partial | 1 |
| ❌ Fail    | 0 |
| ⏭️  Skipped | 0 |
| **Total** | **13** |

LLM calls used: 73

---

## Section Results

### ✅ Login — PASS (90/100)

**Page visited:** `http://localhost:8080/login` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Email/Username input field present (id='username')
- Password input field present (id='password')
- Sign In submit button present (inner_text='Sign In')
- Forgot Password? link present (href='/forgot-password')
- Register link present (href='/register')
- Page heading 'Sign In' visible

*All statically verifiable login form elements are present. Client-side validation rules and authentication behaviors (flash messages, redirects, clearing password) are dynamic and not verifiable from this static snapshot.*

---

### ✅ Register — PASS (90/100)

**Page visited:** `http://localhost:8080/register` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- First Name input field present (id='firstName')
- Last Name input field present (id='lastName')
- Street Address input field present (id='streetAddress')
- City input field present (id='city')
- State dropdown/combobox control present (Select state)
- ZIP Code input present with placeholder '12345'
- Phone Number input present with example placeholder
- Social Security Number input present with placeholder
- Username input present with type='email' (username)
- Password input present (type='password')
- Confirm Password input present (type='password')
- Register submit button present with text 'Register'
- Sign in link present pointing to /login

**✘ Missing (spec says it should exist, not found in DOM):**
- Dropdown options for State (full list of US states) not found in DOM

*All required input fields and the Register button are present and labeled; the state control exists but the snapshot does not include the full list of US state options to verify.*

---

### ✅ Accounts Overview — PASS (95/100)

**Page visited:** `http://localhost:8080/dashboard` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Welcome message showing user's name John Doe
- Page heading Accounts Overview present
- Account table with columns Account Number Account Type
- Clickable masked account numbers (e.g. ****5001)
- Account types shown Checking Savings Credit Card Loan
- Current balances present for each account row
- Status Active badges visible in each row
- Open dates shown (e.g. Jan 15, 2023)
- Footer totals: Total Assets Liabilities Net Worth
- Rows ordered earliest-to-latest by open date

*The dashboard implements the Accounts Overview as specified: welcome with user name, masked clickable account numbers, account type, balances, Active status badges, open dates, footer totals, and rows ordered earliest-first. No required static elements from the spec are missing.*

---

### ✅ Open New Account — PASS (90/100)

**Page visited:** `http://localhost:8080/open-account` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Checking account card with radio input
- Savings account card with radio input
- Minimum deposit: $25.00 (Checking)
- Minimum deposit: $100.00 (Savings)
- Initial Deposit Amount input (id=initialDeposit)
- Funding Source Account combobox labeled 'Select funding source'
- Open Account submit button
- Hidden input name='accountType'

*All required static UI elements for 'Open New Account' are present (account type cards, min deposits, deposit input, funding source selector, submit). Dynamic behaviors (validation, balance checks, success message/redirect) are not verifiable from this static snapshot.*

---

### ⚠️ Transfer Funds — PARTIAL (65/100)

**Page visited:** `http://localhost:8080/transfer` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Transfer Amount input present (id='amount')
- From Account dropdown present ('Select source account')
- Transfer To radio 'My ParaBank Account' present
- Transfer To radio 'External Account' present
- To Account dropdown present ('Select destination account')
- Submit button 'Transfer Funds' present
- Page URL '/transfer' reached

**✘ Missing (spec says it should exist, not found in DOM):**
- External account number input field for External Account
- Confirm external account number input field for External Account

*The page contains the main transfer form controls (amount, source/destination selectors, transfer-type radios, submit). However the UI elements required for external transfers (enter/confirm external account number) are not present, so the spec is only partially implemented.*

---

### ✅ Payments — PASS (95/100)

**Page visited:** `http://localhost:8080/bill-pay` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Payee Name input present (id='payeeName')
- Street Address input present (id='streetAddress')
- City input field present (id='city')
- State selector present (combobox 'Select state')
- ZIP Code input present (id='zipCode')
- Phone Number input present (id='phoneNumber')
- Payee Account Number input present (id='payeeAccount')
- Confirm Account Number input present (id='payeeAccountConfirm')
- Payment Amount numeric input present (id='paymentAmount')
- Source Account selector present (combobox 'Select source account')
- Pay button present (type='submit' inner_text='Pay Bill')

*The bill-pay form fields and Pay button required by the Payments spec are present on /bill-pay. Dynamic behaviors (validation, submission success, balance updates) are not verifiable from the static DOM snapshot.*

---

### ✅ Request Loan — PASS (85/100)

**Page visited:** `http://localhost:8080/loan` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Request Loan page heading present
- Personal, Auto, Home loan cards visible
- Interest rates and amount ranges shown on cards
- Radio inputs for selecting loan type
- Loan Amount numeric input present
- Down Payment numeric input present
- Collateral account dropdown (combobox) present
- Apply for Loan submit button present
- Loan Application section and explanatory text present

**⚡ Mismatches (DOM contradicts the spec):**
- loanAmount input has min='100' (general) — does not reflect type-specific min/max ranges required by spec

*The page implements the static UI for Request Loan (cards, fields, dropdown, submit). Dynamic validations, approval simulation, and success/denial messages are not present in the static snapshot and were not evaluated per testing rules.*

---

### ✅ Update Contact Info — PASS (95/100)

**Page visited:** `http://localhost:8080/profile` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page heading 'Update Contact Info' visible
- First Name input pre-filled with 'John'
- Last Name input pre-filled with 'Doe'
- Street Address input pre-filled '123 Main Street'
- City input pre-filled with 'Springfield'
- State control showing 'IL' selected
- ZIP Code input pre-filled with '62701'
- Phone Number input pre-filled '(555) 123-4567'
- Update Profile submit button present

*The page implements the editable contact form with all required fields pre-filled and an Update Profile button. Dynamic behaviors (validation, success/failure messages and highlighting) cannot be verified from this static snapshot.*

---

### ✅ Manage Cards — PASS (90/100)

**Page visited:** `http://localhost:8080/cards` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Manage Cards heading visible
- Your Cards list with debit/credit
- Card Type radios: Debit and Credit
- Account to Link dropdown 'Select account'
- Shipping Address input present
- 'Request Card' submit button present
- Select Existing Card dropdown present
- New Spending Limit numeric input present
- Travel Notice start and end date inputs
- Travel destination input placeholder present
- Card Status radios: Active and Frozen
- 'Update Controls' submit button present

*The page contains both the Request New Card and Card Controls forms with the required fields and buttons as specified. Dynamic behaviors (validation messages, success messages, backend checks) are not present in the static DOM and therefore not verifiable here.*

---

### ✅ Investments — PASS (95/100)

**Page visited:** `http://localhost:8080/investments` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Heading: Investments
- Portfolio Snapshot panel present
- Total Market Value displayed
- Unrealised Gain/Loss displayed
- Holdings table with VTSAX VTIAX
- Trade Action radios Buy/Sell
- Fund Symbol search input
- Quantity input (min=0.01)
- Funding Account select (trade)
- Execute Trade button
- Recurring Plan fund select
- Contribution Amount input (min=25)
- Frequency radios Weekly Monthly
- Start Date input
- Create Plan button

*All statically verifiable Investments page elements from the spec are present (portfolio snapshot, trade form fields, recurring plan fields). Dynamic behaviors (validation messages, execution confirmation) cannot be verified from this static snapshot.*

---

### ✅ Account Statements — PASS (95/100)

**Page visited:** `http://localhost:8080/statements` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page heading 'Account Statements' present
- Generate Statement section heading present
- Account dropdown (Select account combobox)
- Start Date input (id='startDate')
- End Date input (id='endDate')
- Generate Statement button present
- e-Statement Preferences heading present
- Paperless checkbox (id='paperless') with label
- Email Address input (type='email' id='prefEmail')
- Save Preference button present

*Both coordinated forms and all required static controls (account selector, date range inputs, checkbox, email field, and buttons) are present; dynamic validation/messages are not verifiable in this static snapshot.*

---

### ✅ Security Settings — PASS (90/100)

**Page visited:** `http://localhost:8080/security` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Security Settings heading present
- Collapsible panel titled 'Change Password' (open)
- Current Password input (id='currentPw')
- New Password input (id='newPw')
- Confirm New Password input (id='confirmPw')
- Change Password submit button present

**✘ Missing (spec says it should exist, not found in DOM):**
- HTML <form> element wrapping the change-password inputs

*The page shows the Security Settings section with a collapsible Change Password panel and the three password inputs plus submit button. Dynamic behaviors (password verification, strength enforcement, success message, field highlighting) are not verifiable from the static DOM and were not checked.*

---

### ✅ Support Center — PASS (80/100)

**Page visited:** `http://localhost:8080/support` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Support Center heading and subheading present
- Secure Message panel with subject field present
- Subject input field id='msgSubject' present
- Category dropdown control present (closed state)
- Message body textarea id='msgBody' present
- Attachment input and accepted types text present
- Send Message submit button present
- Schedule Callback panel and fields present
- Preferred Date input id='cbDate' present
- Phone number input id='cbPhone' present
- Request Callback submit button present

**✘ Missing (spec says it should exist, not found in DOM):**
- Category dropdown options: Account, Technical, Security, Other
- Reason for Call dropdown options (list not present)
- Preferred Time Window options (choices not present)

**⚡ Mismatches (DOM contradicts the spec):**
- Message Body is plain textarea, not a rich-text editor
- Phone number shown as placeholder, not pre-filled value

*The page implements both Secure Message and Schedule Callback forms with required fields and buttons present. Specific dropdown option items and a rich-text message editor / pre-filled phone value are not present in the static DOM snapshot; dynamic validations and success messages cannot be verified from this snapshot.*

---
