# Spec Verification Report

| | |
|---|---|
| **URL** | http://localhost:8080 |
| **Spec file** | `datasets/parabank/Parabank.md` |
| **Date** | 2026-06-03 |
| **Overall score** | **91 / 100** |

## Summary

| Verdict | Count |
|---------|-------|
| ✅ Pass    | 13 |
| ⚠️  Partial | 0 |
| ❌ Fail    | 0 |
| ⏭️  Skipped | 0 |
| **Total** | **13** |

LLM calls used: 55

---

## Section Results

### ✅ Login — PASS (90/100)

**Page visited:** `http://localhost:8080/login` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Email/Username input field (input type='text', id='username', placeholder='Enter your email or username')
- Password input field (input type='password', id='password', placeholder='Enter your password')
- Sign In button (button type='submit', inner_text='Sign In')
- Forgot Password? link (a href='/forgot-password', inner_text='Forgot Password?')
- Register here link (a href='/register', inner_text='Register here')
- Visible labels/text for 'Email/Username' and 'Password' present in page content

*The static DOM shows the required fields, sign-in button, and forgot-password link, so the page structure matches the spec. Dynamic behaviors (validation, authentication, success/error messages, redirects) cannot be verified from the static snapshot and were not evaluated.*

---

### ✅ Register — PASS (90/100)

**Page visited:** `http://localhost:8080/register` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- First Name input (id='firstName')
- Last Name input (id='lastName')
- Street Address input (id='streetAddress')
- City input (id='city')
- State control (combobox button with 'Select state')
- Hidden select containing US state options (appears to list states)
- ZIP Code input (id='zipCode', placeholder='12345')
- Phone Number input (id='phoneNumber', placeholder='(123) 456-7890')
- Social Security Number input (id='ssn', placeholder='123-45-6789')
- Username input of type='email' (id='username', placeholder='john@example.com')
- Password input (type='password', id='password')
- Confirm Password input (type='password', id='confirmPassword')
- Register button (type='submit', inner_text='Register')
- Link to sign in page (a href='/login', 'Sign in here')

*All required fields, a state selector with state options, email-type username, and the Register button are present in the static DOM. Dynamic behaviors described in the spec (formatting, validation enforcement, success messages and redirects) cannot be verified from a static snapshot and were therefore not assessed.*

---

### ✅ Accounts Overview — PASS (95/100)

**Page visited:** `http://localhost:8080/dashboard` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Welcome message with user's name ('Welcome back, John Doe')
- Accounts table present
- Clickable masked Account Numbers (****5001, ****5002, ****5003, ****5004) as anchors
- Account Types visible for each row (Checking, Savings, Credit Card, Loan)
- Current Balance values present for each account
- Account Status shown as 'Active' for each row
- Open Date present for each account row
- Table footer / totals present (Total Assets, Total Liabilities, Net Worth) and top Total Balance banner
- Rows ordered by Open Date ascending (earliest first: Jan 15, Feb 20, Mar 10, Apr 5)

*The static DOM contains the required welcome text, masked clickable account numbers, account rows with type, balance, status, and open date, and footer totals; ordering by open date is verifiable and correct. Dynamic behaviors (e.g., click action implementation) cannot be verified from the snapshot.*

---

### ✅ Open New Account — PASS (90/100)

**Page visited:** `http://localhost:8080/open-account` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page heading/text 'Open New Account' present
- Checking card with heading, description and features list
- Savings card with heading, description and features list
- Two radio inputs for account type selection
- Minimum deposit amounts displayed for Checking ($25.00) and Savings ($100.00)
- Initial Deposit Amount input present (input type='number', id='initialDeposit')
- Funding Source control present (combobox button) and a select listing funding accounts with balances
- Open Account button present (type='submit')

*All required static UI elements from the spec are present in the DOM (account type cards, radio inputs, deposit input, funding source options, submit button). Dynamic behaviors such as validation, real-time errors, balance sufficiency checks, success message and redirect cannot be verified from a static DOM snapshot and therefore are not assessed here.*

---

### ✅ Transfer Funds — PASS (90/100)

