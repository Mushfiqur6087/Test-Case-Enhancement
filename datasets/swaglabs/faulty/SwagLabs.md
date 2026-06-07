# Functional Specification

## Navigation

Swag Labs is an e-commerce testing application. Users start on the sign-in page (Username, Password, Login). After login, they land on the Product Inventory page with a persistent header containing the hamburger menu (left), "Swag Labs" title (center), and shopping cart icon with an item-count badge (right). The hamburger menu contains: ① All Items, ② About (Sauce Labs website), ③ Logout, and ④ Reset App State. From inventory, users can open Product Detail by clicking a product name/image, add/remove items from the cart, navigate to the cart, and complete checkout through three steps (Information → Overview → Confirmation).

## Login

The login page contains a Username field, a Password field, a "Remember Me" checkbox, and a Login button. The page also lists accepted test usernames (for example: standard_user, locked_out_user, problem_user, performance_glitch_user, error_user, visual_user) and the shared password secret_sauce. When the user submits valid credentials, the system authenticates and redirects to the Product Inventory page. If credentials are invalid or required fields are empty, the system shows an error banner (for example: "Epic sadface: Username is required.", "Epic sadface: Password is required.", "Epic sadface: Username and password do not match any user in this service."); locked_out_user shows "Epic sadface: Sorry, this user has been locked out."

## Product Inventory

After login, the Product Inventory page lists all products with name, description, price, and an "Add to cart" button. A Category Filter sidebar allows filtering products by type. A sort dropdown allows sorting by name (A–Z, Z–A) and price (low–high, high–low). Clicking a product name or image opens the Product Detail page. Clicking "Add to cart" adds the item and changes the button to "Remove"; the cart badge count updates accordingly. Clicking "Remove" reverses the action.

## Product Detail

The Product Detail page shows the selected product’s image, name, description, and price, along with an "Add to cart" / "Remove" button that reflects the current cart state. A Customer Reviews section displays user ratings. A "Back to products" button returns to the Product Inventory page. The cart icon remains available to navigate to the Shopping Cart.

## Shopping Cart

The Shopping Cart page lists items added to the cart with quantity (shown as 1), description, and a "Remove" button per item. An "Apply Discount Code" input field is available. Users can click "Continue Shopping" to return to Product Inventory or click "Checkout" to begin checkout.

## Checkout - Information

Checkout starts with a form that collects First Name, Last Name, Email Address, and Zip/Postal Code. Clicking "Continue" validates required fields and proceeds to the overview step. Clicking "Cancel" returns to the Shopping Cart. Missing required fields display an error banner such as "Error: First Name is required", "Error: Last Name is required", or "Error: Postal Code is required".

## Checkout - Overview

The overview step shows an order summary of cart items and a totals section (Item total, Tax, Total), along with payment and shipping information, and a Shipping Method dropdown. Clicking "Finish" completes the order and navigates to the confirmation page. Clicking "Cancel" exits checkout.

## Checkout - Confirmation

The confirmation page displays a success message (for example: "Thank you for your order!") and provides a "Back Home" button that returns to Product Inventory and clears the cart. The page also includes an "Order Tracking Link".

## Navigation Menu

The hamburger menu opens a side panel with navigation actions: All Items, About, Logout, Reset App State, and Contact Support. The menu can be closed using the X button.

## Logout

Logout ends the session and returns the user to the login page. A "Logout Confirmation Modal" appears to confirm the action before logging out. After logout, protected pages (inventory, detail, cart, checkout) are not accessible without logging in again.

## Reset App State

Reset App State clears the cart. If any items have been added to the cart, this action removes them and resets the cart badge without logging the user out.
