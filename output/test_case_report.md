# Test Case Verification Report

**Application:** http://localhost:8080  
**Test Cases:** `input/parabank/Test_Cases.md`  
**Generated:** 2026-05-31T06:11:16.730626  
**LLM Calls:** 13

---

## Summary

| Metric | Count |
|--------|-------|
| ✅ Valid | 45 |
| ⚠️ Invalid Steps | 5 |
| ❌ Invalid | 0 |
| ⏭️ Skipped | 0 |
| **Total** | **50** |
| **Accuracy** | **90%** |

---

## Results Table

| TC ID | Module | Type | Priority | Verdict | Notes |
|-------|--------|------|----------|---------|-------|
| TC-001 | Login | Positive | High | ✅ Valid | All verifiable interaction steps (enter username/email, enter password, click Si |
| TC-008 | Login | Negative | High | ✅ Valid | All steps reference UI elements present on the page. The expected error behavior |
| TC-009 | Login | Edge/Boundary | Medium | ✅ Valid | Inputs for email/username and password and the Sign In submit button exist; the  |
| TC-014 | Login | Edge/State | Medium | ✅ Valid | All interaction steps target elements present on the page. The post-failure beha |
| TC-001 | Register | Positive | High | ✅ Valid | All verifiable UI elements referenced by the happy-path steps exist on the page. |
| TC-006 | Register | Negative | High | ✅ Valid | All required fields and the Register button exist. Validation error messages and |
| TC-010 | Register | Negative | High | ✅ Valid | All fields needed to perform the mismatch-password negative test are present. Th |
| TC-017 | Register | Edge/Boundary | Medium | ✅ Valid | All verifiable UI elements exist. The runtime behavior of auto-formatting the ph |
| TC-003 | Accounts Overview | Positive | High | ✅ Valid | All steps are executable: the Accounts Overview page and masked account-number l |
| TC-008 | Accounts Overview | Negative | High | ✅ Valid | The navigation step is executable, but the precondition (unauthenticated user) d |
| TC-012 | Accounts Overview | Edge/Data | Medium | ⚠️ Invalid Steps | Negative balances and the Total Balance footer are present and verifiable, but t |
| TC-001 | Open New Account | Positive | High | ✅ Valid | All required UI elements for opening a Checking account are present on the Open  |
| TC-011 | Open New Account | Negative | High | ✅ Valid | All UI controls referenced by the steps exist, but the page's account data does  |
| TC-016 | Open New Account | Edge/Boundary | Medium | ⚠️ Invalid Steps | UI elements exist for selecting account type, entering deposit and submitting, b |
| TC-018 | Open New Account | Edge/Interaction | Medium | ✅ Valid | All UI controls needed to reproduce switching account type after entering a depo |
| TC-002 | Transfer Funds | Positive | High | ✅ Valid | All verifiable UI elements for an external transfer are present (amount input, s |
| TC-009 | Transfer Funds | Negative | High | ✅ Valid | All UI elements required by this negative test (radios, amount input, source/des |
| TC-011 | Transfer Funds | Negative | High | ✅ Valid | Verifiable UI elements (External radio, amount input, source account selector, s |
| TC-012 | Transfer Funds | Edge/Boundary | Medium | ✅ Valid | All UI controls needed for this boundary transfer are present. Verifying the pos |
| TC-018 | Transfer Funds | Edge/Interaction | Medium | ✅ Valid | This test is a multi-step/browser-back interaction that cannot be fully verified |
| TC-001 | Payments | Positive | High | ✅ Valid | All form fields and controls referenced by the steps exist on the page; post-sub |
| TC-008 | Payments | Negative | High | ✅ Valid | The inputs needed to enter mismatched account numbers and submit exist. The expe |
| TC-009 | Payments | Negative | High | ✅ Valid | All UI controls referenced by the steps exist. The insufficient-funds error beha |
| TC-012 | Payments | Edge/Boundary | Medium | ✅ Valid | Form fields and controls required to perform the boundary test exist. The succes |
| TC-016 | Payments | Edge/Interaction | Medium | ✅ Valid | The UI elements needed to submit (and re-submit) exist on the page. The multi-st |
| TC-002 | Request Loan | Positive | High | ✅ Valid | All UI elements referenced by the steps exist (loan type radios, loan amount, do |
| TC-007 | Request Loan | Negative | High | ✅ Valid | All steps reference present controls. Validation outcome (inline error) is dynam |
| TC-010 | Request Loan | Negative | High | ✅ Valid | Inputs and submit button required by the steps are present. The precondition abo |
| TC-017 | Request Loan | Edge/Boundary | Medium | ✅ Valid | All UI controls referenced exist. The boundary validation behavior (exact 10%) i |
| TC-021 | Request Loan | Edge/Boundary | Medium | ✅ Valid | All referenced UI elements are present. The specific balance edge-case precondit |
| TC-004 | Update Contact Info | Positive | High | ✅ Valid | All interactive steps reference existing form controls on the Profile page; post |
| TC-005 | Update Contact Info | Negative | High | ✅ Valid | Required-field negative test references existing inputs and submit button; inlin |
| TC-007 | Update Contact Info | Negative | Medium | ✅ Valid | Phone number field and submit button exist on the page; format validation and er |
| TC-012 | Update Contact Info | Edge/Input | Medium | ✅ Valid | Whitespace-edge case references existing Last Name input and submit button; enfo |
| TC-001 | Manage Cards | Positive | High | ✅ Valid | All verifiable UI elements required to perform a card request (card type radios, |
| TC-008 | Manage Cards | Negative | High | ✅ Valid | All UI elements referenced by the steps exist. The specific data condition (an a |
| TC-010 | Manage Cards | Negative | Medium | ✅ Valid | All UI elements needed to add a travel notice and submit (date inputs and Update |
| TC-014 | Manage Cards | Edge/Boundary | Medium | ✅ Valid | UI elements to enter matching Start and End dates and submit are present. Accept |
| TC-001 | Investments | Positive | High | ✅ Valid | All UI elements referenced by the test exist on the Investments page. The suffic |
| TC-013 | Investments | Negative | High | ✅ Valid | All UI controls required to perform the Sell flow are present. The test's data-d |
| TC-014 | Investments | Negative | High | ✅ Valid | The Recurring Investment Plan form and all referenced inputs are present on the  |
| TC-023 | Investments | Edge/Boundary | Medium | ✅ Valid | All UI elements required for the buy flow are present. The exact buying-power == |
| TC-002 | Account Statements | Positive | High | ⚠️ Invalid Steps | Start/End date inputs, account selector, and Generate button exist and are verif |
| TC-007 | Account Statements | Negative | High | ⚠️ Invalid Steps | Date inputs and Generate button exist so entering an invalid date order is possi |
| TC-011 | Account Statements | Edge/Boundary | Medium | ⚠️ Invalid Steps | Filling both date fields with the same date and clicking Generate is executable, |
| TC-001 | Security Settings | Positive | High | ✅ Valid | All verifiable UI elements required by this test (panel trigger, three password  |
| TC-006 | Security Settings | Negative | High | ✅ Valid | All UI elements referenced by the steps exist. The expected inline error after s |
| TC-010 | Security Settings | Edge/Interaction | Medium | ✅ Valid | The page contains the Current Password input and the Change Password button requ |
| TC-001 | Support Center | Positive | High | ✅ Valid | All verifiable UI elements referenced in the test (Message Body and Send Message |
| TC-016 | Support Center | Edge/Input | Low | ✅ Valid | All referenced form controls (subject, message body, attachment input, and submi |

---

## Detail by Module

### Login

#### ✅ Valid — TC-001: Successful sign-in with valid credentials
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/login

**✔ Valid Steps:**
- step 1: Email/Username input found (input#username placeholder='Enter your email or username')
- step 2: Password input found (input#password placeholder='Enter your password')
- step 3: Sign In button found (button[type=submit] text='Sign In')

**Notes:** All verifiable interaction steps (enter username/email, enter password, click Sign In) map to inputs/buttons present on the page. Post-submit outcomes are dynamic and not checked here.

---

#### ✅ Valid — TC-008: Authentication failure with unregistered credentials
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/login

**✔ Valid Steps:**
- step 1: Email/Username input found (input#username placeholder='Enter your email or username')
- step 2: Password input found (input#password placeholder='Enter your password')
- step 3: Sign In button found (button[type=submit] text='Sign In')

**Notes:** All steps reference UI elements present on the page. The expected error behavior after submit is dynamic and outside static DOM verification.

---

#### ✅ Valid — TC-009: Password at exact minimum length (8 chars) succeeds
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/login

**✔ Valid Steps:**
- step 1: Email/Username input found (input#username placeholder='Enter your email or username')
- step 2: Password input found (input#password placeholder='Enter your password')
- step 3: Sign In button found (button[type=submit] text='Sign In')

**Notes:** Inputs for email/username and password and the Sign In submit button exist; the boundary password length behavior is a backend/flow check and not verifiable from static DOM.

---

#### ✅ Valid — TC-014: Failed login clears Password but preserves Email/Username
**Type:** Edge/State | **Priority:** Medium  
**URL:** http://localhost:8080/login

**✔ Valid Steps:**
- step 1: Email/Username input found (input#username placeholder='Enter your email or username')
- step 2: Password input found (input#password placeholder='Enter your password')
- step 3: Sign In button found (button[type=submit] text='Sign In')

**Notes:** All interaction steps target elements present on the page. The post-failure behavior (clearing password, retaining email, showing error) is dynamic and not validated from the static DOM.

---

### Register

#### ✅ Valid — TC-001: Complete registration happy path
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/register

**✔ Valid Steps:**
- step 1: First Name input found (input#firstName)
- step 1: Last Name input found (input#lastName)
- step 1: Street Address input found (input#streetAddress)
- step 1: City input found (input#city)
- step 2: State selector found (button[role=combobox] text='Select state' and hidden select of states present)
- step 3: ZIP input found (input#zipCode)
- step 4: Phone input found (input#phoneNumber)
- step 5: SSN input found (input#ssn)
- step 6: Username (email) input found (input#username type=email)
- step 7: Password input found (input#password)
- step 7: Confirm Password input found (input#confirmPassword)
- step 8: Register button found (button[type=submit] text='Register')

**Notes:** All verifiable UI elements referenced by the happy-path steps exist on the page. Post-submit outcomes (success message/redirect) are dynamic and not verified here.

---

#### ✅ Valid — TC-006: Submit with ALL required fields empty
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/register

**✔ Valid Steps:**
- step 1: All required inputs are present and can be left blank (input#firstName, input#lastName, input#streetAddress, input#city, state selector, input#zipCode, input#phoneNumber, input#ssn, input#username, input#password, input#confirmPassword)
- step 2: Register button found (button[type=submit] text='Register')

**Notes:** All required fields and the Register button exist. Validation error messages and form submission behavior are dynamic and not verifiable from the static DOM.

---

#### ✅ Valid — TC-010: Confirm Password does not match Password
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/register

**✔ Valid Steps:**
- step 1: Password input found (input#password)
- step 2: Confirm Password input found (input#confirmPassword)
- step 3: Other required fields exist (input#firstName, input#lastName, input#streetAddress, input#city, state selector, input#zipCode, input#phoneNumber, input#ssn, input#username)
- step 4: Register button found (button[type=submit] text='Register')

**Notes:** All fields needed to perform the mismatch-password negative test are present. The inline error message and submission outcome are runtime behaviors and not checked here.

---

#### ✅ Valid — TC-017: 10-digit phone auto-formats to (123) 456-7890 and registration succeeds
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/register

**✔ Valid Steps:**
- step 1: All required inputs exist to fill (input#firstName, input#lastName, input#streetAddress, input#city, state selector, input#zipCode, input#phoneNumber, input#ssn, input#username, input#password, input#confirmPassword)
- step 2: Phone Number input found for entering 10 raw digits (input#phoneNumber)
- step 4: Register button found (button[type=submit] text='Register')

**Notes:** All verifiable UI elements exist. The runtime behavior of auto-formatting the phone field (step 3) and the post-submit success/redirect are dynamic and therefore not verifiable from the static DOM snapshot.

---

### Accounts Overview

#### ✅ Valid — TC-003: Account numbers are masked showing only last four digits
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/dashboard

**✔ Valid Steps:**
- step 1: Navigate to Accounts Overview — 'Accounts Overview' link/button found (a[href='/dashboard'] / page header present)
- step 2: Inspect the Account Number column for each row — account number links found (a[href='/account/12345001'], a[href='/account/12345002'], a[href='/account/12345003'], a[href='/account/12345004']) showing masked values like '****5001', '****5002', '****5003', '****5004'

**Notes:** All steps are executable: the Accounts Overview page and masked account-number links are present and show the expected '****<last4>' format.

---

#### ✅ Valid — TC-008: Unauthenticated access to Accounts Overview redirects to Login
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/dashboard

**✔ Valid Steps:**
- step 1: Navigate directly to the Accounts Overview URL — the Accounts Overview page exists and is reachable (a[href='/dashboard'] / current page is dashboard)

**⚠ Precondition Issues:**
- Precondition says user is unauthenticated, but the page shows an authenticated session (Welcome back, John Doe and a 'Log Out' button are present).

**Notes:** The navigation step is executable, but the precondition (unauthenticated user) does not match the live page state. The expected redirect to Login cannot be validated from this snapshot because the user appears logged in.

---

#### ⚠️ Invalid Steps — TC-012: Zero and negative Current Balance values displayed and summed correctly
**Type:** Edge/Data | **Priority:** Medium  
**URL:** http://localhost:8080/dashboard

**✔ Valid Steps:**
- step 1: Navigate to Accounts Overview — 'Accounts Overview' page/link present (a[href='/dashboard'] / page header)
- step 2 (partial): Negative Current Balance rows are present and locatable (rows show -$1,534.67 and -$45,000.00)
- step 3: Observe each row's display and the Total Balance footer — Total Balance/footer is visible and shows -$15,008.25

**⚠ Precondition Issues:**
- Precondition requires at least one account with Current_Balance = 0, but the live page contains no zero-balance account (only positive and negative balances present)

**✘ Invalid Steps (referenced element NOT found in DOM):**
- step 2: Locate rows with zero and negative balances — a row with Current Balance = 0 is not present anywhere in the DOM/snapshot (no zero balance row found), so the step's requirement to locate both zero and negative rows cannot be satisfied

**Invalid Reason:** The page does not contain any account with a zero current balance as required by the test precondition/step.

**Notes:** Negative balances and the Total Balance footer are present and verifiable, but the required zero-balance row is missing from this snapshot, making the test step invalid for this page state.

---

### Open New Account

#### ✅ Valid — TC-001: Open a Checking account at minimum deposit
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/open-account

**✔ Valid Steps:**
- step 1: 'Open New Account' navigation link present (a[href='/open-account'] inner_text='Open New Account') / page is the Open New Account page
- step 2: 'Checking' account type radio exists (h3 'Checking' present and an input[type='radio'] exists for the Checking card)
- step 3: Initial Deposit Amount input found (input#initialDeposit name='initialDeposit' type='number' placeholder='0.00')
- step 4: Funding source selector exists (button role='combobox' inner_text='Select funding source' and a select element with account options is present)
- step 5: 'Open Account' submit button found (button type='submit' inner_text='Open Account')

**Notes:** All required UI elements for opening a Checking account are present on the Open New Account page; the test steps are executable.

---

#### ✅ Valid — TC-011: Funding account has insufficient balance for requested deposit
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/open-account

**✔ Valid Steps:**
- step 1: 'Checking' account type radio exists (input[type='radio'] alongside 'Checking' card)
- step 2: Initial Deposit Amount input exists to enter an amount (input#initialDeposit)
- step 3: Funding source selector exists (button role='combobox' inner_text='Select funding source' and a select with account options is present)
- step 4: 'Open Account' submit button found (button type='submit' inner_text='Open Account')

**⚠ Precondition Issues:**
- The test scenario implies an under-funded account must exist, but the visible account options in the DOM show large balances (Checking ****5001 $5,847.52 and Savings ****5002 $25,678.90). A funding account with insufficient balance is not present in the provided page data.

**Notes:** All UI controls referenced by the steps exist, but the page's account data does not include a low-balance account to reproduce the insufficient-balance scenario without test data setup.

---

#### ⚠️ Invalid Steps — TC-016: Funding account balance exactly equals deposit amount — boundary succeeds
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/open-account

**✔ Valid Steps:**
- step 1: Account type radio inputs exist (inputs for Checking and Savings present)
- step 2: Initial Deposit Amount input exists (input#initialDeposit)
- step 4: 'Open Account' submit button exists (button type='submit' inner_text='Open Account')

**⚠ Precondition Issues:**
- Precondition requires a funding account whose balance exactly equals the deposit amount X; the page's account options do not contain such an account.

**✘ Invalid Steps (referenced element NOT found in DOM):**
- step 3: 'Select the funding account with balance = X' — no funding account option with a balance exactly equal to a test deposit value X is present in the DOM. The available funding accounts show balances $5,847.52 and $25,678.90; an exact-match balance option is not present.

**Invalid Reason:** The step requiring selection of a funding account with an exact balance (balance == X) cannot be executed because no such account option is present in the DOM.

**Notes:** UI elements exist for selecting account type, entering deposit and submitting, but the specific data condition (funding account with balance exactly = X) is not present on the page, making the step unexecutable.

---

#### ✅ Valid — TC-018: Switching Account Type invalidates a previously valid deposit amount
**Type:** Edge/Interaction | **Priority:** Medium  
**URL:** http://localhost:8080/open-account

**✔ Valid Steps:**
- step 1: 'Checking' account type radio exists (input[type='radio'] and 'Checking' card present)
- step 2: Initial Deposit Amount input exists (input#initialDeposit) — can enter $25
- step 3: Funding source selector exists (button role='combobox' and select element with account options present) — a valid funding account can be chosen
- step 4: 'Savings' account type radio exists to change to (input[type='radio'] alongside 'Savings' card)

**Notes:** All UI controls needed to reproduce switching account type after entering a deposit are present. The real-time validation behavior after switching is dynamic and outside static DOM verification.

---

### Transfer Funds

#### ✅ Valid — TC-002: External transfer with matching account numbers succeeds
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/transfer

**✔ Valid Steps:**
- step 1: Navigate to Transfer Funds — Transfer Funds link present (a[href='/transfer'] text='Transfer Funds') and current page is /transfer
- step 2: Select External Account — radio input#external name='transferType' with label 'External Account' found
- step 3: Enter a valid transfer amount — amount input found (input#amount name='amount' type='number')
- step 4: Select a valid source account — source account combobox/select present (button role='combobox' text='Select source account' and corresponding select with account options)
- step 6: Click Transfer — Transfer button present (button[type='submit'] text='Transfer Funds')

**Notes:** All verifiable UI elements for an external transfer are present (amount input, source account selector, External Account radio, submit). The External Account Number and Confirm fields are not present in the static DOM — they appear to be conditional and therefore their presence is unverified but the trigger (External radio) exists.

---

#### ✅ Valid — TC-009: Transfer amount exceeds available balance
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/transfer

**✔ Valid Steps:**
- step 1: Select My ParaBank Account — radio input#internal name='transferType' with label 'My ParaBank Account' found
- step 2: Enter an amount exceeding the source account balance — amount input found (input#amount name='amount' type='number')
- step 3: Select the source account — source account combobox/select present (button role='combobox' text='Select source account' and select with account options)
- step 4: Select a destination account — destination account combobox/select present (button role='combobox' text='Select destination account' and select with account options)
- step 5: Click Transfer — Transfer button present (button[type='submit'] text='Transfer Funds')

**Notes:** All UI elements required by this negative test (radios, amount input, source/destination selectors, submit) are present. The insufficient-funds error is a runtime/backend outcome and cannot be verified from the static DOM.

---

#### ✅ Valid — TC-011: External account number and confirmation do not match
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/transfer

**✔ Valid Steps:**
- step 1: Select External Account — radio input#external name='transferType' with label 'External Account' found
- step 2: Enter a valid amount and source account — amount input (input#amount) and source account selector (button role='combobox' + select) found
- step 5: Click Transfer — Transfer button present (button[type='submit'] text='Transfer Funds')

**Notes:** Verifiable UI elements (External radio, amount input, source account selector, submit) exist. The External Account Number and Confirm fields referenced in steps 3–4 are not present in the static DOM (they are conditional), so those steps are unverifiable from this snapshot but the trigger (External Account radio) is available.

---

#### ✅ Valid — TC-012: Transfer amount exactly equals available balance succeeds
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/transfer

**✔ Valid Steps:**
- step 1: Select My ParaBank Account — radio input#internal name='transferType' with label 'My ParaBank Account' found
- step 2: Select source account — source account combobox/select present (button role='combobox' + select with accounts)
- step 3: Select destination account — destination account combobox/select present (button role='combobox' + select with accounts)
- step 4: Enter the exact available balance as transfer amount — amount input present (input#amount name='amount')
- step 5: Click Transfer — Transfer button present (button[type='submit'] text='Transfer Funds')

**Notes:** All UI controls needed for this boundary transfer are present. Verifying the post-submit balance change and success message is not possible from the static DOM.

---

#### ✅ Valid — TC-018: Browser Back after successful transfer does not create a duplicate
**Type:** Edge/Interaction | **Priority:** Medium  
**URL:** http://localhost:8080/transfer

**✔ Valid Steps:**
- step 3: Click Transfer again — Transfer button present (button[type='submit'] text='Transfer Funds')
- supporting: Form controls available that would be used in the flow — amount input (input#amount) and account selectors (source and destination combobox/select) are present

**Notes:** This test is a multi-step/browser-back interaction that cannot be fully verified from a static snapshot. The page does contain the transfer form controls and submit button, but completing a prior successful transfer, observing a transaction ID, and testing browser Back behavior are unverifiable here.

---

### Payments

#### ✅ Valid — TC-001: Submit bill payment happy path
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/bill-pay

**✔ Valid Steps:**
- step 1: Bill Pay page is present (nav link a[href='/bill-pay'] exists and page content shows 'Bill Pay')
- step 2: Payee Name input found (input#payeeName); Street Address input found (input#streetAddress); City input found (input#city); State combobox trigger found (button[role=combobox] text='Select state'); ZIP input found (input#zipCode); Phone input found (input#phoneNumber)
- step 3: Payee Account Number input found (input#payeeAccount) and Confirm Account Number input found (input#payeeAccountConfirm)
- step 4: Payment Amount input found (input#paymentAmount[type=number])
- step 5: Source account selector exists (button[role=combobox] text='Select source account' and select with account options present)
- step 6: Pay action/button found (button[type=submit] text='Pay Bill')

**⚠ Precondition Issues:**
- Precondition about source account having sufficient funds cannot be fully validated from the static DOM. Account balances are present in the source-account select text, but the test-specific comparison to the payment amount is data-dependent and not verifiable here.

**Notes:** All form fields and controls referenced by the steps exist on the page; post-submit outcomes (success message, balance update) are dynamic and not verifiable from this snapshot.

---

#### ✅ Valid — TC-008: Payee account number and confirmation do not match
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/bill-pay

**✔ Valid Steps:**
- step 1: Payee Account Number input found (input#payeeAccount)
- step 2: Confirm Account Number input found (input#payeeAccountConfirm)
- step 3: Pay action/button found (button[type=submit] text='Pay Bill')

**⚠ Precondition Issues:**
- Precondition that 'all other required fields are filled' cannot be confirmed from the static DOM; the inputs exist but their values/states are runtime data.

**Notes:** The inputs needed to enter mismatched account numbers and submit exist. The expected inline error is a runtime behavior and cannot be validated in the static snapshot.

---

#### ✅ Valid — TC-009: Insufficient funds in selected source account
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/bill-pay

**✔ Valid Steps:**
- step 1: Source account selector exists (button[role=combobox] text='Select source account' and select with account options present)
- step 2: Payment Amount input found (input#paymentAmount[type=number])
- step 3: Pay action/button found (button[type=submit] text='Pay Bill')

**⚠ Precondition Issues:**
- Precondition about selecting an under-funded account (balance < payment amount) cannot be fully validated from the static DOM. Account balances are present in the select text but the runtime balance comparison to the entered amount is data-dependent.

**Notes:** All UI controls referenced by the steps exist. The insufficient-funds error behavior is dynamic and not verifiable from the snapshot.

---

#### ✅ Valid — TC-012: Payment amount exactly equals available funds succeeds
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/bill-pay

**✔ Valid Steps:**
- step 1: Payment Amount input found (input#paymentAmount[type=number])
- step 2: Source account selector exists (button[role=combobox] text='Select source account' and select with account options present)
- step 3: Pay action/button found (button[type=submit] text='Pay Bill')

**⚠ Precondition Issues:**
- Precondition that a source account exists with an exact balance equal to the payment amount cannot be confirmed from the static DOM; balances are shown in the account select text but matching an exact test value is data/runtime-dependent.

**Notes:** Form fields and controls required to perform the boundary test exist. The success behavior and balance becoming zero are runtime effects not verifiable here.

---

#### ✅ Valid — TC-016: Browser Back after successful payment does not create duplicate
**Type:** Edge/Interaction | **Priority:** Medium  
**URL:** http://localhost:8080/bill-pay

**✔ Valid Steps:**
- step 1 (partial): The Pay action/button required to submit a payment exists (button[type=submit] text='Pay Bill')
- step 3: After navigation the Pay button to attempt a second submission would be present (button[type=submit] text='Pay Bill')

**⚠ Precondition Issues:**
- Steps that rely on post-submit confirmation (observing a reference code) and browser Back navigation are runtime/multi-step interactions and cannot be validated from this static DOM snapshot.
- Precondition about source account having at least 2× the payment amount cannot be fully verified from the static DOM; account balances are present in the source-account select text but exact comparisons are data-dependent.

**Notes:** The UI elements needed to submit (and re-submit) exist on the page. The multi-step behavior (preventing duplicate submission after browser Back) is interaction/state dependent and not verifiable from the static snapshot.

---

### Request Loan

#### ✅ Valid — TC-002: Request Auto Loan with collateral and approval
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/loan

**✔ Valid Steps:**
- step 1: Navigate to Request Loan — current page is Request Loan (/loan) (root shows Request Loan content)
- step 2: Select Auto — Auto Loan radio exists (h3 'Auto Loan' + input[type=radio])
- step 3: Enter a valid loan amount — Loan Amount input found (input#loanAmount)
- step 4: Enter a down payment — Down Payment input found (input#downPayment)
- step 5: Select a collateral account — collateral control exists (button role='combobox' text='Select collateral account' and a select with account options present)
- step 6: Click Request Loan — submit button exists (button[type=submit] text='Apply for Loan' — mapped to 'Request Loan')

**⚠ Precondition Issues:**
- Precondition 'Credit engine configured for approval' cannot be verified from the UI snapshot (external system).
- Precondition 'collateral account balance ≥ 20% of loan amount' is a data condition and cannot be validated from the static DOM (balances shown in select but whether they meet the specific percentage depends on runtime values).

**Notes:** All UI elements referenced by the steps exist (loan type radios, loan amount, down payment, collateral selector, submit). External preconditions (credit engine, exact collateral balance checks) are not verifiable from the page.

---

#### ✅ Valid — TC-007: Loan amount below type-specific minimum is rejected
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/loan

**✔ Valid Steps:**
- step 1: Select Personal — Personal Loan radio exists (h3 'Personal Loan' + input[type=radio])
- step 2: Enter an amount below $1,000 — Loan Amount input found (input#loanAmount)
- step 3: Enter a down payment — Down Payment input found (input#downPayment)
- step 4: Click Request Loan — submit button exists (button[type=submit] text='Apply for Loan')

**Notes:** All steps reference present controls. Validation outcome (inline error) is dynamic and not verifiable from static DOM.

---

#### ✅ Valid — TC-010: Down payment below 10 of loan amount is rejected
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/loan

**✔ Valid Steps:**
- step 1: Enter a valid loan amount — Loan Amount input found (input#loanAmount)
- step 2: Enter a down payment less than 10% — Down Payment input found (input#downPayment)
- step 3: Click Request Loan — submit button exists (button[type=submit] text='Apply for Loan')

**⚠ Precondition Issues:**
- Precondition requires 'Loan Type is selected' but the static DOM shows radio inputs with no checked attribute; selection state is not observable in this snapshot and therefore the precondition cannot be confirmed.

**Notes:** Inputs and submit button required by the steps are present. The precondition about a loan type already being selected is not verifiable from the DOM.

---

#### ✅ Valid — TC-017: Down payment exactly equals 10 of loan amount passes validation
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/loan

**✔ Valid Steps:**
- step 1: Select Home — Home Loan radio exists (h3 'Home Loan' + input[type=radio])
- step 2: Enter a loan amount within the Home range — Loan Amount input found (input#loanAmount)
- step 3: Enter down payment = 10% — Down Payment input found (input#downPayment)
- step 4: Click Request Loan — submit button exists (button[type=submit] text='Apply for Loan')

**Notes:** All UI controls referenced exist. The boundary validation behavior (exact 10%) is runtime logic and not verifiable from the static DOM.

---

#### ✅ Valid — TC-021: Collateral account balance one unit below 20 of loan amount is blocked
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/loan

**✔ Valid Steps:**
- step 1: Select any Loan Type — loan type radios exist (three input[type=radio] with corresponding h3 labels)
- step 2: Enter a valid loan amount — Loan Amount input found (input#loanAmount)
- step 3: Enter a valid down payment — Down Payment input found (input#downPayment)
- step 4: Select the under-collateralised account — collateral selector exists (button role='combobox' and select with account balances present)
- step 5: Click Request Loan — submit button exists (button[type=submit] text='Apply for Loan')

**⚠ Precondition Issues:**
- Precondition that a collateral account exists with balance exactly one unit below 20% of the loan amount cannot be verified from the static DOM; account balances are present but whether they match this specific condition is a runtime/data check.

**Notes:** All referenced UI elements are present. The specific balance edge-case precondition is data-dependent and not verifiable from the page snapshot.

---

### Update Contact Info

#### ✅ Valid — TC-004: Update First and Last Name and save successfully
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/profile

**✔ Valid Steps:**
- step 1: First Name input found (input#firstName name='firstName')
- step 2: Last Name input found (input#lastName name='lastName')
- step 3: Update Profile button found (button[type='submit'] text='Update Profile')

**Notes:** All interactive steps reference existing form controls on the Profile page; post-submit success message is dynamic and not verified here.

---

#### ✅ Valid — TC-005: Leave required field (First Name) blank and submit
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/profile

**✔ Valid Steps:**
- step 1: First Name input found and can be cleared (input#firstName name='firstName')
- step 2: (no UI interaction required) other fields present and pre-filled
- step 3: Update Profile button found (button[type='submit'] text='Update Profile')

**Notes:** Required-field negative test references existing inputs and submit button; inline error behavior is dynamic and not verifiable from the static DOM.

---

#### ✅ Valid — TC-007: Invalid phone number format
**Type:** Negative | **Priority:** Medium  
**URL:** http://localhost:8080/profile

**✔ Valid Steps:**
- step 1: Phone Number input found (input#phoneNumber name='phoneNumber')
- step 2: Update Profile button found (button[type='submit'] text='Update Profile')

**Notes:** Phone number field and submit button exist on the page; format validation and error highlighting are dynamic and not checked against the static DOM.

---

#### ✅ Valid — TC-012: Entering only whitespace into Last Name is treated as missing
**Type:** Edge/Input | **Priority:** Medium  
**URL:** http://localhost:8080/profile

**✔ Valid Steps:**
- step 1: Last Name input found and can be cleared/edited (input#lastName name='lastName')
- step 2: Update Profile button found (button[type='submit'] text='Update Profile')

**Notes:** Whitespace-edge case references existing Last Name input and submit button; enforcement of whitespace-as-empty is server/client validation and not visible in the static DOM.

---

### Manage Cards

#### ✅ Valid — TC-001: Submit card request with complete address and account in good standing
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/cards

**✔ Valid Steps:**
- step 1: Card Type options found (radio inputs present for Debit Card / Credit Card)
- step 2: Account to Link control found (combobox/button 'Select account' and underlying <select> with account options)
- step 3: Shipping Address input found (input#shippingAddress placeholder='Enter full shipping address')
- step 4: Request Card button found (button[type='submit'] text='Request Card')

**Notes:** All verifiable UI elements required to perform a card request (card type radios, account selector, shipping address input, Request Card button) are present on the page. Backend/state preconditions (account's 'good standing') cannot be validated from the DOM but do not block the steps' executability.

---

#### ✅ Valid — TC-008: Selected account is not in good standing
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/cards

**✔ Valid Steps:**
- step 1: Card Type options found (radio inputs present for Debit Card / Credit Card)
- step 2: Account selector found (combobox/button 'Select account' and underlying <select> with account options) — selecting an account UI is available
- step 3: Shipping Address input found (input#shippingAddress placeholder='Enter full shipping address')
- step 4: Request Card button found (button[type='submit'] text='Request Card')

**⚠ Precondition Issues:**
- Precondition requires an account that is NOT in good standing to exist and be selectable — the DOM shows account options but does not indicate account 'good standing' status, so that specific precondition cannot be verified from this snapshot.

**Notes:** All UI elements referenced by the steps exist. The specific data condition (an account not in good standing) is not discernible from the DOM and should be validated in test setup, but it doesn't make the steps un-executable.

---

#### ✅ Valid — TC-010: Travel Notice with Start Date after End Date is rejected
**Type:** Negative | **Priority:** Medium  
**URL:** http://localhost:8080/cards

**✔ Valid Steps:**
- step 1: Card Controls section and travel-notice fields are present (Select card combobox and travel notice area visible)
- step 2: Start Date and End Date inputs found (two input[type='date'] elements present)
- step 3: Update Controls button found (button[type='submit'] text='Update Controls')

**⚠ Precondition Issues:**
- Precondition requires an existing card to be selected in Card Controls. The page contains the 'Select card' control and card options, but the snapshot does not show a card already selected — the precondition's selected state cannot be confirmed from the DOM.

**Notes:** All UI elements needed to add a travel notice and submit (date inputs and Update Controls button) are present. Validation behavior (Start Date > End Date rejection) is dynamic and not verifiable from static DOM.

---

#### ✅ Valid — TC-014: Travel Notice where Start Date equals End Date is accepted
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/cards

**✔ Valid Steps:**
- step 1: Card Controls section and travel-notice fields are present (Select card combobox and travel notice area visible)
- step 2: Start Date and End Date inputs found (two input[type='date'] elements present)
- step 3: Update Controls button found (button[type='submit'] text='Update Controls')

**⚠ Precondition Issues:**
- Precondition requires an existing card to be selected in Card Controls. The control and card options exist but the DOM snapshot does not show a pre-selected card, so that selected-state precondition cannot be confirmed.

**Notes:** UI elements to enter matching Start and End dates and submit are present. Acceptance of Start Date == End Date is a dynamic validation result and cannot be confirmed from the static DOM.

---

### Investments

#### ✅ Valid — TC-001: Execute Buy trade with sufficient buying power
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/investments

**✔ Valid Steps:**
- step 1: Investments navigation link found (a[href='/investments'] text='Investments')
- step 2: 'Buy' action radio found (input#trade-Buy with corresponding label)
- step 3: Fund Symbol input found (input placeholder='Search funds...' and combobox/select for fund exist)
- step 4: Quantity input found (input#tradeQty)
- step 5: Funding account selector found (combobox button and select with account options present)
- step 6: Execute Trade button found (button[type=submit] text='Execute Trade')

**⚠ Precondition Issues:**
- Precondition 'funding account has sufficient buying power' cannot be validated from static DOM — account balances are shown in the select text but sufficiency relative to the trade cost is data-dependent.

**Notes:** All UI elements referenced by the test exist on the Investments page. The sufficiency of buying power is a runtime/data condition that cannot be verified from the DOM snapshot.

---

#### ✅ Valid — TC-013: Sell with quantity exceeding share balance is blocked
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/investments

**✔ Valid Steps:**
- step 1: 'Sell' action radio found (input#trade-Sell with corresponding label)
- step 2: Fund Symbol input found (input placeholder='Search funds...' and combobox/select for fund exist)
- step 3: Quantity input found (input#tradeQty)
- step 4: Destination/funding account selector found (combobox button and select with account options present)
- step 5: Execute Trade button found (button[type=submit] text='Execute Trade')

**⚠ Precondition Issues:**
- Precondition relies on knowing the user's current holding; the page displays holdings (Portfolio Snapshot) but whether a specific entered quantity exceeds the balance is a data/runtime check that cannot be validated from the static DOM.

**Notes:** All UI controls required to perform the Sell flow are present. The test's data-dependent condition (exceeding share balance) cannot be asserted from the snapshot.

---

#### ✅ Valid — TC-014: Recurring plan with Start Date in the past is rejected
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/investments

**✔ Valid Steps:**
- step 1: Recurring plan Fund Symbol selector present (combobox button and select for fund exist)
- step 2: Contribution Amount input found (input#contribution)
- step 3: Frequency options found (input#freq-Weekly and input#freq-Monthly with labels)
- step 4: Start Date input found (input#planStartDate)
- step 5: Funding account selector found (combobox button and select with account options present)
- step 6: Create Plan button found (button[type=submit] text='Create Plan')

**Notes:** The Recurring Investment Plan form and all referenced inputs are present on the page. Validation of a past date rejection is a runtime/server-side behavior not verifiable from DOM.

---

#### ✅ Valid — TC-023: Buy trade with funding account having exactly sufficient buying power succeeds
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/investments

**✔ Valid Steps:**
- step 1: 'Buy' action radio found (input#trade-Buy with corresponding label)
- step 2: Fund Symbol input found (input placeholder='Search funds...' and combobox/select for fund exist)
- step 3: Quantity input found (input#tradeQty)
- step 4: Funding account selector found (combobox button and select with account options present)
- step 5: Execute Trade button found (button[type=submit] text='Execute Trade')

**⚠ Precondition Issues:**
- Precondition that a funding account has buying power exactly equal to the trade cost cannot be validated from the static DOM — account balances are present in the select text but exact equality to computed trade cost is data-dependent.

**Notes:** All UI elements required for the buy flow are present. The exact buying-power == trade-cost boundary condition is a runtime/data check not determinable from the DOM snapshot.

---

### Account Statements

#### ⚠️ Invalid Steps — TC-002: Generate statement for a custom date range
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/statements

**✔ Valid Steps:**
- step 2: Start Date input found (input#startDate)
- step 2: End Date input found (input#endDate)
- step 3: Account selector present (button[role=combobox] text='Select account' and a backing <select> with account options)
- step 4: Generate Statement button found (button[type=submit] text='Generate Statement')

**✘ Invalid Steps (referenced element NOT found in DOM):**
- step 1: 'Select Custom date range from Statement Period' control not found — there is no Statement Period dropdown/radio or a 'Custom date range' option present in the DOM. Only Start Date/End Date inputs are shown.

**Notes:** Start/End date inputs, account selector, and Generate button exist and are verifiable. However the explicit 'Custom date range' selection control referenced in step 1 is not present in the DOM, so the test step is not executable as written.

---

#### ⚠️ Invalid Steps — TC-007: Custom date range with Start Date after End Date is rejected
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/statements

**✔ Valid Steps:**
- step 2: Start Date input found (input#startDate)
- step 2: End Date input found (input#endDate)
- step 3: Generate Statement button found (button[type=submit] text='Generate Statement')

**✘ Invalid Steps (referenced element NOT found in DOM):**
- step 1: 'Select Custom date range' control not found — there is no Statement Period control or explicit 'Custom date range' option in the DOM. Only the Start Date/End Date inputs are available.

**Notes:** Date inputs and Generate button exist so entering an invalid date order is possible, but the test's first step (selecting a 'Custom date range' option) references a control that does not exist on the page.

---

#### ⚠️ Invalid Steps — TC-011: Custom range where Start Date equals End Date is accepted
**Type:** Edge/Boundary | **Priority:** Medium  
**URL:** http://localhost:8080/statements

**✔ Valid Steps:**
- step 2: Start Date input found (input#startDate)
- step 2: End Date input found (input#endDate)
- step 3: Generate Statement button found (button[type=submit] text='Generate Statement')

**✘ Invalid Steps (referenced element NOT found in DOM):**
- step 1: 'Select Custom date range' control not found — DOM contains no Statement Period selector or explicit 'Custom date range' option; only Start Date and End Date fields are present.

**Notes:** Filling both date fields with the same date and clicking Generate is executable, but the explicit action to 'Select Custom date range' is not supported by any visible control on the page.

---

### Security Settings

#### ✅ Valid — TC-001: Change password with valid current password and strong new password
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/security

**✔ Valid Steps:**
- step 1: Expand the Change Password panel trigger found (div[type='button'] with inner_text='Change Password ▲', aria-expanded='true')
- step 2: Current Password input found (input#currentPw type='password')
- step 3: New Password input found (input#newPw type='password')
- step 4: Confirm New Password input found (input#confirmPw type='password')
- step 5: Change Password submit button found (button[type='submit'] inner_text='Change Password')

**Notes:** All verifiable UI elements required by this test (panel trigger, three password inputs, submit button) are present on the Security Settings page. Post-submit success notification is a runtime outcome and not verifiable from the static DOM.

---

#### ✅ Valid — TC-006: Incorrect current password prevents password change
**Type:** Negative | **Priority:** High  
**URL:** http://localhost:8080/security

**✔ Valid Steps:**
- step 1: Current Password input found (input#currentPw type='password')
- step 2: New Password input found (input#newPw type='password')
- step 3: Confirm New Password input found (input#confirmPw type='password')
- step 4: Change Password submit button found (button[type='submit'] inner_text='Change Password')

**Notes:** All UI elements referenced by the steps exist. The expected inline error after submission is a runtime behavior and cannot be verified from the static DOM.

---

#### ✅ Valid — TC-010: Browser Back after successful password change blocks resubmission with old password
**Type:** Edge/Interaction | **Priority:** Medium  
**URL:** http://localhost:8080/security

**✔ Valid Steps:**
- step 2: Current Password input found (input#currentPw type='password')
- step 2: Change Password submit button found (button[type='submit'] inner_text='Change Password')

**⚠ Precondition Issues:**
- Precondition requires a prior successful password change and a visible "Password changed successfully." notification; the current DOM snapshot does not show such a notification so that precondition/state cannot be confirmed from this page.
- Step 1 (press browser Back after success) is a browser navigation interaction dependent on prior session state and is unverifiable from the static DOM snapshot.

**Notes:** The page contains the Current Password input and the Change Password button required for the second step. The browser-back interaction and prior success state referenced in step 1 are not verifiable from this static DOM and therefore were not validated here. Runtime behavior after resubmission is also not verifiable.

---

### Support Center

#### ✅ Valid — TC-001: Send secure message with required Message Body only
**Type:** Positive | **Priority:** High  
**URL:** http://localhost:8080/support

**✔ Valid Steps:**
- step 1: Message Body textarea found (textarea#msgBody)
- step 2: Send Message button found (button[type=submit] text='Send Message')

**Notes:** All verifiable UI elements referenced in the test (Message Body and Send Message) are present on the Support Center page.

---

#### ✅ Valid — TC-016: Attachment with double extension (allowed  disallowed) is blocked
**Type:** Edge/Input | **Priority:** Low  
**URL:** http://localhost:8080/support

**✔ Valid Steps:**
- step 1: Subject input found (input#msgSubject) and Message Body textarea found (textarea#msgBody)
- step 2: Attachment input found (input#attachment) — file attachment control is present
- step 3: Send Message button found (button[type=submit] text='Send Message')

**Notes:** All referenced form controls (subject, message body, attachment input, and submit) are present. The file-rejection behavior is a post-submit validation and is not verifiable from the static DOM.

---
