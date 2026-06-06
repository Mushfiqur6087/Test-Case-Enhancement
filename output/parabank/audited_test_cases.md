# Audited Test Cases

## TC-001 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All interactive elements required by the test (username, password, Sign In) are present on the page. Post-submit outcomes are dynamic and not verified here.

## TC-008 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Elements to enter credentials and submit are present. The expected error message and field-clear behaviour are dynamic and not verifiable from the static DOM.

## TC-009 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All required inputs and the submit button exist. Whether an 8-character password succeeds is a runtime/backend validation not verifiable here.

## TC-014 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** The test's interactive steps map to existing inputs and the submit button. The post-failure state requirements (password cleared, email preserved) are dynamic and cannot be confirmed from the static DOM.

## TC-001 - VALID
- **Valid Steps:** 8
- **Invalid Steps:** 0
- **Notes:** All verifiable UI elements required for the happy-path registration exist on the page. Post-submit outcomes (success message / redirect) are dynamic and therefore not verified here.

## TC-006 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All fields referenced by the negative test exist on the page and the Register button is present. Inline validation errors are runtime behavior and are not verifiable from the static DOM.

## TC-010 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** Password and confirm fields exist so the mismatch scenario can be executed. The inline error behavior is dynamic and not checked in the static DOM.

## TC-017 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** The phone input exists and can accept raw digits; the auto-format observation (step 3) is a dynamic behavior and cannot be verified from the static DOM snapshot.

## TC-003 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable steps reference UI elements present on the Accounts Overview page; account numbers are shown masked in the DOM.

## TC-008 - INVALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Reason:** The page snapshot shows an authenticated session; the negative test (unauthenticated redirect) cannot be validated from this state.
- **Notes:** The navigation step is present, but the precondition (user not authenticated) is not met on the live page, so the expected redirect to Login cannot be verified.

## TC-012 - INVALID_STEPS
- **Valid Steps:** 3
- **Invalid Steps:** 1
- **Notes:** Negative balances and the Total Balance footer are present and verifiable, but the required zero-balance account is missing from the page, so the test cannot fully execute as written.

## TC-001 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All UI elements required by the test (account type radios, deposit input, funding combobox, submit) are present on the Open New Account page; runtime/data-dependent preconditions (funding account balance) are external and not verifiable from the DOM.

## TC-011 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All referenced controls for selecting account type, entering deposit, choosing funding source, and submitting are present. The expected inline error on insufficient funds is a runtime behavior and not verifiable from the static DOM.

## TC-016 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** UI elements required by the test are present. The existence of a funding account with an exact balance X is an external data precondition and cannot be confirmed from the DOM.

## TC-018 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All interactive elements required to reproduce the interaction (select Checking, enter amount, choose funding source, switch to Savings) are present. The real-time validation behavior after switching is dynamic and cannot be verified from this static DOM.

## TC-002 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All interactive controls required by the test are present (amount input, source combobox, external account radio, submit). The External Account Number and Confirm fields referenced in step 5 are not present in the static DOM — they are likely conditional and would appear after selecting External Account; this is unverifiable from this snapshot but the trigger (radio) exists.

## TC-009 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All verifiable UI elements mentioned in the steps exist on the page (radios, amount input, source/destination comboboxes, submit). Balance-related behaviour is backend/dynamic and is not verifiable from the static DOM.

## TC-011 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** The External Account Number and Confirm External Account Number fields referenced in steps 3–4 do not appear in the static DOM; they are likely conditional (shown after selecting External Account). The trigger radio exists, so these steps are conditional/unverifiable from this snapshot but not flagged as invalid.

## TC-012 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All UI elements required by the steps exist. Validation of exact-balance transfer and balance changes are runtime/back-end behaviours and cannot be verified from the static DOM.

## TC-018 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** The page contains the Transfer button used in step 3. Steps that depend on prior successful submission and browser history are not verifiable from the snapshot and are therefore ignored for element existence checks; no UI elements referenced by the test are missing.

## TC-001 - VALID
- **Valid Steps:** 12
- **Invalid Steps:** 0
- **Notes:** All verifiable UI elements required by the happy-path steps exist on the Bill Pay page. Post-submit outcomes (success message, reference code, balance update) are dynamic and cannot be verified from the static DOM.

## TC-008 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Both account number fields and the Pay button exist. The expected inline validation message is a dynamic post-interaction result and cannot be validated from the static DOM.

## TC-009 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All UI elements required to perform the steps exist. The insufficient-funds error is a runtime/backend validation and is not verifiable from this snapshot.

## TC-012 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Inputs and selectors required for the boundary test are present. Success and balance-change outcomes are dynamic and not verifiable here.

## TC-016 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** The Pay button required for submitting is present. However, the multi-step interaction (submit -> confirm success/reference -> press browser Back -> re-submit) and the uniqueness check after navigating back are runtime/browser-flow behaviours and cannot be verified from this static DOM snapshot; those steps are therefore unverifyable here.

