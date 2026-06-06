# Swaglab — Top 50 Curated Test Cases

**Selected:** 50 high-impact test cases across all 9 modules
**Coverage:** At least one Positive, Negative, and Edge/Boundary per module
**Prioritisation:** Business-critical flows, security concerns, state transitions, and boundary behaviours

---

## Summary Table

| # | Module | TC ID | Type | Priority |
|---|--------|-------|------|----------|
| 1 | Login | TC-001 | Positive | High |
| 2 | Login | TC-007 | Negative | High |
| 3 | Login | TC-011 | Negative | High |
| 4 | Login | TC-012 | Edge/Input | Medium |
| 5 | Login | TC-015 | Edge/Interaction | Medium |
| 6 | Product Inventory | TC-001 | Positive | High |
| 7 | Product Inventory | TC-002 | Positive | High |
| 8 | Product Inventory | TC-003 | Positive | High |
| 9 | Product Inventory | TC-005 | Negative | High |
| 10 | Product Inventory | TC-007 | Negative | High |
| 11 | Product Inventory | TC-008 | Edge/State | Medium |
| 12 | Product Inventory | TC-010 | Edge/Interaction | Low |
| 13 | Product Detail | TC-001 | Positive | High |
| 14 | Product Detail | TC-002 | Positive | High |
| 15 | Product Detail | TC-003 | Positive | Medium |
| 16 | Product Detail | TC-005 | Negative | High |
| 17 | Product Detail | TC-006 | Negative | High |
| 18 | Product Detail | TC-007 | Edge/State | Medium |
| 19 | Product Detail | TC-009 | Edge/Interaction | Medium |
| 20 | Product Detail | TC-011 | Edge/Interaction | Medium |
| 21 | Shopping Cart | TC-001 | Positive | High |
| 22 | Shopping Cart | TC-002 | Positive | Medium |
| 23 | Shopping Cart | TC-003 | Positive | High |
| 24 | Shopping Cart | TC-004 | Negative | High |
| 25 | Shopping Cart | TC-005 | Negative | High |
| 26 | Shopping Cart | TC-006 | Edge/Input | Low |
| 27 | Checkout – Information | TC-001 | Positive | High |
| 28 | Checkout – Information | TC-006 | Positive | High |
| 29 | Checkout – Information | TC-007 | Negative | High |
| 30 | Checkout – Information | TC-010 | Negative | High |
| 31 | Checkout – Information | TC-011 | Edge/Boundary | Medium |
| 32 | Checkout – Information | TC-013 | Edge/Input | Medium |
| 33 | Checkout – Overview | TC-001 | Positive | High |
| 34 | Checkout – Overview | TC-002 | Positive | Medium |
| 35 | Checkout – Overview | TC-003 | Negative | High |
| 36 | Checkout – Overview | TC-005 | Edge/Interaction | Medium |
| 37 | Checkout – Overview | TC-006 | Edge/Interaction | Medium |
| 38 | Checkout – Confirmation | TC-001 | Positive | Medium |
| 39 | Checkout – Confirmation | TC-002 | Positive | High |
| 40 | Checkout – Confirmation | TC-003 | Negative | High |
| 41 | Checkout – Confirmation | TC-005 | Edge/Interaction | Medium |
| 42 | Checkout – Confirmation | TC-007 | Edge/Interaction | Medium |
| 43 | Logout | TC-001 | Positive | High |
| 44 | Logout | TC-002 | Positive | High |
| 45 | Logout | TC-004 | Negative | High |
| 46 | Logout | TC-005 | Negative | High |
| 47 | Logout | TC-007 | Edge/Interaction | Medium |
| 48 | Reset App State | TC-001 | Positive | High |
| 49 | Reset App State | TC-003 | Negative | High |
| 50 | Reset App State | TC-007 | Edge/State | Medium |

---

## 1. Login

### TC-001 — Successful login with valid credentials ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Login page; user is not authenticated |
| **Steps** | 1. Enter `standard_user` in the Username field<br>2. Enter `secret_sauce` in the Password field<br>3. Click the **Login** button |
| **Expected Result** | User is redirected to the Product Inventory page; no error banner is displayed |

