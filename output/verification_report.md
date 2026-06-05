# Spec Verification Report

| | |
|---|---|
| **URL** | http://localhost:8080 |
| **Spec file** | `datasets/parabank/Parabank.md` |
| **Date** | 2026-06-06 |
| **Overall score** | **88 / 100** |

## Summary

| Verdict | Count |
|---------|-------|
| ✅ Pass    | 12 |
| ⚠️  Partial | 1 |
| ❌ Fail    | 0 |
| ⏭️  Skipped | 0 |
| **Total** | **13** |

LLM calls used: 57

---

## Section Results

### ✅ Login — PASS (90/100)

**Page visited:** `http://localhost:8080/` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Email/Username input field (id='username')
- Password input field (id='password')
- 'Sign In' submit button present
- 'Forgot Password?' link (href='/forgot-password')
- 'Register here' link present

*Login form elements (username, password, submit, forgot-password link) are present. Server-side authentication, success/failure messages, and password/email validation rules are not verifiable from this static snapshot.*

---

### ✅ Register — PASS (90/100)

**Page visited:** `http://localhost:8080/register` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- First Name input present
- Last Name input present
- Street Address input present
- City input present
- State dropdown control 'Select state' present
- ZIP Code input (placeholder '12345') present
- Phone Number input (placeholder '(123) 456-7890') present
- Social Security Number input (placeholder '123-45-6789') present
- Username (Email) input type='email' present
- Password input present
- Confirm Password input present
- Register submit button present
- Sign in here link present

**✘ Missing (spec says it should exist, not found in DOM):**
- State dropdown options list (all US states not present in DOM snapshot)

*All required form fields and the Register button/link are present. The DOM shows a state selector control but the actual list of US state options is not present in the snapshot and therefore cannot be verified.*

---

### ✅ Accounts Overview — PASS (95/100)

**Page visited:** `http://localhost:8080/dashboard` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Welcome message includes 'John Doe'
- Page heading 'Accounts Overview' present
- Table headers: Account Number, Account Type, Current Balance, Status, Open Date
- Masked, clickable account numbers (****5001 etc.)
- Account types shown for each row
- Current balance values present for each account
- Status shown as 'Active' for each account
- Open Date values present for each account
- Footer totals showing Total Assets/Liabilities/Net Worth
- Rows ordered by open date (earliest first)

*The page implements the Accounts Overview per the spec: welcome + user name, masked clickable account numbers, required columns, active status badges, totals, and rows ordered by creation date. No static mismatches were found.*

---

### ✅ Open New Account — PASS (90/100)

**Page visited:** `http://localhost:8080/open-account` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page heading: Open New Account visible
- Checking account card with radio input present
- Savings account card with radio input present
- Minimum deposit text: $25.00 and $100.00 present
- Initial Deposit Amount numeric input present
- Funding Source Account dropdown combobox present
- Open Account submit button visible

*All required static elements from the spec are present (account type cards with minima, deposit input, funding selector, and Open Account button). Dynamic behaviors (real-time validation, funding-balance checks, success message and redirect) cannot be validated from this static DOM snapshot.*

---

### ✅ Transfer Funds — PASS (80/100)

**Page visited:** `http://localhost:8080/transfer` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page reached at /transfer URL
- Heading and section title 'Transfer Funds' present
- Transfer Amount input field (type=number, id='amount')
- From Account source dropdown / combobox present
- Transfer Type radio 'My ParaBank Account' present
- Transfer Type radio 'External Account' present
- To Account destination dropdown / combobox present
- Submit button labeled 'Transfer Funds' present

**✘ Missing (spec says it should exist, not found in DOM):**
- External account number input field for external transfers
- Confirm external account number input field for external transfers

*Core transfer UI elements (amount, source/destination selectors, transfer-type radios, submit) are present and the URL is correct. The page snapshot does not include fields to enter/confirm an external account number, so the external-transfer input flow is incomplete in this static DOM.*

---

### ✅ Payments — PASS (90/100)

**Page visited:** `http://localhost:8080/bill-pay` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Payee Name input (id=payeeName)
- Quick Select payee buttons (Electric/Gas/Internet)
- Street Address input (id=streetAddress)
- City input (id=city)
- State selector (combobox 'Select state')
- ZIP Code input (id=zipCode)
- Phone Number input (id=phoneNumber)
- Payee Account Number input (id=payeeAccount)
- Confirm Account Number input (id=payeeAccountConfirm)
- Payment Amount input (type=number id=paymentAmount)
- Source Account dropdown (combobox 'Select source account')
- Submit button present (labeled 'Pay Bill')

**⚡ Mismatches (DOM contradicts the spec):**
- Submit button text is 'Pay Bill' but spec expects 'Pay' (label differs)

*All required form fields and a submit control for bill payments are present on /bill-pay. Dynamic behaviors (validation messages, success confirmation, balance updates) cannot be verified from this static snapshot and were not treated as missing.*

---

### ✅ Request Loan — PASS (85/100)

