# Enriched Test Cases

## TC-001 - Successful login with valid credentials
- **Module:** Login
- **Direct Link:** https://www.saucedemo.com/login
- **Requires Auth:** False

### Steps
1. Enter 'standard_user' in the Username field
2. Enter 'secret_sauce' in the Password field
3. Click the Login button

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-007 - Submit with Username blank shows required error
- **Module:** Login
- **Direct Link:** https://www.saucedemo.com/login
- **Requires Auth:** False

### Steps
1. Ensure the Username field is empty (clear any existing text)
2. Enter 'secret_sauce' in the Password field
3. Click the Login button

### Test Data
```json
{
  "username": "",
  "password": "secret_sauce"
}
```

## TC-011 - Locked-out user receives locked-out error
- **Module:** Login
- **Direct Link:** https://www.saucedemo.com/login
- **Requires Auth:** False

### Steps
1. Enter 'locked_out_user' in the Username field
2. Enter 'secret_sauce' in the Password field
3. Click the Login button

### Test Data
```json
{
  "username": "locked_out_user",
  "password": "secret_sauce"
}
```

## TC-012 - Username with leading and trailing whitespace authenticates successfully
- **Module:** Login
- **Direct Link:** https://www.saucedemo.com/login
- **Requires Auth:** False

### Steps
1. Enter ' standard_user ' (one leading space and one trailing space) in the Username field
2. Enter 'secret_sauce' in the Password field
3. Click the Login button

### Test Data
```json
{
  "username": " standard_user ",
  "password": "secret_sauce"
}
```

## TC-015 - Rapid double-submit of Login with valid credentials
- **Module:** Login
- **Direct Link:** https://www.saucedemo.com/login
- **Requires Auth:** False

### Steps
1. Enter 'standard_user' in the Username field
2. Enter 'secret_sauce' in the Password field
3. Click the Login button
4. Immediately click the Login button again (second click within a short interval)

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-001 - Open Product Detail from product name
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** True

### Steps
1. On the Product Inventory page, locate any product in the list (e.g. Sauce Labs Backpack)
2. Click the product's name link (e.g. Sauce Labs Backpack)

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "product": "Sauce Labs Backpack"
}
```

## TC-002 - Add product to cart from the product list
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** True

### Steps
1. On the Product Inventory page, locate the target product row for Sauce Labs Backpack
2. Click the Add to cart button in that row

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "product": "Sauce Labs Backpack"
}
```

## TC-003 - Remove product from cart from the product list
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** True

### Steps
1. On the Product Inventory page, locate the target product row for Sauce Labs Backpack
2. If a Remove button is not present in the product row (snapshot shows only Add to cart buttons), click the Add to cart button to ensure the product becomes InCart, then click the cart badge to open the Cart page and click Remove for the product on the Cart page

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "product": "Sauce Labs Backpack"
}
```

## TC-005 - Unauthenticated user cannot access Product Inventory page
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** False

### Steps
1. Open the Product Inventory page URL directly in the browser: https://www.saucedemo.com/inventory

### Test Data
```json
{}
```

## TC-007 - Add to cart action unavailable when product is already InCart
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** True

### Steps
1. Navigate to the Product Inventory page
2. Locate the row for Sauce Labs Backpack. If the row shows an Add to cart button (snapshot shows Add buttons only), click Add to cart to create an InCart state for this product, then re-locate the row now representing the InCart product
3. Inspect the available action buttons in that row
4. Attempt to click an Add to cart button in that row if present

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "product": "Sauce Labs Backpack"
}
```

## TC-008 - Double-click Add on a NotInCart product increments cart by exactly one
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** True

### Steps
1. Locate product P in the product list (use Sauce Labs Backpack as product P)
2. Click the Add to cart button for product P
3. Immediately click the Add to cart button for product P again (second click before UI updates)

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "product_p": "Sauce Labs Backpack"
}
```

## TC-010 - Rapidly adding multiple distinct products reflects correct badge count
- **Module:** Product Inventory
- **Direct Link:** https://www.saucedemo.com/inventory
- **Requires Auth:** True

### Steps
1. Click Add to cart for product A (Sauce Labs Backpack)
2. Immediately click Add to cart for product B (Sauce Labs Bike Light)
3. Immediately click Add to cart for product C (Sauce Labs Bolt T-Shirt)

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "product_a": "Sauce Labs Backpack",
  "product_b": "Sauce Labs Bike Light",
  "product_c": "Sauce Labs Bolt T-Shirt"
}
```