## TC-002 - VALID
- **Valid Steps:** 6
- **Invalid Steps:** 0
- **Notes:** All UI elements required by the steps (loan type radios, loanAmount, downPayment, collateral selector, submit) exist on the page. Credit-engine and account-balance preconditions are not verifiable from this snapshot.

## TC-007 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All UI elements referenced in the steps are present. Inline validation messages and submission outcome are dynamic and not verifiable from the static DOM.

## TC-010 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Inputs and submit button required by the test exist. The precondition that a loan type is already selected is not observable in the static DOM but the radio controls are available to satisfy it at runtime.

## TC-017 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All UI elements required by the steps are present. Exact validation behavior (no error) after submission is dynamic and not verifiable from this snapshot.

## TC-021 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All UI controls needed to perform the steps exist. Account balances and the edge-case precondition cannot be confirmed from the provided DOM.

## TC-004 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable UI elements (first name, last name inputs and Update Profile button) exist on the Profile page. Post-submit success message is dynamic and therefore not verifiable from the static DOM.

## TC-005 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All required form controls are present so the steps are executable. The inline validation error and blocking behavior are dynamic and cannot be verified from the static DOM.

## TC-007 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** Phone number input and submit button exist; entering an invalid format and observing inline validation is a runtime behavior and not verifiable in the static DOM.

## TC-012 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** The Last Name field and Update Profile button are present so the steps are executable. The expectation that whitespace-only input is treated as empty is a validation behavior and cannot be confirmed from the static DOM.

## TC-001 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All UI elements required to perform the request-card flow are present. The specific account state (good standing) is not verifiable from this static page.

## TC-008 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All referenced controls exist so the steps are executable; whether a non-good-standing account is present is not verifiable here.

## TC-010 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Travel notice start/end date inputs and Update Controls button are present; validation logic (Start > End rejection) is dynamic and not verifiable from the snapshot.

## TC-014 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All UI elements required to enter identical start/end dates and submit controls are present; acceptance of the edge case is behavior to be validated at runtime, not from the static DOM.

## TC-001 - VALID
- **Valid Steps:** 6
- **Invalid Steps:** 0
- **Notes:** All UI elements required to perform a Buy trade are present on the Investments page. Post-submit outcomes (trade execution, order ID, holdings update) are dynamic and not verifiable from the static DOM.

## TC-013 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All form controls needed to attempt a Sell are present. The behavioral check for 'quantity exceeding balance' is a runtime/backend validation and cannot be verified from the static DOM.

## TC-014 - VALID
- **Valid Steps:** 6
- **Invalid Steps:** 0
- **Notes:** All UI elements required to create a recurring plan (including start date) are present. The validation that a past date is rejected is a runtime behavior and cannot be confirmed from the static DOM.

## TC-023 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All UI controls needed to place a boundary-case Buy are present. The exact-balance edge condition depends on runtime account data and backend validation, which cannot be verified here.

## TC-002 - INVALID_STEPS
- **Valid Steps:** 3
- **Invalid Steps:** 1
- **Notes:** Date inputs, account selector, and Generate button are present and actionable, but the test's first step (choosing a 'Custom date range' from a Statement Period control) references a control that does not exist on this page.

## TC-007 - INVALID_STEPS
- **Valid Steps:** 2
- **Invalid Steps:** 1
- **Notes:** Start/End date inputs and the Generate button are present so the date-entry and submission steps are executable; however the referenced 'Custom date range' selection control is not present in the DOM.

## TC-011 - INVALID_STEPS
- **Valid Steps:** 2
- **Invalid Steps:** 1
- **Notes:** The page exposes both date inputs and the Generate button so entering identical start/end dates and submitting is possible, but the test's explicit action to select a 'Custom date range' cannot be executed because that UI control is absent.

## TC-001 - VALID
- **Valid Steps:** 5
- **Invalid Steps:** 0
- **Notes:** All interactive elements required to perform the change-password flow are present and verifiable on the Security Settings page. The post-submit success notification is dynamic and therefore not checked here.

## TC-006 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All referenced form fields and the submit control exist. The expected inline error on incorrect current password is a dynamic post-submit outcome and not verifiable from the static DOM.

## TC-010 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All UI elements referenced (inputs and submit button) exist, but the browser Back / prior-success state required for the full interaction is not verifiable from the provided snapshot.

## TC-001 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable UI elements for sending a secure message are present on the Support Center page (message body and Send Message button). The post-submit success/ticket ID is dynamic and not verifiable from the static DOM.

## TC-016 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable controls referenced by the test exist (subject, message body, attachment input, and Send Message). The DOM shows an attachment input but does not explicitly declare its type as 'file' in the snapshot; selecting a file and server-side validation/error messages are dynamic and not verifiable from the static DOM.