---

### TC-007 — Submit with Username blank shows required error ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Login page; user is not authenticated |
| **Steps** | 1. Ensure the Username field is empty<br>2. Enter `secret_sauce` in the Password field<br>3. Click the **Login** button |
| **Expected Result** | An inline validation error is shown: "Epic sadface: Username is required."; form does not submit; user remains on the Login page |

---

### TC-011 — Locked-out user receives locked-out error ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Login page; user is not authenticated |
| **Steps** | 1. Enter `locked_out_user` in the Username field<br>2. Enter `secret_sauce` in the Password field<br>3. Click the **Login** button |
| **Expected Result** | Error banner is shown: "Epic sadface: Sorry, this user has been locked out."; form does not submit; user remains on the Login page |

---

### TC-012 — Username with leading and trailing whitespace authenticates successfully ⚡ Edge/Input | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Login page is open |
| **Steps** | 1. Enter the accepted username with a single leading space and a single trailing space in the Username field<br>2. Enter the accepted shared password in the Password field<br>3. Click the **Login** button |
| **Expected Result** | Whitespace is trimmed; authentication succeeds; user is redirected to the Product Inventory page; no error banner is displayed |

---

### TC-015 — Rapid double-submit of Login with valid credentials ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | Login page is open |
| **Steps** | 1. Enter an accepted username in the Username field<br>2. Enter the accepted shared password in the Password field<br>3. Click the **Login** button<br>4. Immediately click the **Login** button again (second click within a short interval) |
| **Expected Result** | Form submits successfully on the first click; redirect to Product Inventory succeeds; the second rapid click does not produce a duplicate navigation or error banner |

---

## 2. Product Inventory

### TC-001 — Open Product Detail from product name ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Product Inventory page is open with multiple products listed |
| **Steps** | 1. On the Product Inventory page, locate any product in the list<br>2. Click the product's name link |
| **Expected Result** | The Product Detail page for that product is displayed |

---

### TC-002 — Add product to cart from the product list ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; target product is in NotInCart state on the Product Inventory page |
| **Steps** | 1. Locate the target product row<br>2. Click the **Add to cart** button in that row |
| **Expected Result** | Item is added to the cart; button label changes to **Remove**; cart badge count increments by 1 |

---

### TC-003 — Remove product from cart from the product list ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; target product is in InCart state on the Product Inventory page |
| **Steps** | 1. Locate the target product row<br>2. Click the **Remove** button in that row |
| **Expected Result** | Item is removed from the cart; button label changes to **Add to cart**; cart badge count decrements by 1 |

---

### TC-005 — Unauthenticated user cannot access Product Inventory page ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated (no valid session) |
| **Steps** | 1. Open the Product Inventory page URL directly in the browser |
| **Expected Result** | Access is blocked; user is redirected to the Login page; product list rows and sort controls are not visible |

---

### TC-007 — Add to cart action unavailable when product is already InCart ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; a product currently in InCart state exists in the Product Inventory |
| **Steps** | 1. Navigate to the Product Inventory page<br>2. Locate the row for the product in InCart state<br>3. Inspect the available action buttons in that row<br>4. Attempt to click an **Add to cart** button in that row if present |
| **Expected Result** | The **Add to cart** button is not present for the InCart product; the row displays **Remove** instead; cart badge count remains unchanged; no duplicate add occurs |

---

### TC-008 — Double-click Add on a NotInCart product increments cart by exactly one ⚡ Edge/State | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; product P is in NotInCart state; cart badge shows current count N |
| **Steps** | 1. Locate product P in the product list<br>2. Click the **Add to cart** button for product P<br>3. Immediately click the **Add to cart** button for product P again (second click before UI updates) |
| **Expected Result** | Only the first click succeeds; cart badge increments by exactly 1; button text changes to **Remove**; no duplicate increment or error message occurs |

---

