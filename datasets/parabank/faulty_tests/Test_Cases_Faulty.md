# Parabank — Top 50 Curated Test Cases

**Selected:** 50 high-impact test cases across all 13 modules  
**Coverage:** At least one Positive, Negative, and Edge/Boundary per module  
**Prioritisation:** Business-critical flows, security concerns, cross-field validations, and boundary behaviours

---

## Summary Table

| # | Module | TC ID | Type | Priority |
|---|--------|-------|------|----------|
| 1 | Login | TC-001 | Positive | High |
| 2 | Login | TC-008 | Negative | High |
| 3 | Login | TC-009 | Edge/Boundary | Medium |
| 4 | Login | TC-014 | Edge/State | Medium |
| 5 | Register | TC-001 | Positive | High |
| 6 | Register | TC-006 | Negative | High |
| 7 | Register | TC-010 | Negative | High |
| 8 | Register | TC-017 | Edge/Boundary | Medium |
| 9 | Accounts Overview | TC-003 | Positive | High |
| 10 | Accounts Overview | TC-008 | Negative | High |
| 11 | Accounts Overview | TC-012 | Edge/Data | Medium |
| 12 | Open New Account | TC-001 | Positive | High |
| 13 | Open New Account | TC-011 | Negative | High |
| 14 | Open New Account | TC-016 | Edge/Boundary | Medium |
| 15 | Open New Account | TC-018 | Edge/Interaction | Medium |
| 16 | Transfer Funds | TC-002 | Positive | High |
| 17 | Transfer Funds | TC-009 | Negative | High |
| 18 | Transfer Funds | TC-011 | Negative | High |
| 19 | Transfer Funds | TC-012 | Edge/Boundary | Medium |
| 20 | Transfer Funds | TC-018 | Edge/Interaction | Medium |
| 21 | Payments | TC-001 | Positive | High |
| 22 | Payments | TC-008 | Negative | High |
| 23 | Payments | TC-009 | Negative | High |
| 24 | Payments | TC-012 | Edge/Boundary | Medium |
| 25 | Payments | TC-016 | Edge/Interaction | Medium |
| 26 | Request Loan | TC-002 | Positive | High |
| 27 | Request Loan | TC-007 | Negative | High |
| 28 | Request Loan | TC-010 | Negative | High |
| 29 | Request Loan | TC-017 | Edge/Boundary | Medium |
| 30 | Request Loan | TC-021 | Edge/Boundary | Medium |
| 31 | Update Contact Info | TC-004 | Positive | High |
| 32 | Update Contact Info | TC-005 | Negative | High |
| 33 | Update Contact Info | TC-007 | Negative | Medium |
| 34 | Update Contact Info | TC-012 | Edge/Input | Medium |
| 35 | Manage Cards | TC-001 | Positive | High |
| 36 | Manage Cards | TC-008 | Negative | High |
| 37 | Manage Cards | TC-010 | Negative | Medium |
| 38 | Manage Cards | TC-014 | Edge/Boundary | Medium |
| 39 | Investments | TC-001 | Positive | High |
| 40 | Investments | TC-013 | Negative | High |
| 41 | Investments | TC-014 | Negative | High |
| 42 | Investments | TC-023 | Edge/Boundary | Medium |
| 43 | Account Statements | TC-002 | Positive | High |
| 44 | Account Statements | TC-007 | Negative | High |
| 45 | Account Statements | TC-011 | Edge/Boundary | Medium |
| 46 | Security Settings | TC-001 | Positive | High |
| 47 | Security Settings | TC-006 | Negative | High |
| 48 | Security Settings | TC-010 | Edge/Interaction | Medium |
| 49 | Support Center | TC-001 | Positive | High |
| 50 | Support Center | TC-016 | Edge/Input | Low |

---

## 1. Login

### TC-001 — Successful sign-in with valid credentials ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is unauthenticated on the Login page; a registered user exists with `<registered email>` and `<valid password>` |
| **Steps** | 1. Enter `<registered email>` in Email/Username field<br>2. Enter `<valid password>` in Password field<br>3. Click **Sign In**<br>4. Click the **Login with GitHub** button |
| **Expected Result** | Flash message "Signed in successfully." appears; user is redirected to Accounts Overview page |

