# SwagLabs Faulty Test Cases: Bug Report

This document details the 20 intentional faults injected into `faulty_tests/Test_Cases_Faulty.md`. 
The framework's `TestStepVerifierAgent` is expected to catch these errors when auditing the test suite against the live DOM.

## Category A: Invalid Steps (Hallucinations)
These test cases command the agent to interact with UI elements that **do not exist**. The agent should flag them as `INVALID_STEPS`.

| # | Test Case ID | Module | Injected Invalid Step |
|---|--------------|--------|-----------------------|
| 1 | TC-001 | Login | Click the **Remember Me** checkbox |
| 2 | TC-007 | Login | Click **Login with Google** |
| 3 | TC-001 | Product Inventory | Select **Electronics** from the Category sidebar |
| 4 | TC-002 | Product Inventory | Click the **Export to PDF** button |
| 5 | TC-001 | Product Detail | Click the **Read Customer Reviews** link |
| 6 | TC-002 | Product Detail | Click **Share on Twitter** |
| 7 | TC-001 | Shopping Cart | Enter 'SAVE20' in the **Apply Discount Code** field |
| 8 | TC-001 | Checkout - Information | Enter a valid email in the **Email Address** field |
| 9 | TC-001 | Checkout - Overview | Select **Express Delivery** from the Shipping Method dropdown |
| 10 | TC-001 | Logout | Click **Confirm** on the Logout Confirmation Modal |

## Category B: Missing Steps (Omissions)
These test cases omit a crucial prerequisite step, making it impossible to successfully execute the test as written. The agent should flag them as `MISSING_STEPS` or `PRECONDITION_ISSUES`.

| # | Test Case ID | Module | Omitted Prerequisite Step |
|---|--------------|--------|---------------------------|
| 11 | TC-011 | Login | Removed entering password |
| 12 | TC-012 | Login | Removed entering username |
| 13 | TC-003 | Product Inventory | Removed clicking Remove button |
| 14 | TC-008 | Product Inventory | Removed first Add to cart click |
| 15 | TC-003 | Product Detail | Removed clicking Back to products |
| 16 | TC-002 | Shopping Cart | Removed clicking Continue Shopping |
| 17 | TC-006 | Checkout - Information | Removed clicking Cancel |
| 18 | TC-002 | Checkout - Overview | Removed clicking Cancel |
| 19 | TC-002 | Checkout - Confirmation | Removed clicking Back Home |
| 20 | TC-002 | Logout | Removed clicking Logout |

## Expected Outcome
The framework should successfully identify these 20 broken test cases, separating them into `INVALID_STEPS` and `MISSING_STEPS` verdicts during the audit pipeline.