**Page visited:** `http://localhost:8080/transfer` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Transfer Amount input present (input type='number' id='amount' name='amount')
- Transfer Type radio buttons present (input id='internal' name='transferType' and input id='external' name='transferType')
- Radio labels present for 'My ParaBank Account' and 'External Account'
- Source account selector present (select containing 'Checking Account (****5001)' and 'Savings Account (****5002)')
- Destination account selector present (select containing same Checking and Savings entries)
- Transfer submit button present (button type='submit' inner_text='Transfer Funds')

*All static, verifiable UI elements required by the spec are present (amount field, source dropdown filtered to Checking/Savings, transfer-type radios, destination selector, and submit). Dynamic behaviors and runtime validations (changing destination inputs for external transfers, validation messages, success/failure text) cannot be verified from the static DOM snapshot and were not assessed.*

---

### ✅ Payments — PASS (90/100)

**Page visited:** `http://localhost:8080/bill-pay` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Payee Name input (id='payeeName')
- Quick Select buttons (Electric Company, Gas Utility, Internet Provider)
- Street Address input (id='streetAddress')
- City input (id='city')
- State selector (combobox button plus hidden select of states)
- ZIP Code input (id='zipCode')
- Phone Number input (id='phoneNumber')
- Payee Account Number input (id='payeeAccount')
- Confirm Account Number input (id='payeeAccountConfirm')
- Payment Amount input (type='number' id='paymentAmount')
- Source Account selector (combobox button and hidden select with accounts)
- Submit button present (type='submit' inner_text='Pay Bill')

**⚡ Mismatches (DOM contradicts the spec):**
- Spec calls for a “Pay” button; DOM shows a submit button labeled 'Pay Bill'

*All required form fields and account/source options are present in the DOM. Dynamic behaviors (validation, success/error messages, balance updates) cannot be verified from the static snapshot and were not evaluated.*

---

### ✅ Request Loan — PASS (85/100)