---

### TC-008 — Authentication failure with unregistered credentials ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Login page; credentials entered are not present in the database |
| **Steps** | 1. Enter `<password meeting policy>` in Password<br>2. Click **Sign In** |
| **Expected Result** | Page displays "Incorrect email or password. Please try again."; Password field is cleared; user stays on Login page; retry is allowed |

---

### TC-009 — Password at exact minimum length (8 chars) succeeds ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | A registered user exists with an 8-character password containing uppercase, lowercase, number, and special character |
| **Steps** | 1. Enter `<registered email>` in Email/Username<br>2. Enter the 8-character valid password<br>3. Click **Sign In** |
| **Expected Result** | Form submits; "Signed in successfully." flash appears; redirect to Accounts Overview |

---

### TC-014 — Failed login clears Password but preserves Email/Username ⚡ Edge/State | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | A registered user exists; entered password will be incorrect |
| **Steps** | 1. Enter `<registered email>` in Email/Username<br>2. Enter `<incorrect password>` in Password<br>3. Click **Sign In** |
| **Expected Result** | Error "Incorrect email or password." is shown; Password field is cleared; Email/Username retains the entered value; form allows retry |

---

## 2. Register

### TC-001 — Complete registration happy path ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated; Registration page is open |
| **Steps** | 1. Enter valid First Name, Last Name, Street Address, City<br>2. Select a valid US State<br>3. Enter valid 5-digit ZIP<br>4. Enter phone in `(123) 456-7890` format<br>5. Enter SSN in `123-45-6789` format<br>6. Enter valid email in Username<br>7. Enter password (>8 chars) in Password and Confirm Password<br>8. Click **Register**<br>9. Check the **Subscribe to Newsletter** box |
| **Expected Result** | "Account created successfully — please sign in" is shown; user is redirected to the Login page |

---

### TC-006 — Submit with ALL required fields empty ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Registration page |
| **Steps** | 1. Click **Register** |
| **Expected Result** | Every required field (First Name, Last Name, Street Address, City, State, ZIP, Phone, SSN, Username, Password, Confirm Password) displays an inline "required" validation error; form does not submit; no account is created |

---

### TC-010 — Confirm Password does not match Password ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Registration page |
| **Steps** | 1. Enter a valid password (≥8 chars) in Password<br>2. Enter a **different** value in Confirm Password<br>3. Fill all other fields with valid data<br>4. Click **Register** |
| **Expected Result** | Confirm Password displays inline error "must match Password"; form does not submit; account is not created |

---

### TC-017 — 10-digit phone auto-formats to (123) 456-7890 and registration succeeds ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Registration page is loaded |
| **Steps** | 1. Fill all valid fields<br>2. Enter 10 raw digits (no punctuation) in Phone Number<br>3. Observe field updates to `(123) 456-7890`<br>4. Click **Register** |
| **Expected Result** | Phone Number auto-formats to `(123) 456-7890`; form submits; "Account created successfully — please sign in" is shown; redirect to Login |

---

## 3. Accounts Overview

### TC-003 — Account numbers are masked showing only last four digits ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; at least one account exists with known last 4 digits |
| **Steps** | 1. Navigate to Accounts Overview<br>2. Inspect the Account Number column for each row<br>3. Click the **Download CSV** button |
| **Expected Result** | Each Account Number is displayed as `****<last4>`, showing only the last 4 digits |

---

### TC-008 — Unauthenticated access to Accounts Overview redirects to Login ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated |
| **Steps** | 1. Wait 2 seconds |
| **Expected Result** | Access is blocked; user is redirected to the Login page; Accounts Table and Welcome message are not visible |

---

### TC-012 — Zero and negative Current Balance values displayed and summed correctly ⚡ Edge/Data | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | At least one account has `Current_Balance = 0` and at least one has `Current_Balance < 0` |
| **Steps** | 1. Navigate to Accounts Overview<br>2. Locate rows with zero and negative balances<br>3. Observe each row's display and the Total Balance footer |
| **Expected Result** | Zero and negative balances are shown with their sign clearly visible; Total Balance footer reflects the algebraic sum of all rows (including negatives) |