### TC-010 — Rapidly adding multiple distinct products reflects correct badge count ⚡ Edge/Interaction | Low

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; products A, B, and C are all in NotInCart state; cart badge shows current count N |
| **Steps** | 1. Click **Add to cart** for product A<br>2. Immediately click **Add to cart** for product B<br>3. Immediately click **Add to cart** for product C |
| **Expected Result** | Each add action succeeds exactly once; cart badge increments by exactly 3 and shows N+3; each of products A, B, and C displays the **Remove** button; no missed or duplicate increments occur |

---

## 3. Product Detail

### TC-001 — Add product to cart when product is NotInCart ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; product exists and is in NotInCart state |
| **Steps** | 1. Navigate to the Product Detail page for the product<br>2. Click the **Add to cart** button |
| **Expected Result** | The Product Detail page now shows the **Remove** button; product state has changed to InCart |

---

### TC-002 — Remove product from cart when product is InCart ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; product exists and is in InCart state |
| **Steps** | 1. Navigate to the Product Detail page for the product<br>2. Click the **Remove** button |
| **Expected Result** | The Product Detail page now shows the **Add to cart** button; product state has changed to NotInCart |

---

### TC-003 — Navigate back to Product Inventory via Back to products link ✅ Positive | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Product Detail page is open for any product |
| **Steps** | 1. Click the **Back to products** link |
| **Expected Result** | The Product Inventory page is displayed |

---

### TC-005 — Add to cart is unavailable when product is already InCart ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | Product is already InCart; user is on the Product Detail page for that product |
| **Steps** | 1. Open the Product Detail page for a product whose state is InCart<br>2. Look for an **Add to cart** button on the page<br>3. If visible, attempt to click it |
| **Expected Result** | The **Add to cart** button is not visible or is disabled; the page shows the **Remove** action instead; product remains InCart and no additional item is added |

---

### TC-006 — Remove is unavailable when product is NotInCart ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | Product is NotInCart; user is on the Product Detail page for that product |
| **Steps** | 1. Open the Product Detail page for a product whose state is NotInCart<br>2. Look for a **Remove** button on the page<br>3. If visible, attempt to click it |
| **Expected Result** | The **Remove** button is not visible or is disabled; the page shows the **Add to cart** action instead; product remains NotInCart and no item is removed |

---

### TC-007 — Rapid double-click Add to cart when NotInCart does not duplicate cart entry ⚡ Edge/State | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Product Detail page for a product in NotInCart state; Shopping Cart does not contain this product |
| **Steps** | 1. Verify the page shows the **Add to cart** button<br>2. Click the **Add to cart** button<br>3. Immediately click the **Add to cart** button again (rapid second click)<br>4. Navigate to the Shopping Cart |
| **Expected Result** | First click succeeds; product is added once; Shopping Cart lists exactly one instance of the product; Product Detail shows **Remove**; no duplicate entries or errors |

---

### TC-009 — Click Add to cart then immediately open Shopping Cart via cart icon ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Product Detail page for a NotInCart product; Shopping Cart does not contain this product |
| **Steps** | 1. Verify the page shows the **Add to cart** button and the Cart icon is visible<br>2. Click the **Add to cart** button<br>3. Immediately click the Cart icon before waiting for a detailed UI text change<br>4. Observe Shopping Cart contents<br>5. Return to the Product Detail page for the same product |
| **Expected Result** | Shopping Cart opens; product appears exactly once (no duplicate from rapid navigation); returning to Product Detail shows state as InCart with **Remove** button visible |

---

### TC-011 — Navigate Back to products immediately after clicking Add to cart persists the add ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Product Detail page for a NotInCart product; Shopping Cart does not contain this product |
| **Steps** | 1. Click the **Add to cart** button<br>2. Immediately click the **Back to products** link before waiting for UI confirmation<br>3. From the Product Inventory, navigate back to the same Product Detail page |
| **Expected Result** | Navigation to Product Inventory succeeds; returning to Product Detail shows the product as InCart (**Remove** button visible); Shopping Cart contains exactly one instance |

---