## TC-001 - Add product to cart when product is NotInCart (Positive | High)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Navigate to the Product Detail page for the product (open https://www.saucedemo.com/product-detail.html)
2. Click the Remove button (button[data-test='remove'|id='remove']) to remove the product from the cart

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "initial_product_state": "InCart"
}
```

## TC-002 - Remove product from cart when product is InCart (Positive | High)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Navigate to the Product Detail page for the product (open https://www.saucedemo.com/product-detail.html)
2. Click the Remove button (button[data-test='remove'|id='remove'])

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "initial_product_state": "InCart"
}
```

## TC-003 - Navigate back to Product Inventory via Back to products link (Positive | Medium)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Click the Back to products link

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-005 - Add to cart is unavailable when product is already InCart (Negative | High)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Open the Product Detail page for a product whose state is InCart
2. Look for an Add to cart button on the page
3. If visible, attempt to click it

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "initial_product_state": "InCart"
}
```

## TC-006 - Remove is unavailable when product is NotInCart (Negative | High)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Open the Product Detail page for a product whose state is NotInCart
2. Look for a Remove button on the page
3. If visible, attempt to click it

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "observed_product_state": "InCart"
}
```

## TC-007 - Rapid double-click Add to cart when NotInCart does not duplicate cart entry (Edge/State | Medium)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Verify the page shows the Remove button (product currently InCart)
2. Click the Remove button to change the product state to NotInCart
3. Verify the Add to cart button is visible
4. Click the Add to cart button
5. Immediately click the Add to cart button again (rapid second click)
6. Navigate to the Shopping Cart

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "initial_product_state": "InCart"
}
```

## TC-009 - Click Add to cart then immediately open Shopping Cart via cart icon (Edge/Interaction | Medium)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Verify the page shows the Remove button (product is currently InCart)
2. Click the Remove button to set the product to NotInCart
3. Verify the Add to cart button is visible and the Cart icon is visible
4. Click the Add to cart button
5. Immediately click the Cart icon before waiting for a detailed UI text change
6. Observe Shopping Cart contents
7. Return to the Product Detail page for the same product

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "initial_product_state": "InCart"
}
```

## TC-011 - Navigate Back to products immediately after clicking Add to cart persists the add (Edge/Interaction | Medium)
- **Module:** Product Detail
- **Direct Link:** https://www.saucedemo.com/product-detail.html
- **Requires Auth:** True