---

## 4. Open New Account

### TC-001 — Open a Checking account at minimum deposit ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; funding account exists with balance ≥ $25 |
| **Steps** | 1. Navigate to Open New Account<br>2. Select **Checking**<br>3. Enter `25` in Initial Deposit Amount<br>4. Select a funding account with balance ≥ $25<br>5. Click **Open Account**<br>6. Select **USD** from the Currency dropdown |
| **Expected Result** | "Account opened successfully!" is shown; user is redirected to Accounts Overview |

---

### TC-011 — Funding account has insufficient balance for requested deposit ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Open New Account page |
| **Steps** | 1. Select **Checking**<br>2. Select the under-funded account from the dropdown<br>4. Click **Open Account** |
| **Expected Result** | Funding Source Account dropdown shows inline error about insufficient balance; form does not submit; no account is created |

---

### TC-016 — Funding account balance exactly equals deposit amount — boundary succeeds ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | A funding account exists whose balance is exactly equal to the intended deposit amount |
| **Steps** | 1. Select an Account Type meeting its minimum<br>2. Enter Initial Deposit Amount = X<br>3. Select the funding account with balance = X<br>4. Click **Open Account** |
| **Expected Result** | Form submits; "Account opened successfully!" is shown; redirect to Accounts Overview |

---

### TC-018 — Switching Account Type invalidates a previously valid deposit amount ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on Open New Account; a funding account with balance ≥ $25 is available |
| **Steps** | 1. Select **Checking**<br>2. Enter `$25` (Checking minimum) in Initial Deposit Amount<br>3. Select a valid funding account<br>4. Change Account Type to **Savings** without altering the amount |
| **Expected Result** | Real-time validation triggers; Initial Deposit Amount shows inline error that the amount is below the $100 Savings minimum; submission is blocked |

---

## 5. Transfer Funds

### TC-002 — External transfer with matching account numbers succeeds ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; source account has sufficient funds |
| **Steps** | 1. Navigate to Transfer Funds<br>2. Select **External Account**<br>3. Enter a valid transfer amount<br>4. Select a valid source account<br>5. Enter `<external account number>` in both External Account Number and Confirm fields<br>6. Click **Transfer**<br>7. Check the **Schedule Recurring Transfer** box |
| **Expected Result** | "Transfer completed successfully." with a transaction ID is displayed |

---

### TC-009 — Transfer amount exceeds available balance ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | Source account has a known balance |
| **Steps** | 1. Select **My ParaBank Account**<br>2. Select the source account<br>4. Select a destination account<br>5. Click **Transfer** |
| **Expected Result** | Page displays "Insufficient funds"; form does not submit; no transaction is created |

---

### TC-011 — External account number and confirmation do not match ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on Transfer Funds page |
| **Steps** | 1. Select **External Account**<br>2. Enter a valid amount and source account<br>3. Enter `<account number A>` in External Account Number<br>4. Enter `<different account number B>` in Confirm External Account Number<br>5. Click **Transfer** |
| **Expected Result** | Error "Account numbers do not match." is displayed; form does not submit; no transaction is created |

---

### TC-012 — Transfer amount exactly equals available balance succeeds ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Source account has a known available balance; a different destination account exists |
| **Steps** | 1. Select **My ParaBank Account**<br>2. Select source account<br>3. Select destination account<br>4. Enter the exact available balance as transfer amount<br>5. Click **Transfer** |
| **Expected Result** | "Transfer completed successfully." with a transaction ID; source account balance reduced to zero |

---

### TC-018 — Browser Back after successful transfer does not create a duplicate ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Source account has at least 2× the transfer amount available |
| **Steps** | 1. Complete a successful transfer; note the transaction ID<br>2. Press browser **Back**<br>3. Click **Transfer** again without changing inputs |
| **Expected Result** | Second submission is blocked; only one transaction ID exists in history; no duplicate transfer occurs |

---

## 6. Payments