## 4. Shopping Cart

### TC-001 — Remove an item from the cart ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Shopping Cart page is open with at least one item in the cart |
| **Steps** | 1. Locate the row for the target item in the Shopping Cart table<br>2. Click the **Remove** button on that row |
| **Expected Result** | The removed item's row is no longer displayed in the Shopping Cart table |

---

### TC-002 — Continue Shopping navigates to Product Inventory ✅ Positive | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Shopping Cart page is open |
| **Steps** | 1. Click the **Continue Shopping** link in the cart action bar |
| **Expected Result** | The Product Inventory page is displayed |

---

### TC-003 — Begin Checkout from the cart ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Shopping Cart page is open with at least one item in the cart |
| **Steps** | 1. Click the **Checkout** button in the cart action bar |
| **Expected Result** | The Checkout – Information page is displayed and the checkout flow begins |

---

### TC-004 — Unauthenticated user cannot access Shopping Cart page ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated (not logged in) |
| **Steps** | 1. Navigate directly to the Shopping Cart page URL as an unauthenticated user |
| **Expected Result** | Access is blocked; user is redirected to the Login page; the Shopping Cart table, item rows, and cart actions (Remove, Continue Shopping, Checkout) are not displayed |

---

### TC-005 — Unauthenticated user cannot begin checkout ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated (not logged in) |
| **Steps** | 1. Navigate directly to the Shopping Cart page URL<br>2. Click the **Checkout** button |
| **Expected Result** | Checkout is blocked; user is redirected to the Login page; the checkout flow does not begin; no items are removed or modified |

---

### TC-006 — Very long product description does not break cart table layout ⚡ Edge/Input | Low

| Field | Detail |
|-------|--------|
| **Preconditions** | A product with a 200+ character description has been added to the cart |
| **Steps** | 1. Navigate to the Shopping Cart page<br>2. Locate the cart row for the product with the long description<br>3. Observe the description cell in the cart table |
| **Expected Result** | The cart table displays the description without breaking layout; the description cell shows truncated overflow with a visible ellipsis; the table row does not collapse or overlap adjacent rows |

---

## 5. Checkout – Information

### TC-001 — Continue with all required fields filled proceeds to Overview ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Checkout – Information page is open |
| **Steps** | 1. Enter a valid first name in the First Name field<br>2. Enter a valid last name in the Last Name field<br>3. Enter a valid postal code in the Zip/Postal Code field<br>4. Click **Continue** |
| **Expected Result** | The Checkout – Overview step is displayed |

---

### TC-006 — Click Cancel returns user to Shopping Cart ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Checkout – Information page is open |
| **Steps** | 1. Click the **Cancel** button |
| **Expected Result** | The Shopping Cart page is displayed |

---

### TC-007 — Continue with First Name blank shows required error ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Checkout – Information page |
| **Steps** | 1. Ensure the First Name field is blank<br>2. Enter a valid last name in the Last Name field<br>3. Enter a valid postal code in the Zip/Postal Code field<br>4. Click the **Continue** button |
| **Expected Result** | A visible error banner states "Error: First Name is required"; the form does not proceed to the Overview step; the page remains on Checkout – Information |

---

### TC-010 — Continue with all required fields empty shows all three errors ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Checkout – Information page |
| **Steps** | 1. Ensure the First Name field is blank<br>2. Ensure the Last Name field is blank<br>3. Ensure the Zip/Postal Code field is blank<br>4. Click the **Continue** button |
| **Expected Result** | Visible error banners are shown for all three fields: "Error: First Name is required", "Error: Last Name is required", and "Error: Postal Code is required"; the form does not proceed; the page remains on Checkout – Information |

---

### TC-011 — Whitespace-only in First Name is treated as empty and blocks submission ⚡ Edge/Boundary | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Checkout – Information form |
| **Steps** | 1. Enter a whitespace-only value (spaces or tabs) in the First Name field<br>2. Enter a valid value in the Last Name field<br>3. Enter a valid value in the Zip/Postal Code field<br>4. Click **Continue** |
| **Expected Result** | Submission is blocked; an error banner with the exact text "Error: First Name is required" is displayed; the user remains on Checkout – Information |

