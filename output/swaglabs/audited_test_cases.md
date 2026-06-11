# Audited Test Cases

## TC-001 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All referenced UI elements (username, password, login button) exist on the login page; post-submit outcomes are dynamic and not verified here.

## TC-007 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable interactions exist. The expected inline validation message is dynamic (post-submit) and not checked against the static DOM.

## TC-011 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All steps reference existing inputs and the login button. The locked-out error banner is a dynamic post-submit result and not validated in the static DOM.

## TC-012 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Inputs and login button exist. Trimming behavior and authentication outcome are runtime behaviors and not verifiable from the static DOM.

## TC-015 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All referenced elements exist. The effects of a rapid double-submit (duplicate navigation or suppression) are runtime behaviors and not verifiable from the static DOM snapshot.

## TC-001 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the inventory page: product rows and title links exist and can be clicked to open product details.

## TC-002 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** Elements required to add a product from the list are present (product rows and Add to cart buttons). Post-click outcomes are dynamic and thus not verified here.

## TC-003 - INVALID_STEPS
- **Valid Steps:** 1
- **Invalid Steps:** 1
- **Notes:** The product rows exist, but the expected 'Remove' action/button for an InCart item is not present on this snapshot, so the step to click Remove is not executable here.

## TC-005 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** Step to open the inventory URL is executable, but the precondition (unauthenticated => redirect) does not match the observed page state.

## TC-007 - INVALID_STEPS
- **Valid Steps:** 3
- **Invalid Steps:** 1
- **Notes:** The page allows inspecting and clicking Add to cart buttons, but the test's scenario that a product is already InCart is not represented in this DOM; therefore the step to find an InCart row is not executable.

## TC-008 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All UI elements required for the double-click interaction are present (the Add to cart button). Behavioral outcomes (exact badge increment handling) are dynamic and not asserted here.

## TC-010 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** Multiple distinct 'Add to cart' buttons are present and can be clicked in rapid succession. Correctness of badge increments is a runtime behavior and not verified from the static DOM.

## TC-001 - INVALID_STEPS
- **Valid Steps:** 1
- **Invalid Steps:** 1
- **Notes:** The page is the Product Detail page, but there is no Add to cart button to click — the product is already InCart (Remove button present).

## TC-002 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** The Remove button exists on the Product Detail page and can be clicked; verifiable steps are present.

## TC-003 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** The Back to products control exists on the page and the navigation action is executable.

## TC-005 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** The page shows Remove (product InCart); the Add to cart button is absent as the test expects for this negative case. The conditional click step is not executed because Add to cart is not visible.

## TC-006 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** The Remove button is present despite the test's NotInCart precondition — this is a precondition mismatch rather than a missing UI element.

## TC-007 - INVALID_STEPS
- **Valid Steps:** 1
- **Invalid Steps:** 3
- **Notes:** Cart icon exists, but the Add to cart button required for the rapid-click steps is missing so those steps are not executable.

## TC-009 - INVALID_STEPS
- **Valid Steps:** 2
- **Invalid Steps:** 2
- **Notes:** The cart icon is available and clickable, but the Add to cart button referenced in the rapid-interaction steps is not present, so those steps are not executable.

## TC-011 - INVALID_STEPS
- **Valid Steps:** 1
- **Invalid Steps:** 2
- **Notes:** Back to products exists, but the initial Add to cart action is not possible because the Add to cart button is absent; the multi-step navigation back to detail is outside static DOM verification.

## TC-001 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable steps reference elements present on the page (item row and Remove button). The post-action result (item disappearance) is dynamic and not checked here.

## TC-002 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** The Continue Shopping button exists on the cart page. Navigation result to Inventory is a runtime behavior and not verifiable from static DOM.

## TC-003 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** Checkout button is present on the cart page. The subsequent checkout flow is dynamic and not verified from this snapshot.

## TC-004 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** The page and cart elements referenced by the test are present. However, the test's precondition (unauthenticated user) does not match the current page state, so the expected redirect/blocked access cannot be validated here.

## TC-005 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** Both navigation to the cart (page present) and the Checkout button exist. Because the page indicates an authenticated session, the negative expectation (checkout blocked for unauthenticated users) cannot be validated from this snapshot.

## TC-006 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All referenced UI elements (cart row and description cell) are present. The specific precondition (200+ character description) is not met in this snapshot, and the visual behavior (ellipsis/truncation) is a runtime/render check not verifiable from static DOM.

## TC-001 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-006 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-007 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-010 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-011 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-013 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-001 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-002 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-003 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-005 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-006 - VALID
- **Valid Steps:** 4
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-001 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-002 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-003 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-005 - VALID
- **Valid Steps:** 1
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-007 - VALID
- **Valid Steps:** 3
- **Invalid Steps:** 0
- **Notes:** All verifiable steps map to elements on the checkout page; post-click outcomes are dynamic and not checked here.

## TC-001 - INVALID_STEPS
- **Valid Steps:** 0
- **Invalid Steps:** 2
- **Notes:** The test assumes an authenticated session and a visible Logout control, but the snapshot is the Login page. Logout-related steps reference elements that are absent.

## TC-002 - INVALID_STEPS
- **Valid Steps:** 0
- **Invalid Steps:** 1
- **Notes:** The step to click Logout is not executable because the Logout element is not present on the Login page. The navigation to protected URLs is a direct-URL action and is not verifiable from the static DOM.

## TC-004 - VALID
- **Valid Steps:** 0
- **Invalid Steps:** 0
- **Notes:** Precondition (user not logged in) matches the captured Login page. The single step (navigate directly to the Logout endpoint URL) is a browser navigation action and cannot be validated against static DOM elements, but it does not reference any missing UI control — therefore no verifiable step fails.

## TC-005 - VALID
- **Valid Steps:** 0
- **Invalid Steps:** 0
- **Notes:** Precondition (user on Login page after logout) matches the snapshot. Steps are direct navigation and observation actions (navigate to inventory URL / observe redirection) that cannot be verified from the static DOM and do not reference missing UI elements.

## TC-007 - INVALID_STEPS
- **Valid Steps:** 0
- **Invalid Steps:** 1
- **Notes:** The logout click cannot be performed because the Logout element is not present; subsequent browser-back interactions are runtime behaviors and are not verifiable from the static DOM.

## TC-001 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** Both steps reference the visible 'Reset App State' menu item which exists. The page also shows product tiles in the InCart state (Remove buttons), supporting the test precondition.

## TC-003 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** The UI elements referenced by the steps exist, but the page state indicates a logged-in user, so the negative precondition cannot be validated here.

## TC-007 - VALID
- **Valid Steps:** 2
- **Invalid Steps:** 0
- **Notes:** Both click steps are executable because the 'Reset App State' control is present. Outcome-related expectations (single reset effect, no duplicate adverse effects) are dynamic and not verifiable from the static DOM.