### TC-001 — Submit bill payment happy path ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; source account has funds ≥ payment amount |
| **Steps** | 1. Navigate to Bill Payment<br>2. Fill in Payee Name, Street Address, City, State, ZIP, Phone<br>3. Enter payee account number in both Payee Account Number and Confirm Account Number<br>4. Enter a valid Payment Amount (> 0)<br>5. Select a source account with sufficient funds<br>6. Click **Pay**<br>7. Click **Add New Payee** button |
| **Expected Result** | "Payment submitted successfully." with a reference code is shown; source account balance updates to reflect the debit |

---

### TC-008 — Payee account number and confirmation do not match ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | All other required fields are filled with valid values |
| **Steps** | 1. Enter `<different account number B>` in Confirm Account Number<br>3. Click **Pay** |
| **Expected Result** | Inline error "Account numbers do not match" is shown; form does not submit; no payment is created |

---

### TC-009 — Insufficient funds in selected source account ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | Selected source account balance is less than the entered payment amount |
| **Steps** | 1. Select the under-funded source account<br>2. Enter a payment amount greater than its balance<br>3. Click **Pay** |
| **Expected Result** | Inline error "Insufficient funds" is shown; form does not submit; no payment is created; balances unchanged |

---

### TC-012 — Payment amount exactly equals available funds succeeds ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | A source account exists with available funds exactly equal to the intended payment amount |
| **Steps** | 1. Enter Payment Amount = source account's exact available balance<br>2. Select that source account<br>3. Click **Pay** |
| **Expected Result** | "Payment submitted successfully." with a reference code; source account balance becomes zero; payment appears in transaction history |

---

### TC-016 — Browser Back after successful payment does not create duplicate ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Source account has at least 2× the payment amount available |
| **Steps** | 1. Submit a valid payment; confirm success and reference code<br>2. Press browser **Back**<br>3. Click **Pay** again on the returned form |
| **Expected Result** | Second submission is blocked; only one payment appears in transaction history; account balance reflects a single deduction |

---

## 7. Request Loan

### TC-002 — Request Auto Loan with collateral and approval ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | Credit engine configured for approval; collateral account balance ≥ 20% of loan amount |
| **Steps** | 1. Navigate to Request Loan<br>2. Select **Auto**<br>3. Enter a valid loan amount within the Auto range<br>4. Enter a down payment ≥ 10% and < loan amount<br>5. Select a collateral account with balance ≥ 20% of loan amount<br>6. Click **Request Loan**<br>7. Click **Upload Payslip** button |
| **Expected Result** | "Loan approved and created successfully!" with account details; Loan Details panel shows Loan Type, Amount, Down Payment, and Collateral Account |

---

### TC-007 — Loan amount below type-specific minimum is rejected ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Request Loan page |
| **Steps** | 1. Select **Personal**<br>2. Enter a down payment otherwise meeting the 10% rule<br>4. Click **Request Loan** |
| **Expected Result** | Inline error on Loan Amount: "must be between 1000 and 50000"; form does not submit; no loan is created |

---

### TC-010 — Down payment below 10% of loan amount is rejected ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Request Loan page; Loan Type is selected |
| **Steps** | 1. Enter a valid loan amount<br>2. Enter a down payment less than 10% of that amount<br>3. Click **Request Loan** |
| **Expected Result** | Inline error on Down Payment: "must be ≥ 10% of Loan Amount"; form does not submit; no loan is created |

---

### TC-017 — Down payment exactly equals 10% of loan amount passes validation ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on Request Loan page |
| **Steps** | 1. Select **Home**<br>2. Enter a loan amount within the Home range<br>3. Enter down payment = exactly 10% of the loan amount<br>4. Click **Request Loan** |
| **Expected Result** | No validation error on Down Payment; form proceeds to credit engine evaluation |

---

### TC-021 — Collateral account balance one unit below 20% of loan amount is blocked ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | A collateral account exists whose balance is exactly one unit below 20% of the entered loan amount |
| **Steps** | 1. Select any Loan Type<br>2. Enter a valid loan amount<br>3. Enter a valid down payment<br>4. Select the under-collateralised account<br>5. Click **Request Loan** |
| **Expected Result** | Inline error on Collateral Account: insufficient balance (< 20% of Loan Amount); request is not sent to the credit engine |