---

### TC-013 — Very long text in name fields (200+ chars) is accepted or visibly truncated ⚡ Edge/Input | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is on the Checkout – Information form |
| **Steps** | 1. Enter a 200+ character string in the First Name field<br>2. Enter a 200+ character string in the Last Name field<br>3. Enter a valid postal code in the Zip/Postal Code field<br>4. Click **Continue** |
| **Expected Result** | Either the form submits successfully and the Overview displays the full long strings; or submission is blocked and the field is visibly truncated with an inline indicator/error; the UI must clearly indicate which behaviour occurred |

---

## 6. Checkout – Overview

### TC-001 — Finish checkout navigates to Confirmation page ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Checkout – Overview page is open with items in cart and order summary visible |
| **Steps** | 1. Review the Order Summary to confirm items are listed<br>2. Verify totals section shows Item total, Tax, and Total<br>3. Click the **Finish** button |
| **Expected Result** | Order is completed; user is navigated to the Checkout – Confirmation page |

---

### TC-002 — Cancel exits checkout from Overview ✅ Positive | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Checkout – Overview page is open |
| **Steps** | 1. Optionally review the Order Summary<br>2. Click the **Cancel** button |
| **Expected Result** | Checkout is exited; user is navigated away from the Overview step |

---

### TC-003 — Unauthenticated user cannot access or Finish checkout from Overview ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated (logged out) |
| **Steps** | 1. Navigate directly to the Checkout – Overview page URL<br>2. Observe the page content<br>3. Click the **Finish** button |
| **Expected Result** | User is redirected to the Login page; the Checkout – Overview content is not accessible; the order is not completed; the Confirmation page is not shown |

---

### TC-005 — Rapid double-click of Finish does not create duplicate orders ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is signed in; items are in cart; Checkout – Overview step is visible with order summary |
| **Steps** | 1. Click the **Finish** button<br>2. Immediately click the **Finish** button again (within one second)<br>3. Observe the UI until navigation to the Confirmation page completes |
| **Expected Result** | First submission succeeds; the second click is blocked or ignored (Finish button is disabled or a processing indicator appears); only one Confirmation page is shown and no duplicate order is created |

---

### TC-006 — Browser Back after successful Finish does not allow duplicate order creation ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is signed in; items are in cart; user has just successfully completed checkout via the Finish button |
| **Steps** | 1. Click the **Finish** button on the Overview step<br>2. Wait for the Confirmation page to be displayed<br>3. Use the browser **Back** button once<br>4. If the Overview page is shown, attempt to click **Finish** again |
| **Expected Result** | Re-submission is blocked; no second order is created; either the Finish button is disabled, a prevention message is shown, or the UI prevents submission; only one confirmation and order exist |

---

## 7. Checkout – Confirmation

### TC-001 — Confirmation page displays the success message ✅ Positive | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Confirmation page is displayed after completing checkout |
| **Steps** | 1. Navigate to the Confirmation page<br>2. Observe the page content |
| **Expected Result** | The Confirmation page displays the message "Thank you for your order!" |

---

### TC-002 — Back Home button returns to Product Inventory with an empty cart ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; Confirmation page is open after a successful order |
| **Steps** | 1. Click the **Back Home** button on the Confirmation page<br>2. Wait for navigation to complete and observe the landing page |
| **Expected Result** | The Product Inventory page is displayed; the cart indicator shows no items; the cart contents are empty |

---

### TC-003 — Unauthenticated user cannot access the Confirmation page ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated (no valid session) |
| **Steps** | 1. Navigate directly to the Confirmation page URL |
| **Expected Result** | Access is blocked; the Login page is shown instead; Confirmation text such as "Thank you for your order!" is not displayed; the Back Home button is not accessible; cart contents remain unchanged |

---

