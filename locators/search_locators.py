class SearchLocators:
    """Encapsulated locators for Silhouette America Search functionality."""

    # Search Inputs & Controls
    SEARCH_INPUT = "#search_mini_form input#search, input#search.input-text, input#search"
    SEARCH_FORM = "#search_mini_form, form[action*='/search']"
    SEARCH_BUTTON = "#search_mini_form button[type='submit'], .action.search, button[title='Search']"
    SEARCH_TOGGLE = ".header-search-toggle, button.search-toggle"

    # Search Results Containers & Product Cards
    SEARCH_RESULTS_CONTAINER = ".search.results, .klevuResults, .products.wrapper"
    SEARCH_RESULT_ITEMS = ".item.product, .kuProductBlock, .product-item"
    PRODUCT_ITEM_LINK = ".item.product a, .kuProductBlock a, .product-item a.product-item-link, a[class*='product']"
    PRODUCT_ITEM_TITLE = ".klevuProductTitle, .product-item-name, a.product-item-link, .kuProductTitle"

    # No Results & Error States
    NO_RESULTS_MESSAGE = ".message.notice, .no-results, .kuNoResults, div:has-text(\"We're sorry, no results found for\")"
    NO_RESULTS_TEXT_CONTAINER = "#maincontent, .page-main, .columns"
    EMPTY_QTY_COUNTER = ".counter.qty.empty, .qty.empty"

    # Product Detail Page (PDP) Indicators
    PDP_TITLE = "h1.page-title, h1"
    PDP_ADD_TO_CART_BUTTON = "#product-addtocart-button, button:has-text('Add to Cart'), .action.tocart"
    PDP_MAIN_CONTENT = ".product-info-main, #maincontent"

    # Search Autocomplete Overlay
    SEARCH_AUTOCOMPLETE = "#search_autocomplete, .klevuTarget, .search-autocomplete"
