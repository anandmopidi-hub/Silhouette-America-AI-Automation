class CatalogLocators:
    """Encapsulated locators for Silhouette America Catalog and Category Listing (PLP) pages."""

    # Product Grid & Listing Items
    PRODUCT_GRID = ".products.wrapper, .products-grid, .product-items"
    PRODUCT_ITEMS = ".product-item, .item.product, li.product-item"
    PRODUCT_ITEM_INFO = ".product-item-info"
    PRODUCT_ITEM_LINK = "a.product-item-link, .product-item a.product-item-link"
    PRODUCT_ITEM_NAME = ".product-item-name, a.product-item-link"
    PRODUCT_ITEM_PRICE = ".price, [data-price-type='finalPrice']"
    PRODUCT_ITEM_IMAGE = ".product-image-photo, .product-item img"

    # Category Page Header & Layout Elements
    PAGE_TITLE = "h1.page-title, h1#page-title-heading, h1"
    BREADCRUMBS = ".breadcrumbs, ul.items"
    MAIN_CONTENT = "#maincontent, .page-main"

    # Layered Navigation / Filters
    FILTER_BLOCK = ".block.filter, #layered-filter-block, .sidebar .filter"
    FILTER_ITEMS = ".filter-options-item, [data-role='collapsible']"
    FILTER_TITLE = ".filter-options-title, .title"
    FILTER_CONTENT = ".filter-options-content"
    FILTER_OPTION_LINK = ".filter-options-content a"
    FILTER_CURRENT_CONTAINER = ".filter-current, .block-actions.filter-actions, .items-filter, #am-shopby-container"
    FILTER_CURRENT_ITEMS = ".filter-current .item, .filter-current li, .items-filter .item, .amshopby-item"
    FILTER_CLEAR_ALL = ".sa-filter-clear-all-desktop, a:has-text('Clear All'), .action.clear, .filter-clear, a.action.clear, .filter-actions a"

    # Sorter / Toolbar Controls
    TOOLBAR = ".toolbar.toolbar-products, .toolbar-top"
    SORTER_SELECT = "#sorter, select.sorter-options, select[data-role='sorter']"
    SORTER_DIRECTION = "a.action.sorter-action, .sorter-action"

    # Pagination Controls
    PAGINATION_CONTAINER = ".pages, .pagination, .toolbar-products .pages"
    PAGINATION_ITEMS = ".pages-items .item, .pages .item"
    PAGINATION_CURRENT_PAGE = ".pages-items .item.current, .pages .item.current"
    PAGINATION_PAGE_LINKS = ".pages-items .item:not(.pages-item-next):not(.pages-item-previous) a.page, .pages a.page"
    PAGINATION_NEXT_BUTTON = ".action.next, .pages a.next, a[title='Next']"
    PAGINATION_PREV_BUTTON = ".action.previous, .pages a.previous, a[title='Previous']"

    # Empty / No Matching Products Notification State
    NO_PRODUCTS_NOTICE = ".message.info.empty, .message.notice, div:has-text(\"We can't find products matching the selection.\")"