### Steps
1. Verify the page shows the Remove button (product currently InCart)
2. Click the Remove button to set the product to NotInCart
3. Click the Add to cart button
4. Immediately click the Back to products link before waiting for UI confirmation
5. From the Product Inventory, navigate back to the same Product Detail page

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "initial_product_state": "InCart"
}
```

## TC-001 - Remove an item from the cart
- **Module:** Shopping Cart
- **Direct Link:** https://www.saucedemo.com/cart.html
- **Requires Auth:** True

### Steps
1. Locate the row for the target item in the Shopping Cart table
2. Click the Remove button on that row

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-002 - Continue Shopping navigates to Product Inventory
- **Module:** Shopping Cart
- **Direct Link:** https://www.saucedemo.com/cart.html
- **Requires Auth:** True

### Steps
1. Click the Continue Shopping link in the cart action bar

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-003 - Begin Checkout from the cart
- **Module:** Shopping Cart
- **Direct Link:** https://www.saucedemo.com/cart.html
- **Requires Auth:** True

### Steps
1. Click the Checkout button in the cart action bar

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-004 - Unauthenticated user cannot access Shopping Cart page
- **Module:** Shopping Cart
- **Direct Link:** https://www.saucedemo.com/cart.html
- **Requires Auth:** False

### Steps
1. Navigate directly to the Shopping Cart page URL (https://www.saucedemo.com/cart.html) as an unauthenticated user

### Test Data
```json
{}
```

## TC-005 - Unauthenticated user cannot begin checkout
- **Module:** Shopping Cart
- **Direct Link:** https://www.saucedemo.com/cart.html
- **Requires Auth:** False

### Steps
1. Navigate directly to the Shopping Cart page URL (https://www.saucedemo.com/cart.html)
2. Click the Checkout button

### Test Data
```json
{}
```

## TC-006 - Very long product description does not break cart table layout
- **Module:** Shopping Cart
- **Direct Link:** https://www.saucedemo.com/cart.html
- **Requires Auth:** True

### Steps
1. Navigate to the Shopping Cart page
2. Locate the cart row for the product with the long description
3. Observe the description cell in the cart table

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-001 - Continue with all required fields filled proceeds to Overview
- **Module:** Checkout - Information
- **Direct Link:** https://www.saucedemo.com/checkout-step-one.html
- **Requires Auth:** True

### Steps
1. Enter a valid first name in the First Name field
2. Enter a valid last name in the Last Name field
3. Enter a valid postal code in the Zip/Postal Code field
4. Click **Continue**

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-006 - Click Cancel returns user to Shopping Cart
- **Module:** Checkout - Information
- **Direct Link:** https://www.saucedemo.com/checkout-step-one.html
- **Requires Auth:** True

### Steps
1. Click the **Cancel** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-007 - Continue with First Name blank shows required error
- **Module:** Checkout - Information
- **Direct Link:** https://www.saucedemo.com/checkout-step-one.html
- **Requires Auth:** True

### Steps
1. Ensure the First Name field is blank
2. Enter a valid last name in the Last Name field
3. Enter a valid postal code in the Zip/Postal Code field
4. Click the **Continue** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-010 - Continue with all required fields empty shows all three errors
- **Module:** Checkout - Information
- **Direct Link:** https://www.saucedemo.com/checkout-step-one.html
- **Requires Auth:** True

### Steps
1. Ensure the First Name field is blank
2. Ensure the Last Name field is blank
3. Ensure the Zip/Postal Code field is blank
4. Click the **Continue** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-011 - Whitespace-only in First Name is treated as empty and blocks submission
- **Module:** Checkout - Information
- **Direct Link:** https://www.saucedemo.com/checkout-step-one.html
- **Requires Auth:** True

### Steps
1. Enter a whitespace-only value (spaces or tabs) in the First Name field
2. Enter a valid value in the Last Name field
3. Enter a valid value in the Zip/Postal Code field
4. Click **Continue**

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-013 - Very long text in name fields (200+ chars) is accepted or visibly truncated
- **Module:** Checkout - Information
- **Direct Link:** https://www.saucedemo.com/checkout-step-one.html
- **Requires Auth:** True

### Steps
1. Enter a 200+ character string in the First Name field
2. Enter a 200+ character string in the Last Name field
3. Enter a valid postal code in the Zip/Postal Code field
4. Click **Continue**

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-001 - Finish checkout navigates to Confirmation page
- **Module:** Checkout - Overview
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Review the Order Summary to confirm items are listed
2. Verify totals section shows Item total, Tax, and Total
3. Click the **Finish** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-002 - Cancel exits checkout from Overview
- **Module:** Checkout - Overview
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Optionally review the Order Summary
2. Click the **Cancel** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-003 - Unauthenticated user cannot access or Finish checkout from Overview
- **Module:** Checkout - Overview
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Navigate directly to the Checkout – Overview page URL
2. Observe the page content
3. Click the **Finish** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-005 - Rapid double-click of Finish does not create duplicate orders
- **Module:** Checkout - Overview
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Click the **Finish** button
2. Immediately click the **Finish** button again (within one second)
3. Observe the UI until navigation to the Confirmation page completes

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-006 - Browser Back after successful Finish does not allow duplicate order creation
- **Module:** Checkout - Overview
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Click the **Finish** button on the Overview step
2. Wait for the Confirmation page to be displayed
3. Use the browser **Back** button once
4. If the Overview page is shown, attempt to click **Finish** again

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-001 - Confirmation page displays the success message
- **Module:** Checkout - Confirmation
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Navigate to the Confirmation page
2. Observe the page content

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-002 - Back Home button returns to Product Inventory with an empty cart
- **Module:** Checkout - Confirmation
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Click the **Back Home** button on the Confirmation page
2. Wait for navigation to complete and observe the landing page

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-003 - Unauthenticated user cannot access the Confirmation page
- **Module:** Checkout - Confirmation
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Navigate directly to the Confirmation page URL

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-005 - Rapid double-click of Back Home button navigates once without error
- **Module:** Checkout - Confirmation
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Rapidly click the **Back Home** button twice in immediate succession

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-007 - Page refresh on Confirmation then click Back Home still navigates correctly
- **Module:** Checkout - Confirmation
- **Direct Link:** https://www.saucedemo.com/checkout-step-two.html
- **Requires Auth:** True

### Steps
1. Reload/refresh the Confirmation page
2. Verify the confirmation message is still visible (or a cached view is shown)
3. Click the **Back Home** button

### Test Data
```json
{
  "user": "standard_user"
}
```

## TC-001 - Click Logout redirects user to Login page
- **Module:** Logout
- **Direct Link:** https://www.saucedemo.com/inventory.html
- **Requires Auth:** False

### Steps
1. Open https://www.saucedemo.com/ (Login page).
2. Enter 'standard_user' in Username field
3. Enter 'secret_sauce' in Password field
4. Click the Login button
5. On the Inventory page, click the Menu (burger) button
6. Click the 'Logout' link in the side menu

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "inventory_url": "https://www.saucedemo.com/inventory.html"
}
```

