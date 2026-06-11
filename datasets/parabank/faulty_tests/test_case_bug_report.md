# ParaBank Faulty Test Cases: Bug Report

This document details the 20 intentional faults injected into `faulty_tests/Test_Cases_Faulty.md`. 
The framework's `TestStepVerifierAgent` is expected to catch these errors when auditing the test suite against the live DOM.

## Category A: Invalid Steps (Hallucinations)
These test cases command the agent to interact with UI elements that **do not exist**. The agent should flag them as `INVALID_STEPS`.

| # | Test Case ID | Module | Injected Invalid Step |
|---|--------------|--------|-----------------------|
| 1 | TC-001 | Login | Click the **Login with GitHub** button |
| 2 | TC-001 | Register | Check the **Subscribe to Newsletter** box |
| 3 | TC-003 | Accounts Overview | Click the **Download CSV** button |
| 4 | TC-001 | Open New Account | Select **USD** from the Currency dropdown |
| 5 | TC-002 | Transfer Funds | Check the **Schedule Recurring Transfer** box |
| 6 | TC-001 | Payments | Click **Add New Payee** button |
| 7 | TC-002 | Request Loan | Click **Upload Payslip** button |
| 8 | TC-004 | Update Contact Info | Click the **Link Twitter Account** button |
| 9 | TC-001 | Manage Cards | Select **Expedite Shipping** option |
| 10 | TC-001 | Investments | Click **View Prospectus** link |

## Category B: Missing Steps (Omissions)
These test cases omit a crucial prerequisite step, making it impossible to successfully execute the test as written. The agent should flag them as `MISSING_STEPS` or `PRECONDITION_ISSUES`.

| # | Test Case ID | Module | Omitted Prerequisite Step |
|---|--------------|--------|---------------------------|
| 11 | TC-008 | Login | Removed entering email |
| 12 | TC-006 | Register | Removed leaving fields blank |
| 13 | TC-008 | Accounts Overview | Removed navigation step |
| 14 | TC-011 | Open New Account | Removed entering deposit amount |
| 15 | TC-009 | Transfer Funds | Removed entering transfer amount |
| 16 | TC-008 | Payments | Removed entering payee account number |
| 17 | TC-007 | Request Loan | Removed entering loan amount |
| 18 | TC-005 | Update Contact Info | Removed clearing the first name field |
| 19 | TC-008 | Manage Cards | Removed selecting card type |
| 20 | TC-013 | Investments | Removed entering quantity |

## Expected Outcome
The framework should successfully identify these 20 broken test cases, separating them into `INVALID_STEPS` and `MISSING_STEPS` verdicts during the audit pipeline.