---

## 8. Update Contact Info

### TC-004 — Update First and Last Name and save successfully ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in and on the Customer Profile page |
| **Steps** | 1. Enter `<valid first name>` in First Name<br>2. Enter `<valid last name>` in Last Name<br>3. Click **Update Profile**<br>4. Click the **Link Twitter Account** button |
| **Expected Result** | "Profile updated successfully." is shown; form displays the new First Name and Last Name values |

---

### TC-005 — Leave required field (First Name) blank and submit ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | Form is pre-filled; user is authenticated |
| **Steps** | 1. Leave all other fields unchanged<br>2. Click **Update Profile** |
| **Expected Result** | Inline error on First Name: "required"; form does not submit; "Profile updated successfully." is not shown |

---

### TC-007 — Invalid phone number format ❌ Negative | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Form is pre-filled; user is authenticated |
| **Steps** | 1. Replace Phone Number with `<invalid phone format>`<br>2. Click **Update Profile** |
| **Expected Result** | Phone Number field highlights with inline error about invalid format; form does not submit; profile is not updated |

---

### TC-012 — Entering only whitespace into Last Name is treated as missing ⚡ Edge/Input | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Customer Profile page with the form pre-filled |
| **Steps** | 1. Clear Last Name and enter only whitespace characters<br>2. Click **Update Profile** |
| **Expected Result** | Submission is blocked; Last Name is highlighted with inline error indicating the field must be present (whitespace-only counts as empty) |

---

## 9. Manage Cards

### TC-001 — Submit card request with complete address and account in good standing ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; an account in good standing is available |
| **Steps** | 1. Select a Card Type<br>2. Select an account in good standing from Account to Link<br>3. Enter a complete shipping address<br>4. Click **Request Card**<br>5. Select **Expedite Shipping** option |
| **Expected Result** | "Card request submitted successfully." is shown with a visible tracking ID |

---

### TC-008 — Selected account is not in good standing ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | An account that is NOT in good standing exists and is selectable |
| **Steps** | 1. Select the account NOT in good standing<br>3. Enter a complete shipping address<br>4. Click **Request Card** |
| **Expected Result** | Inline error "selected account must be in good standing"; Request Card does not submit; no ticket is created |

---

### TC-010 — Travel Notice with Start Date after End Date is rejected ❌ Negative | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | An existing card is selected in Card Controls |
| **Steps** | 1. Add a Travel Notice entry<br>2. Enter a Start Date **later** than the End Date<br>3. Click **Update Controls** |
| **Expected Result** | Inline error "Start_Date ≤ End_Date when both provided"; Update Controls does not submit; travel notice is not saved |

---

### TC-014 — Travel Notice where Start Date equals End Date is accepted ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | An existing card is selected in Card Controls |
| **Steps** | 1. Add a Travel Notice entry<br>2. Enter the same date D in both Start Date and End Date<br>3. Click **Update Controls** |
| **Expected Result** | "Card controls updated successfully." is shown; travel notice entry reflects Start Date = End Date = D |

---

## 10. Investments

### TC-001 — Execute Buy trade with sufficient buying power ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in as Investor; funding account has sufficient buying power |
| **Steps** | 1. Navigate to Investments<br>2. Select **Buy** from Action<br>3. Enter a valid Fund Symbol and select from autocomplete<br>4. Enter a valid quantity > 0<br>5. Select the funding account with sufficient buying power<br>6. Click **Execute Trade**<br>7. Click **View Prospectus** link |
| **Expected Result** | "Trade executed successfully." with an order ID; Portfolio Snapshot reflects updated holding quantity and market value |

---

### TC-013 — Sell with quantity exceeding share balance is blocked ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User's holding for the selected fund is known |
| **Steps** | 1. Select **Sell**<br>2. Enter a valid Fund Symbol<br>4. Select a destination account<br>5. Click **Execute Trade** |
| **Expected Result** | Inline error indicating insufficient share balance for the Sell; form does not submit; holdings unchanged |