## TC-002 - After logout, accessing a protected page redirects to Login page
- **Module:** Logout
- **Direct Link:** https://www.saucedemo.com/inventory.html
- **Requires Auth:** False

### Steps
1. Open https://www.saucedemo.com/ (Login page).
2. Enter 'standard_user' in Username field
3. Enter 'secret_sauce' in Password field
4. Click the Login button
5. On the Inventory page, click the Menu (burger) button
6. Click the 'Logout' link in the side menu
7. Attempt to open a protected page by navigating to https://www.saucedemo.com/inventory.html

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "protected_url": "https://www.saucedemo.com/inventory.html"
}
```

## TC-004 - Direct access to logout endpoint when not authenticated is blocked
- **Module:** Logout
- **Direct Link:** https://www.saucedemo.com/logout
- **Requires Auth:** False

### Steps
1. In the browser address bar, navigate directly to https://www.saucedemo.com/logout

### Test Data
```json
{
  "logout_url": "https://www.saucedemo.com/logout"
}
```

## TC-005 - After logout, protected pages are inaccessible without logging in again
- **Module:** Logout
- **Direct Link:** https://www.saucedemo.com/inventory.html
- **Requires Auth:** False

### Steps
1. From the Login page, navigate directly to the Product Inventory page URL: https://www.saucedemo.com/inventory.html
2. Observe the page content or redirection

### Test Data
```json
{
  "inventory_url": "https://www.saucedemo.com/inventory.html"
}
```

## TC-007 - Browser Back after logout does not expose protected content
- **Module:** Logout
- **Direct Link:** https://www.saucedemo.com/inventory.html
- **Requires Auth:** False

### Steps
1. Open https://www.saucedemo.com/ (Login page).
2. Enter 'standard_user' in Username field
3. Enter 'secret_sauce' in Password field
4. Click the Login button
5. On the Inventory page, click the Menu (burger) button
6. Click the 'Logout' link in the side menu
7. Wait until the app redirects to the Login page
8. Use the browser Back button once

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce",
  "inventory_url": "https://www.saucedemo.com/inventory.html"
}
```

## TC-001 - Reset clears a populated cart and resets all button states
- **Module:** Reset App State
- **Direct Link:** https://www.saucedemo.com/reset-app-state
- **Requires Auth:** True

### Steps
1. Open https://www.saucedemo.com/reset-app-state
2. Enter 'standard_user' in the Username field
3. Enter 'secret_sauce' in the Password field
4. Click the Login button
5. On the products page, click 'Add to cart' on the first product tile
6. Verify the cart badge shows '1' and the product's button now shows 'Remove'
7. Open the application menu and click the 'Reset App State' menu item
8. Verify the cart is cleared (cart badge is hidden or shows '0')
9. Verify all product add/remove buttons are reset to 'Add to cart'
10. Verify the user remains logged in (e.g., the menu still shows the Logout option)

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```

## TC-003 - Unauthenticated user cannot perform Reset App State
- **Module:** Reset App State
- **Direct Link:** https://www.saucedemo.com/reset-app-state
- **Requires Auth:** False

### Steps
1. Open https://www.saucedemo.com/reset-app-state
2. Click the 'Reset App State' menu item

### Test Data
```json
{}
```

## TC-007 - Rapid consecutive clicks on Reset App State apply a single reset outcome
- **Module:** Reset App State
- **Direct Link:** https://www.saucedemo.com/reset-app-state
- **Requires Auth:** True

### Steps
1. Open https://www.saucedemo.com/reset-app-state
2. Enter 'standard_user' in the Username field
3. Enter 'secret_sauce' in the Password field
4. Click the Login button
5. On the products page, click 'Add to cart' on the first product tile
6. Verify the cart badge shows '1' and the product's button now shows 'Remove'
7. Click the 'Reset App State' menu item
8. Immediately click the 'Reset App State' menu item again (within a typical double-click/double-tap interval)
9. Verify a single reset outcome is applied: cart is cleared (badge hidden or '0') and product buttons return to 'Add to cart'
10. Verify no error or duplicate adverse effect is shown and the user remains logged in

### Test Data
```json
{
  "username": "standard_user",
  "password": "secret_sauce"
}
```