**Page visited:** `http://localhost:8080/loan` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Three loan type cards present: Personal, Auto, Home (each displays rate, amount range, term)
- Three radio inputs for selecting loan type
- Loan Amount input present (input#loanAmount)
- Down Payment Amount input present (input#downPayment)
- Collateral account control present (combobox button and underlying select with account options and balances)
- Apply for Loan button present
- Loan Application section and associated labels ('Loan Amount', 'Down Payment Amount', 'Collateral Account') visible

**⚡ Mismatches (DOM contradicts the spec):**
- Single loan amount input has min='100' on the input element rather than per-type min/max constraints; the DOM does not show per-type input constraints for the specified ranges (Personal $1,000+, Auto $5,000+, Home $50,000+)

*All required UI elements (loan cards, inputs, collateral selector, apply button) are present. Dynamic behaviors and validations described in the spec (range enforcement, credit engine behavior, approval/denial messages) cannot be verified from a static DOM and were not marked missing.*

---

### ✅ Update Contact Info — PASS (90/100)

**Page visited:** `http://localhost:8080/profile` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page header/section 'Update Contact Info' present
- Section title 'Personal Information' present
- First Name input (id='firstName', value='John') present
- Last Name input (id='lastName', value='Doe') present
- Street Address input (id='streetAddress', value='123 Main Street') present
- City input (id='city', value='Springfield') present
- State control present (combobox button showing 'IL' and a select with state options)
- ZIP Code input (id='zipCode', placeholder='12345', value='62701') present
- Phone Number input (id='phoneNumber', placeholder='(123) 456-7890', value='(555) 123-4567') present
- Update Profile button (type='submit') present

*All required form fields and the Update Profile button are present and pre-filled in the static DOM. Runtime behaviors from the spec (validation, success/failure messages, refresh) cannot be verified from this static snapshot and were therefore not checked.*

---

### ✅ Manage Cards — PASS (95/100)

**Page visited:** `http://localhost:8080/cards` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Card Type radio options (Debit Card, Credit Card) present
- Account to Link selector (combobox button and select with account options) present
- Shipping Address input (id='shippingAddress') present
- 'Request Card' submit button present
- Select Existing Card dropdown (combobox button and select with cards) present
- New Spending Limit numeric input (id='spendingLimit', step/min/max attributes present)
- Travel Notice Start Date input (type='date') present
- Travel Notice End Date input (type='date') present
- Travel Notice Destination input (placeholder='Destination (e.g., Europe, Asia)') present
- Card Status radio options (Active, Frozen) present
- 'Update Controls' submit button present
- 'Your Cards' card list (Debit Card and Credit Card entries) present

*All static, verifiable UI elements required by the Manage Cards spec are present in the DOM. Dynamic behaviors (validation, success messages, ticket creation, account standing checks) cannot be verified from the static snapshot and were not assessed.*

---

### ✅ Investments — PASS (95/100)

**Page visited:** `http://localhost:8080/investments` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Portfolio Snapshot panel present
- Total Market Value displayed
- Unrealised Gain/Loss displayed
- Holdings table with columns Symbol, Name, Shares, Price, Market Value, Gain/Loss (VTSAX, VTIAX rows)
- Trade Funds section present
- Action radios for Buy and Sell (trade-Buy, trade-Sell)
- Fund Symbol search input / autocomplete field (placeholder 'Search funds...')
- Fund selector control (Select fund) and options list
- Quantity input (id='tradeQty', type='number')
- Funding Account dropdown for trade (select with accounts)
- Execute Trade button (type='submit')
- Recurring Investment Plan section present
- Recurring Fund Symbol selector (Select fund) and options list
- Contribution Amount input (id='contribution', min='25')
- Frequency radios Weekly and Monthly (freq-Weekly, freq-Monthly)
- Start Date input (type='date', id='planStartDate')
- Funding Account dropdown for plan (select with accounts)
- Create Plan button (type='submit')

*All static, verifiable UI elements from the Investments spec are present (portfolio snapshot, trade form fields, and recurring plan fields). Dynamic behaviors and runtime validations cannot be assessed from the static DOM and were not checked.*

---

### ✅ Account Statements — PASS (95/100)

**Page visited:** `http://localhost:8080/statements` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Account Statements page header
- Generate Statement section heading
- Account selector (combobox/select) with account options
- Start Date input (id='startDate')
- End Date input (id='endDate')
- Generate Statement button
- e-Statement Preferences heading
- Opt into paperless statements checkbox (role='checkbox', id='paperless') and label
- Email Address input (type='email', id='prefEmail')
- Save Preference button

*The static DOM contains the required fields and buttons for both the Generate Statement and e-Statement Preference forms. Dynamic behaviors (date/email validation, success/failure messages, and generation flow) cannot be verified from this static snapshot.*

---

### ✅ Security Settings — PASS (90/100)

**Page visited:** `http://localhost:8080/security` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Security Settings page heading present
- Collapsible 'Change Password' panel (aria-expanded='true') present
- Current Password input (input type='password' id='currentPw') present
- New Password input (input type='password' id='newPw') present
- Confirm New Password input (input type='password' id='confirmPw') present
- 'Change Password' submit button (type='submit' inner_text='Change Password') present
- Navigation link to 'Security Settings' present

*The static DOM contains the expected collapsible panel, three password fields, and the Change Password button. Dynamic behaviors (current-password verification, strong-password enforcement, match checking, success message, and validation highlighting) cannot be verified from a static snapshot.*

---

### ✅ Support Center — PASS (85/100)

**Page visited:** `http://localhost:8080/support` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Secure Message - Subject input (id='msgSubject') present
- Secure Message - Category dropdown present with options: Account, Technical, Security, Other
- Secure Message - Message Body field present (textarea id='msgBody')
- Secure Message - Attachment input (id='attachment') present and Accepted file types text visible
- Secure Message - 'Send Message' button present
- Schedule Callback - Reason for Call dropdown present with options
- Schedule Callback - Preferred Date input (type='date', id='cbDate') present
- Schedule Callback - Preferred Time Window dropdown present with options
- Schedule Callback - Phone Number input (id='cbPhone') present
- Schedule Callback - 'Request Callback' button present

**⚡ Mismatches (DOM contradicts the spec):**
- Message Body is implemented as a plain textarea in the DOM, but the spec requires a rich text editor
- Phone Number appears only as a placeholder (no pre-filled value visible in the DOM); spec requires the phone to be pre-filled but editable

*The page includes the required form fields, dropdowns, and buttons for both secure message and callback forms. Two small discrepancies: the message editor is a textarea rather than an explicit rich-text editor, and the phone number is not shown as pre-filled in the static DOM.*

---
