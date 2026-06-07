# Spec Verification Report

| | |
|---|---|
| **URL** | http://localhost:8080/ |
| **Spec file** | `datasets/parabank/faulty/Parabank.md` |
| **Date** | 2026-06-06 |
| **Overall score** | **70 / 100** |

## Summary

| Verdict | Count |
|---------|-------|
| ✅ Pass    | 4 |
| ⚠️  Partial | 0 |
| ❌ Fail    | 9 |
| ⏭️  Skipped | 0 |
| **Total** | **13** |

LLM calls used: 70

---

## Section Results

### ❌ Login — FAIL (60/100)

**Page visited:** `http://localhost:8080/` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Email/Username input field present with placeholder
- Password input field present with placeholder
- Sign In submit button present labeled 'Sign In'
- Forgot Password? link present with href '/forgot-password'
- Register here link present with href '/register'

**✘ Missing (spec says it should exist, not found in DOM):**
- Sign In with Google OAuth button

*Core login form inputs and primary actions (Sign In button and Forgot Password link) are present. Dynamic behaviors (validation, authentication messages, redirects) cannot be verified in this static snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-008** ✅ VALID
- **TC-009** ✅ VALID
- **TC-014** ✅ VALID

---

### ✅ Register — PASS (95/100)

**Page visited:** `http://localhost:8080/register` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- First Name input field
- Last Name input field
- Street Address input field
- City input field
- State dropdown/combobox control
- ZIP Code input (placeholder 12345)
- Phone Number input (placeholder (123) 456-7890)
- Social Security Number input (placeholder 123-45-6789)
- Username input (type=email, placeholder)
- Password input field
- Confirm Password input field
- Register submit button

*All required form inputs and the Register button are present in the static DOM. Dynamic behaviors (auto-formatting, validation enforcement, and post-submit success/redirect) cannot be verified from this snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-006** ✅ VALID
- **TC-010** ✅ VALID
- **TC-017** ✅ VALID

---

### ❌ Accounts Overview — FAIL (60/100)

**Page visited:** `http://localhost:8080/dashboard` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Welcome message with user's name
- Accounts Overview heading present
- Account table present under 'Your Accounts'
- Masked, clickable account numbers (e.g. ****5001)
- Account Type column (Checking, Savings, etc.)
- Current Balance values shown for each row
- Status column showing 'Active' for each account
- Open Date column present for each account
- Footer totals and Total Balance displayed
- Rows ordered by open date (earliest first)

**✘ Missing (spec says it should exist, not found in DOM):**
- Download CSV export button

*The page includes the welcome message, masked clickable account numbers, account type, balances, Active status badges, open dates, ordered rows, and footer totals matching the spec.*

#### Test Case Verification

- **TC-003** ✅ VALID
- **TC-008** ❌ INVALID
  - 🛑 Precondition says user is unauthenticated, but the live page shows an authenticated dashboard (Welcome back, John Doe and account data visible) — the test cannot be executed under the stated precondition
- **TC-012** ⚠️ INVALID_STEPS
  - ❌ step 2: Row with zero balance not found anywhere in the DOM — no account with a zero Current Balance is present in the snapshot
  - 🛑 Precondition requires at least one account with Current_Balance = 0; the live page contains negative balances but no zero balance row

---

### ❌ Open New Account — FAIL (60/100)

**Page visited:** `http://localhost:8080/open-account` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Checking account card (Minimum deposit: $25.00)
- Savings account card (Minimum deposit: $100.00)
- Radio inputs for account type selection
- Initial Deposit Amount numeric input (id='initialDeposit')
- Funding Source Account combobox/dropdown (Select funding source)
- "Open Account" submit button

**✘ Missing (spec says it should exist, not found in DOM):**
- Currency Selection dropdown

*All required static UI elements for opening a new account are present (account type cards, deposit input, funding source selector, submit). Runtime behaviors (validations, success message, redirect) are dynamic and not verifiable in this static snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-011** ✅ VALID
- **TC-016** ✅ VALID
- **TC-018** ✅ VALID

---

### ❌ Transfer Funds — FAIL (60/100)

**Page visited:** `http://localhost:8080/transfer` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Transfer Amount numeric input
- From Account selector (combobox)
- Radio button: My ParaBank Account
- Radio button: External Account
- To Account selector (combobox)
- Transfer Funds submit button

**✘ Missing (spec says it should exist, not found in DOM):**
- External account number input field for external transfers
- Confirm external account number input field for external transfers
- Schedule Recurring Transfer checkbox

*Core transfer form elements (amount, source selector, transfer-type radios, destination selector, submit) are present. Fields specific to external-transfer entry/confirmation are not found in the static DOM.*

#### Test Case Verification

- **TC-002** ✅ VALID
  - 🛑 Precondition 'User is logged in' satisfied by page text 'Welcome back, John Doe' and 'Log Out' button
- **TC-009** ✅ VALID
- **TC-011** ✅ VALID
  - 🛑 Precondition 'User is on Transfer Funds page' satisfied by page content