### TC-005 — Rapid double-click of Back Home button navigates once without error ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User has completed checkout and is on the Confirmation page showing the success message |
| **Steps** | 1. Rapidly click the **Back Home** button twice in immediate succession |
| **Expected Result** | First click succeeds: app navigates to Product Inventory and cart is cleared; the immediate second click is ignored; no additional navigation or error is shown |

---

### TC-007 — Page refresh on Confirmation then click Back Home still navigates correctly ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User has completed checkout and is on the Confirmation page showing the success message |
| **Steps** | 1. Reload/refresh the Confirmation page<br>2. Verify the confirmation message is still visible (or a cached view is shown)<br>3. Click the **Back Home** button |
| **Expected Result** | Back Home succeeds after a page refresh; app navigates to Product Inventory and cart is cleared; no error or duplicate navigation occurs |

---

## 8. Logout

### TC-001 — Click Logout redirects user to Login page ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in |
| **Steps** | 1. Ensure a page with the Logout option is open<br>2. Click the **Logout** button |
| **Expected Result** | The application redirects to the Login page; the Login page is displayed |

---

### TC-002 — After logout, accessing a protected page redirects to Login page ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in |
| **Steps** | 1. Click the **Logout** button<br>2. Attempt to open a protected page (inventory, detail, cart, or checkout) by navigating to its URL |
| **Expected Result** | Attempting to access the protected page redirects to the Login page; the Login page is displayed |

---

### TC-004 — Direct access to logout endpoint when not authenticated is blocked ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not logged in |
| **Steps** | 1. In the browser address bar, navigate directly to the Logout endpoint URL |
| **Expected Result** | No logout session-change occurs (there is no active session); the browser is redirected to the Login page; protected content is not displayed; user remains unauthenticated |

---

### TC-005 — After logout, protected pages are inaccessible without logging in again ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User was logged in and has just clicked Logout; session has ended; user is on the Login page |
| **Steps** | 1. From the Login page, navigate directly to the Product Inventory page URL<br>2. Observe the page content or redirection |
| **Expected Result** | Navigation to the Product Inventory page redirects to the Login page; protected content is not displayed; authentication is required before access is granted |

---

### TC-007 — Browser Back after logout does not expose protected content ⚡ Edge/Interaction | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in and on a protected page with visible sensitive content |
| **Steps** | 1. Click the **Logout** button<br>2. Wait until the app redirects to the Login page<br>3. Use the browser **Back** button once |
| **Expected Result** | Back navigation to the protected page is blocked; Login page is shown (or the app immediately redirects to Login); no protected content is visible; authentication is required |

---

## 9. Reset App State

### TC-001 — Reset clears a populated cart and resets all button states ✅ Positive | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; cart contains one or more items; at least one product tile shows the **Remove** button (InCart state) |
| **Steps** | 1. Open the page containing the **Reset App State** button<br>2. Click the **Reset App State** button |
| **Expected Result** | Cart is cleared (cart badge is hidden or shows zero); all product add/remove buttons reset to the default **Add to cart** state; user remains logged in |

---

### TC-003 — Unauthenticated user cannot perform Reset App State ❌ Negative | High

| Field | Detail |
|-------|--------|
| **Preconditions** | User is not authenticated (not logged in) |
| **Steps** | 1. Open the application page that contains the **Reset App State** button<br>2. Click the **Reset App State** button |
| **Expected Result** | Action is blocked; user is redirected to the Login page (or shown an authentication prompt); Reset App State is not performed; cart contents, cart badge, and button states remain unchanged |

---

### TC-007 — Rapid consecutive clicks on Reset App State apply a single reset outcome ⚡ Edge/State | Medium

| Field | Detail |
|-------|--------|
| **Preconditions** | User is logged in; cart contains one or more items; product tiles show the **Remove** button (InCart state) |
| **Steps** | 1. Click the **Reset App State** button<br>2. Immediately click the **Reset App State** button again (within typical double-click speed) |
| **Expected Result** | A single reset outcome is applied: cart is cleared (badge hidden or zero), product buttons return to the default **Add to cart** state; no error or duplicate adverse effect is shown; user remains logged in |