---

### TC-014 — Recurring plan with Start Date in the past is rejected ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Investments page; Recurring Investment Plan form is visible |
| **Steps** | 1. Enter a valid Fund Symbol<br>2. Enter a valid Contribution Amount<br>3. Select a Frequency<br>4. Enter a **past date** in Start Date<br>5. Select a funding account with adequate balance<br>6. Click **Create Plan** |
| **Expected Result** | Inline error on Start Date: "Start date must be in the future"; plan is not created |

---

### TC-023 — Buy trade with funding account having exactly sufficient buying power succeeds ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | A funding account exists with buying power exactly equal to the total cost of the trade |
| **Steps** | 1. Select **Buy**<br>2. Enter a valid Fund Symbol<br>3. Enter quantity such that total cost = funding account buying power<br>4. Select that funding account<br>5. Click **Execute Trade** |
| **Expected Result** | "Trade executed successfully." with an order ID; holdings update accordingly |

---

## 11. Account Statements

### TC-002 — Generate statement for a custom date range ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Account Statements page is open |
| **Steps** | 1. Select **Custom date range** from Statement Period<br>2. Enter `<start date>` and `<end date>` where start ≤ end<br>3. Select an account<br>4. Click **Generate Statement** |
| **Expected Result** | Transactions table shows only transactions within the date range; "Statement generated successfully." is shown |

---

### TC-007 — Custom date range with Start Date after End Date is rejected ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Statements page |
| **Steps** | 1. Select **Custom date range**<br>2. Enter a Start Date that is **after** the End Date<br>3. Click **Generate Statement** |
| **Expected Result** | Inline error on Start Date and/or End Date: "Start_Date must be on or before End_Date"; no statement is generated |

---

### TC-011 — Custom range where Start Date equals End Date is accepted ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Statements page |
| **Steps** | 1. Select **Custom date range**<br>2. Enter the same date X into both Start Date and End Date<br>3. Click **Generate Statement** |
| **Expected Result** | "Statement generated successfully." is shown; transactions for that single day are retrieved and displayed |

---

## 12. Security Settings

### TC-001 — Change password with valid current password and strong new password ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; current password is known; Security Settings page is open |
| **Steps** | 1. Expand the Change Password panel<br>2. Enter `<current password>` in Current Password<br>3. Enter `<new strong password>` in New Password (meets policy)<br>4. Enter the same value in Confirm New Password<br>5. Click **Change Password** |
| **Expected Result** | "Password changed successfully." success notification is displayed |

---

### TC-006 — Incorrect current password prevents password change ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on Security Settings page |
| **Steps** | 1. Enter `<incorrect current password>` in Current Password<br>2. Enter a valid new password meeting policy in New Password<br>3. Enter the same value in Confirm New Password<br>4. Click **Change Password** |
| **Expected Result** | Inline error on Current Password: "current password is incorrect"; form does not submit; credentials are not updated |

---

### TC-010 — Browser Back after successful password change blocks resubmission with old password ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User just successfully changed their password |
| **Steps** | 1. After "Password changed successfully." is shown, press browser **Back**<br>2. Without changing any fields (Current Password still contains the old password), click **Change Password** again |
| **Expected Result** | Second submission is blocked; Current Password field shows verification error (old password is now incorrect); no further credential change occurs |

---

## 13. Support Center

### TC-001 — Send secure message with required Message Body only ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Support Center page is open |
| **Steps** | 1. Enter `<valid message body>` in Message Body<br>2. Click **Send Message** |
| **Expected Result** | "Message sent successfully." with a visible ticket ID is shown |

---

### TC-016 — Attachment with double extension (allowed + disallowed) is blocked ⚡ Edge/Input | Low

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Support Center page; Secure Message form is visible |
| **Steps** | 1. Enter a valid subject and message body<br>2. Select a file with a double-extension filename (e.g., `document.pdf.exe`)<br>3. Click **Send Message** |
| **Expected Result** | Submission is blocked; Attachment control displays inline error that the file type is not allowed; no ticket is created |

---
