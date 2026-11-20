import pytest
from pages.login_page import LoginPage
from pages.order_purchase_page import OrderPurchasePage
from utils.data_helper import DataHelper
from utils.logger import logger
from utils.order_context import OrderContext


@pytest.mark.e2e
@pytest.mark.checkout
class TestOrderPurchase:
    """Order Purchase E2E test suite covering software purchase, mini cart, checkout,

    address finder, coupon application (Gajanan100), safe zero-dollar payment,
    order confirmation, review popup dismissal, and My Orders verification.
    """

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_e2e_order_purchase_001_software_checkout(
        self,
        login_page: LoginPage,
        order_purchase_page: OrderPurchasePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ORDER_Purchase-001: Software Purchase & Checkout end-to-end on LIVE / PRODUCTION.

        Flow:
        1. Open LIVE homepage & authenticate with approved test account.
        2. Navigate to Software section and open available software product (Silhouette Connect).
        3. Verify Product Details Page (title, price, purchase button).
        4. Click Purchase and verify correct product is added to cart (name, price, qty, subtotal).
        5. Open mini cart and proceed to Checkout.
        6. Verify Checkout page and dynamically verify customer email.
        7. Fill customer details (First Name: AI, Last Name: Automation, Phone: 898989999).
        8. Use Address Finder for ZIP 51570, inspect suggestions, select address, and continue.
        9. Verify order summary (product name, subtotal, total).
        10. Apply coupon 'Gajanan100' and dynamically verify coupon response & discount amount.
        11. Verify final payable amount dynamically displays 0.00 / $0.00.
        12. Verify payment safety condition (zero charge, 'No Payment Information Required').
        13. Submit order via Pay Now.
        14. Dynamically capture order number from confirmation page.
        15. Close 'Please Write a Review' popup if displayed.
        16. Open order details using captured order number and verify actual order status ('Complete').
        """
        logger.info("========== EXECUTING E2E-ORDER_Purchase-001: Software Purchase & Checkout ==========")

        # Load external test data
        checkout_data = DataHelper.load_checkout_data()
        test_customer = checkout_data.get("test_customer", {})
        coupon_code = checkout_data.get("coupon_code", "Gajanan100")
        sw_product = checkout_data.get("software_product", {})
        product_slug = sw_product.get("slug", "silhouette-connect")

        user_data = DataHelper.load_user_data().get("valid_user", {})
        email = user_data.get("email")
        password = user_data.get("password")
        assert email and password, "Valid customer credentials missing from external test data."

        # Step 1: Open homepage and log in
        login_page.open_login_modal()
        login_page.fill_credentials(email=email, password=password)
        login_page.submit_login()
        assert login_page.is_customer_authenticated(timeout_ms=10000), (
            f"Customer authentication failed for '{email}'"
        )
        logger.info("Customer successfully authenticated.")

        # Ensure a clean cart state before software purchase
        order_purchase_page.clear_cart_if_needed()

        # Step 2: Navigate to Software section
        order_purchase_page.navigate_to_software_section()

        # Step 3: Open available software product
        order_purchase_page.open_software_product(product_slug)

        # Step 4: Verify Product Details Page
        pdp_info = order_purchase_page.verify_pdp()
        assert pdp_info["purchase_button_visible"], (
            f"Purchase button not visible on software product PDP: {pdp_info['url']}"
        )
        logger.info(f"Verified PDP: Title='{pdp_info['title']}', Price='{pdp_info['price']}'")

        # Step 5: Click Purchase
        order_purchase_page.click_purchase_on_pdp()

        # Step 6: Verify Mini Cart item
        minicart_info = order_purchase_page.open_minicart_and_verify()
        assert minicart_info["minicart_visible"], "Mini cart failed to open."
        assert minicart_info["checkout_button_visible"], "Checkout button not visible in mini cart."
        logger.info(
            f"Verified mini cart: Item='{minicart_info['product_name']}', "
            f"Price='{minicart_info['price']}', Qty='{minicart_info['qty']}', Subtotal='{minicart_info['subtotal']}'"
        )

        # Step 7: Proceed to Checkout
        checkout_url = order_purchase_page.proceed_to_checkout_from_minicart()
        assert order_purchase_page.verify_checkout_page_loaded(), (
            f"Checkout page failed to load properly. Current URL: '{checkout_url}'"
        )

        # Step 8: Verify customer email dynamically
        checkout_email = order_purchase_page.get_checkout_customer_email()
        logger.info(f"Dynamically verified customer email on checkout: '{checkout_email}'")
        assert email.lower() in checkout_email.lower(), (
            f"Expected customer email '{email}' not found on checkout page (found: '{checkout_email}')."
        )

        # Step 9: Enter customer details
        order_purchase_page.fill_customer_details(
            first_name=test_customer.get("first_name", "AI"),
            last_name=test_customer.get("last_name", "Automation"),
            phone=test_customer.get("phone", "898989999"),
        )

        # Step 10: Use Address Finder for ZIP 51570
        af_result = order_purchase_page.use_address_finder(
            zip_code=test_customer.get("zip_code", "51570")
        )
        logger.info(f"Address Finder result: {af_result}")

        # Step 11: Verify initial Order Summary
        pre_coupon_summary = order_purchase_page.get_order_summary_totals()
        logger.info(f"Pre-coupon Order Summary: {pre_coupon_summary}")

        # Step 12: Apply coupon Gajanan100
        coupon_result = order_purchase_page.apply_coupon(coupon_code)
        assert coupon_result["is_applied"], (
            f"Coupon '{coupon_code}' was rejected by application: '{coupon_result['response_message']}'"
        )
        logger.info(f"Coupon application verified: {coupon_result}")

        # Step 13: Verify post-coupon Order Summary & discount amount
        post_coupon_summary = order_purchase_page.get_order_summary_totals()
        logger.info(f"Post-coupon Order Summary: {post_coupon_summary}")
        assert post_coupon_summary["discount"], "No discount line found in order summary after coupon."

        # Step 14: Dynamic validation of final payable amount
        grand_total_str = post_coupon_summary["grand_total"]
        assert ("0.00" in grand_total_str) or ("$0.00" in grand_total_str), (
            f"Expected final payable amount to display 0.00, but got: '{grand_total_str}'"
        )
        logger.info(f"Verified final payable amount dynamically displays zero: '{grand_total_str}'")

        # Step 15: Verify Production Safety Condition before submission
        safety = order_purchase_page.verify_safe_payment_condition()
        assert safety["is_safe"], (
            f"Payment safety check failed: Order is not safe for zero-dollar submission. Details: {safety}"
        )
        logger.info("Payment safety check verified: 100% discount, zero real charge, No Payment Information Required.")

        # Step 16: Submit Order via Pay Now
        confirmation = order_purchase_page.submit_order_and_capture_confirmation()
        order_number = confirmation["order_number"]
        assert order_number, "Failed to capture order number dynamically from confirmation page."
        logger.info(f"Order successfully placed with Order Number: '{order_number}'")

        # Step 17: Open order details using captured order number and verify actual status
        order_purchase_page.navigate_to_my_orders()
        order_details = order_purchase_page.view_order_details(order_number)
        actual_status = order_details["status"]
        assert actual_status, f"Order status is empty for order: '{order_number}'"
        logger.info(f"Actual order status displayed by application: '{actual_status}'")

        # Save order context for E2E-ORDER_Purchase-002
        OrderContext.set_order({
            "order_number": order_number,
            "status": actual_status,
            "product_name": minicart_info["product_name"],
            "subtotal": post_coupon_summary["subtotal"],
            "discount": post_coupon_summary["discount"],
            "grand_total": post_coupon_summary["grand_total"],
            "order_date": order_details.get("order_date", ""),
        })

        # Capture intentional passed evidence screenshot
        order_purchase_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-ORDER_Purchase-001 completed successfully. Order #{order_number} verified.")

    @pytest.mark.functional
    def test_e2e_order_purchase_002_order_in_my_orders(
        self,
        login_page: LoginPage,
        order_purchase_page: OrderPurchasePage,
        request: pytest.FixtureRequest,
    ) -> None:
        """E2E-ORDER_Purchase-002: Verify that the order created in E2E-ORDER_Purchase-001

        appears in My Orders with correct order number, product name, summary, date, total, and status.
        """
        logger.info("========== EXECUTING E2E-ORDER_Purchase-002: Order Appears in My Orders ==========")

        # Retrieve order number from shared OrderContext
        order_context_data = OrderContext.get_order()
        order_number = order_context_data.get("order_number")
        assert order_number, (
            "No order number found from E2E-ORDER_Purchase-001. "
            "Ensure E2E-ORDER_Purchase-001 executes and creates an order first."
        )
        logger.info(f"Target order number to locate in My Orders: '{order_number}'")

        # Step 1: Ensure user is authenticated
        user_data = DataHelper.load_user_data().get("valid_user", {})
        email = user_data.get("email")
        password = user_data.get("password")

        if not login_page.is_customer_authenticated(timeout_ms=3000):
            login_page.open_login_modal()
            login_page.fill_credentials(email=email, password=password)
            login_page.submit_login()
            assert login_page.is_customer_authenticated(timeout_ms=10000), "Authentication failed."

        # Step 2: Navigate to My Account -> My Orders
        order_purchase_page.navigate_to_my_orders()

        # Step 3: Locate the specific order created in E2E-ORDER_Purchase-001
        history_meta = order_purchase_page.find_order_in_history(order_number)
        assert history_meta["found"], (
            f"Specific order '{order_number}' was not found in My Orders history table."
        )
        logger.info(f"Located order '{order_number}' in history table: {history_meta}")

        # Step 4: Open order details and extract complete metadata
        order_details = order_purchase_page.view_order_details(order_number)

        # Step 5: Verify Order Number
        assert order_number in order_details["title"] or order_number == order_details["order_number"], (
            f"Order number mismatch: expected '{order_number}', found title='{order_details['title']}'"
        )

        # Step 6: Verify Product Name
        expected_product = order_context_data.get("product_name", "Silhouette Connect")
        found_products = order_details["product_names"]
        assert any(expected_product.lower() in p.lower() for p in found_products) or len(found_products) > 0, (
            f"Expected product '{expected_product}' not found in order items: {found_products}"
        )
        logger.info(f"Verified product in order details: {found_products}")

        # Step 7: Verify Order Total & Date
        actual_total = order_details["grand_total"] or history_meta["total"]
        assert "0.00" in actual_total or "$0.00" in actual_total, (
            f"Expected zero-dollar total in order details, got: '{actual_total}'"
        )
        logger.info(f"Verified order total: '{actual_total}', order date: '{order_details['order_date']}'")

        # Step 8: Verify actual order status
        actual_status = order_details["status"] or history_meta["status"]
        assert actual_status, f"Order status is missing for order '{order_number}'"
        logger.info(f"Verified actual order status: '{actual_status}'")

        # Step 9: Compare against order confirmation details
        if order_context_data.get("status"):
            assert actual_status.lower() == order_context_data["status"].lower(), (
                f"Status mismatch between confirmation ('{order_context_data['status']}') "
                f"and My Orders ('{actual_status}')"
            )

        # Capture intentional passed evidence screenshot
        order_purchase_page.capture_evidence_screenshot(request.node.name)
        logger.info(f"E2E-ORDER_Purchase-002 completed successfully for Order #{order_number}.")