- **TC-012** ✅ VALID
- **TC-018** ✅ VALID
  - 🛑 Steps 1–2 (complete a successful transfer and press browser Back) are multi-step/browser-state interactions and cannot be verified from this static DOM snapshot — marked as unverifiable

---

### ❌ Payments — FAIL (60/100)

**Page visited:** `http://localhost:8080/bill-pay` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Payee Name input (id=payeeName)
- Street Address input (id=streetAddress)
- City input (id=city)
- State select combobox (role=combobox)
- ZIP Code input (id=zipCode)
- Phone Number input (id=phoneNumber)
- Payee Account Number input (id=payeeAccount)
- Confirm Account Number input (id=payeeAccountConfirm)
- Payment Amount numeric input (id=paymentAmount)
- Source Account dropdown (combobox)
- Submit button labeled 'Pay Bill'

**✘ Missing (spec says it should exist, not found in DOM):**
- Add New Payee button that opens a modal

*All required static form fields and the Pay button are present on the /bill-pay page. Dynamic behaviors (validation, funds check, success message, balance updates) cannot be verified from the static DOM snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-008** ✅ VALID
- **TC-009** ✅ VALID
  - 🛑 Precondition about the selected source account's balance (insufficient funds) cannot be verified from the static DOM
- **TC-012** ✅ VALID
  - 🛑 Precondition that a source account exists with an exact available balance matching the payment amount cannot be verified from the static DOM
- **TC-016** ✅ VALID
  - 🛑 Precondition about the source account having >=2× the payment amount cannot be verified from the static DOM

---

### ❌ Request Loan — FAIL (60/100)

**Page visited:** `http://localhost:8080/loan` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Request Loan heading and description
- Personal loan card with rate and range
- Auto loan card with rate and range
- Home loan card with rate and range
- Radio inputs for selecting loan type
- Loan Amount input (id=loanAmount)
- Down Payment input (id=downPayment)
- Collateral account combobox button
- Apply for Loan submit button

**✘ Missing (spec says it should exist, not found in DOM):**
- Upload Payslip file input

*Core UI elements required by the spec are present (loan type cards, rates/ranges, loan amount, down payment, collateral selector, submit). Runtime validations, approval engine behavior and success/denial messages are not verifiable in this static snapshot.*

#### Test Case Verification

- **TC-002** ✅ VALID
  - 🛑 Precondition: 'Credit engine configured for approval' cannot be verified from the static page
  - 🛑 Precondition: collateral account balance ≥ 20% cannot be verified from the static DOM (account list/balances not present)
- **TC-007** ✅ VALID
  - 🛑 Precondition states user is on Request Loan page — the page is present in the DOM
- **TC-010** ✅ VALID
  - 🛑 Precondition: 'Loan Type is selected' cannot be confirmed from the static snapshot (radio controls exist and can be selected during test)
  - 🛑 Validation outcome (inline error) is dynamic and not verifiable from DOM
- **TC-017** ✅ VALID
  - 🛑 Precondition: User is on Request Loan page — page is present
- **TC-021** ✅ VALID
  - 🛑 Precondition: existence of a collateral account with a specific balance (one unit below 20%) cannot be validated from the static DOM — account balances are not present
  - 🛑 The specific selection of an under-collateralised account and the resulting inline error are dynamic and not verifiable from this snapshot

---

### ❌ Update Contact Info — FAIL (60/100)

**Page visited:** `http://localhost:8080/profile` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Personal Information heading present
- First Name input pre-filled
- Last Name input pre-filled
- Street Address input pre-filled
- City input pre-filled
- State combobox showing IL
- ZIP Code input pre-filled
- Phone Number input pre-filled
- Update Profile submit button present

**✘ Missing (spec says it should exist, not found in DOM):**
- Secondary Email Address input field

*All required form fields and the Update Profile button are present and pre-filled as specified. Dynamic behaviors (validation messages and success banner) cannot be verified from the static DOM snapshot.*

#### Test Case Verification

- **TC-004** ✅ VALID
- **TC-005** ✅ VALID
- **TC-007** ✅ VALID
- **TC-012** ✅ VALID

---

### ✅ Manage Cards — PASS (95/100)

**Page visited:** `http://localhost:8080/cards` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Card Type radio options (Debit/Credit)
- Account to Link select (Select account)
- Shipping Address input (placeholder present)
- Request Card submit button
- Select Existing Card dropdown (Select card)
- New Spending Limit numeric input (id=spendingLimit)
- Travel Notice start date input
- Travel Notice end date input
- Travel Notice destination input
- Card Status radio options (Active, Frozen)
- Update Controls submit button

*All core static form elements for both the Request New Card and Card Controls sections are present. Dynamic behaviors and success/validation messages are not verifiable from this static DOM snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
  - 🛑 Precondition 'an account in good standing is available' cannot be confirmed from the static DOM — account selector exists but individual account option states are not present in the snapshot
- **TC-008** ✅ VALID
  - 🛑 Precondition 'an account that is NOT in good standing exists and is selectable' cannot be confirmed from the static DOM — the account selector control exists but option details and their standing are not present