**Page visited:** `http://localhost:8080/loan` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Personal Loan card with rate and amount
- Auto Loan card with rate and amount
- Home Loan card with rate and amount
- Loan Application heading visible
- Loan Amount input field present
- Down Payment input field present
- Collateral account combobox present
- Apply for Loan submit button present

**⚡ Mismatches (DOM contradicts the spec):**
- loanAmount input has min='100' (DOM) which does not enforce the spec's type-specific minimums (e.g., $1,000/$5,000/$50,000)

*The page includes the three loan type cards (with rates and displayed ranges), inputs for loan and down payment, a collateral account selector, and the Apply button. Dynamic validations and approval/denial messaging are not present in the static snapshot and therefore not assessed here.*

---

### ✅ Update Contact Info — PASS (95/100)

**Page visited:** `http://localhost:8080/profile` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Heading 'Update Contact Info' present
- First Name input value 'John'
- Last Name input value 'Doe'
- Street Address input value '123 Main Street'
- City input value 'Springfield'
- State selection 'IL' present
- ZIP Code input value '62701'
- Phone Number input value '(555) 123-4567'
- Button 'Update Profile' present

*All required editable fields are present and pre-filled and the Update Profile button is available. Runtime validation and success/failure messaging are dynamic behaviors and not verifiable from this static snapshot.*

---

### ✅ Manage Cards — PASS (90/100)

**Page visited:** `http://localhost:8080/cards` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Manage Cards page heading present
- Your Cards list showing two cards
- Request New Card form present
- Card Type radio options (Debit, Credit)
- Account to Link dropdown (Select account)
- Shipping Address input present
- Request Card submit button present
- Card Controls form present
- New Spending Limit numeric input present
- Travel Notice date and destination inputs present
- Card Status radios (Active, Frozen) present
- Update Controls button present

*The page and both stacked forms (Request New Card and Card Controls) contain the required static fields and buttons per spec. Dynamic behaviors (submission success messages, validation, ticket creation) are not verifiable in this static snapshot.*

---

### ✅ Investments — PASS (95/100)

**Page visited:** `http://localhost:8080/investments` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Portfolio Snapshot panel with total market value
- Unrealised Gain/Loss displayed with value
- Holdings table with symbols, shares, price, values
- Trade Funds section with Buy and Sell radios
- Fund Symbol autocomplete/search input present
- Quantity numeric input (id=tradeQty) present
- Funding Account dropdown/combo field present
- Execute Trade submit button present
- Recurring Investment Plan section present
- Recurring Fund Symbol select input present
- Contribution Amount input with min=25
- Frequency radios Weekly and Monthly present
- Start Date date input (id=planStartDate) present
- Create Plan submit button present

*The page includes the Portfolio Snapshot, Trade Funds form, and Recurring Investment Plan form as specified. Dynamic validations, trade execution, and runtime checks are not verifiable from this static snapshot.*

---

### ✅ Account Statements — PASS (90/100)

**Page visited:** `http://localhost:8080/statements` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Account Statements page heading present
- Subtitle: Generate statements and manage e-statement preferences
- Generate Statement form heading present
- Account dropdown / combobox labeled 'Select account'
- Start Date input (input type=date, id=startDate)
- End Date input (input type=date, id=endDate)
- Generate Statement button present
- E-Statement Preferences heading and checkbox present
- Paperless checkbox (role=checkbox, id=paperless) present
- Email Address input (type=email, id=prefEmail) and Save Preference button

*The page includes the two side-by-side forms with account selector, start/end date fields, generate button, paperless checkbox, email field, and save button. Dynamic behaviors and success/error messages are not verifiable from this static snapshot.*

---

### ✅ Security Settings — PASS (90/100)

**Page visited:** `http://localhost:8080/security` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Security Settings page heading 'Security Settings' visible
- Collapsible panel titled 'Change Password' present and open
- Current Password input field present (id=currentPw)
- New Password input field present (id=newPw)
- Confirm New Password input field present (id=confirmPw)
- Change Password submit button present with label

*The page includes the Security Settings heading, an open Change Password collapsible panel, three password inputs and a Change Password submit button. Runtime behaviors (password verification, strength enforcement, success/validation messages) are dynamic and not verifiable from the static snapshot.*

---

### ⚠️ Support Center — PARTIAL (65/100)

**Page visited:** `http://localhost:8080/support` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Support Center heading present
- Subject input present
- Category dropdown control present
- Message Body textarea present
- Attachment input present (accepted types shown)
- Send Message button present
- Reason for Call dropdown control present
- Preferred Date input present
- Preferred Time Window control present
- Phone Number input present (editable)
- Request Callback button present

**✘ Missing (spec says it should exist, not found in DOM):**
- Category dropdown options: Account, Technical, Security, Other

**⚡ Mismatches (DOM contradicts the spec):**
- Message Body is a plain textarea, not a rich-text editor
- Phone Number shown as placeholder (555-123-4567) rather than pre-filled value

*The page contains both secure message and callback forms with the required fields and buttons, but the category option values are not present in the DOM and the message body is a textarea instead of a rich-text editor; phone number is shown only as a placeholder.*

---
