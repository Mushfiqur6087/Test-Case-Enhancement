# SwagLabs Faulty Dataset: Bug Report

This document outlines the 9 intentional "hallucinated requirements" (bugs) injected into the `faulty/SwagLabs.md` functional description. These bugs misrepresent the actual capabilities of the SwagLabs frontend application.

In addition to the legitimate failing bug already present in the application ("Reset App State"), the agent should flag 9 out of the 9 injected bugs during verification.

## The 9 Injected Specification Bugs

| # | Section | False Requirement Injected | Expected Verification Result |
|---|---------|----------------------------|------------------------------|
| 1 | **Login** | Claimed the presence of a `"Remember Me"` checkbox. | Agent flags missing Remember Me checkbox. |
| 2 | **Product Inventory** | Claimed there is a `"Category Filter"` sidebar. | Agent flags missing Category Filter sidebar. |
| 3 | **Product Detail** | Claimed there is a `"Customer Reviews"` section. | Agent flags missing Customer Reviews section. |
| 4 | **Shopping Cart** | Claimed there is an `"Apply Discount Code"` input field. | Agent flags missing Apply Discount Code field. |
| 5 | **Checkout - Information** | Claimed there is an `"Email Address"` input field. | Agent flags missing Email Address field. |
| 6 | **Checkout - Overview** | Claimed there is a `"Shipping Method"` dropdown. | Agent flags missing Shipping Method dropdown. |
| 7 | **Checkout - Confirmation** | Claimed there is an `"Order Tracking Link"`. | **MISSED BY AGENT** (Intentional simulation failure). |
| 8 | **Navigation Menu** | Claimed there is a `"Contact Support"` link. | Agent flags missing Contact Support link. |
| 9 | **Logout** | Claimed a `"Logout Confirmation Modal"` appears. | Agent flags missing Logout Confirmation Modal. |

## Pre-existing Legitimate Bug
| # | Section | Actual Application Defect | Expected Verification Result |
|---|---------|----------------------------|------------------------------|
| 10 | **Reset App State** | The cart is not cleared when the reset button is clicked. | Agent flags cart badge state mismatch (Fails). |

## Conclusion
The application frontend remains functionally unmodified. This dataset stress-tests the verification engine's strict adherence to identifying elements specified in `SwagLabs.md` that do not exist in the live DOM.
