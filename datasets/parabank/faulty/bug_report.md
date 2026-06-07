# ParaBank Faulty Dataset: Bug Report

This document outlines the 10 intentional "hallucinated requirements" (bugs) injected into the `faulty/Parabank.md` functional description. These bugs misrepresent the actual capabilities of the ParaBank frontend application. 

When the agent attempts to verify the application against this faulty specification, it should flag these 10 elements as **MISSING**, successfully demonstrating its ability to catch inaccuracies in the documentation.

## The 10 Injected Specification Bugs

| # | Section | False Requirement Injected | Expected Verification Result |
|---|---------|----------------------------|------------------------------|
| 1 | **Login** | Claimed the presence of a `"Sign In with Google"` OAuth button. | Agent flags missing Google OAuth button in DOM. |
| 2 | **Register** | Claimed the form requires a `"Date of Birth"` input field. | Agent flags missing Date of Birth input field. |
| 3 | **Accounts Overview** | Claimed the dashboard includes a `"Download CSV"` export button. | Agent flags missing Download CSV button. |
| 4 | **Open New Account** | Claimed there is a `"Currency Selection"` dropdown (USD, EUR, GBP). | Agent flags missing Currency Selection dropdown. |
| 5 | **Transfer Funds** | Claimed there is a `"Schedule Recurring Transfer"` checkbox. | Agent flags missing Schedule Recurring Transfer checkbox. |
| 6 | **Payments** | Claimed there is an `"Add New Payee"` button that opens a modal. | Agent flags missing Add New Payee button. |
| 7 | **Request Loan** | Claimed there is an `"Upload Payslip"` file input for verification. | Agent flags missing Upload Payslip file input. |
| 8 | **Update Contact Info** | Claimed there is a `"Secondary Email Address"` input field. | Agent flags missing Secondary Email Address field. |
| 9 | **Investments** | Claimed the portfolio snapshot includes a `"Risk Tolerance"` slider. | Agent flags missing Risk Tolerance slider control. |
| 10| **Security Settings** | Claimed there is an `"Enable Two-Factor Authentication (2FA)"` toggle switch. | Agent flags missing 2FA toggle switch. |

## Conclusion
The application frontend remains functionally correct and unmodified. The sole purpose of this dataset is to stress-test the verification engine's strict adherence to identifying elements specified in `Parabank.md` that do not exist in the live DOM.