- **TC-010** ✅ VALID
  - 🛑 Precondition 'An existing card is selected in Card Controls' cannot be confirmed from the static DOM — 'Select card' combobox exists but the snapshot does not show a selected card
- **TC-014** ✅ VALID
  - 🛑 Precondition 'An existing card is selected in Card Controls' cannot be confirmed from the static DOM — 'Select card' combobox exists but the snapshot does not show a selected card

---

### ❌ Investments — FAIL (60/100)

**Page visited:** `http://localhost:8080/investments` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Portfolio Snapshot panel with holdings table
- Total Market Value displayed ($22,834.23)
- Unrealised Gain/Loss displayed (+$396.98)
- Holdings rows for VTSAX and VTIAX with market values
- Trade Funds action radios (Buy and Sell)
- Fund Symbol autocomplete / search input and combobox
- Quantity numeric input (id=tradeQty, min/step present)
- Funding Account combobox (Select account)
- Execute Trade submit button
- Recurring Investment Plan form fields and Create Plan button
- Contribution Amount input (id=contribution, min=25)
- Frequency radios (Weekly, Monthly) and Start Date input

**✘ Missing (spec says it should exist, not found in DOM):**
- Risk Tolerance slider control

*All core Investments features (portfolio snapshot, trade form, recurring plan form and required inputs/buttons) are present in the static DOM. Runtime validation behaviors and success/error messages are dynamic and not verifiable from the snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-013** ✅ VALID
  - 🛑 Precondition requires knowledge of the user's holding balance; the page does show a Portfolio Snapshot (holdings listed) but the exact balance verification is external to the static DOM.
- **TC-014** ✅ VALID
  - 🛑 Precondition states the Recurring Investment Plan form is visible — the DOM contains the Recurring Investment Plan fields, so the precondition is satisfied.
- **TC-023** ✅ VALID
  - 🛑 Precondition requires an account with exact buying power equal to trade cost; presence of account selector is verifiable but account balances are backend data not present in static DOM.

---

### ✅ Account Statements — PASS (90/100)

**Page visited:** `http://localhost:8080/statements` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Page heading 'Account Statements'
- Account selection combobox ('Select account')
- Start Date input (type=date, id='startDate')
- End Date input (type=date, id='endDate')
- 'Generate Statement' submit button
- Paperless opt-in checkbox (role='checkbox', id='paperless')
- Email Address input (type=email, id='prefEmail')
- 'Save Preference' submit button

*Both coordinated forms and all required static inputs/buttons from the spec are present (custom date range used for statement period). Dynamic validation messages and success/failure alerts are not verifiable in this static snapshot.*

#### Test Case Verification

- **TC-002** ⚠️ INVALID_STEPS
  - ❌ step 1: 'Select Custom date range from Statement Period' — no Statement Period control or 'Custom date range' option found in DOM (no select/radio/group labeled Statement Period)
- **TC-007** ⚠️ INVALID_STEPS
  - ❌ step 1: 'Select Custom date range' — no Statement Period control or 'Custom date range' option found in DOM
- **TC-011** ⚠️ INVALID_STEPS
  - ❌ step 1: 'Select Custom date range' — no Statement Period control or 'Custom date range' option found in DOM

---

### ❌ Security Settings — FAIL (60/100)

**Page visited:** `http://localhost:8080/security` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Collapsible panel header 'Change Password ▲'
- Security Settings page heading present
- Input: Current Password (type=password, id=currentPw)
- Input: New Password (type=password, id=newPw)
- Input: Confirm New Password (type=password, id=confirmPw)
- Submit button 'Change Password' (type=submit)
- Panel shown as open (aria-expanded/data-state attributes)

**✘ Missing (spec says it should exist, not found in DOM):**
- Enable Two-Factor Authentication (2FA) toggle switch

*Core change-password form and collapsible panel are present with the three password fields and submit button; dynamic behaviors (verification, validation, success messages) are not verifiable from the static DOM.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-006** ✅ VALID
- **TC-010** ✅ VALID
  - 🛑 Test precondition requires a prior successful password change and a visible success notification; the static DOM snapshot does not show any success message or evidence of a just-completed change, so the browser-back interaction and resulting state cannot be verified here.
  - 🛑 Step 1 (press browser Back) is a navigation/history interaction and is UNVERIFIABLE from this static DOM snapshot.

---

### ✅ Support Center — PASS (95/100)

**Page visited:** `http://localhost:8080/support` — *online-banking-suite*

**✔ Matches (spec requirements found in live UI):**
- Subject input field present (id=msgSubject)
- Category dropdown combobox present (Select category)
- Message body textarea present (id=msgBody)
- Attachment input present with accepted types text
- Send Message button present (type=submit)
- Reason for Call dropdown combobox present
- Preferred date input present (id=cbDate)
- Preferred time window combobox present
- Phone number input present (id=cbPhone placeholder)
- Request Callback button present (type=submit)

*Core secure message and schedule callback form fields and submit buttons are present. Dynamic behaviors (validation, success messages, dropdown option contents) are not verifiable in this static DOM snapshot.*

#### Test Case Verification

- **TC-001** ✅ VALID
- **TC-016** ✅ VALID

---
