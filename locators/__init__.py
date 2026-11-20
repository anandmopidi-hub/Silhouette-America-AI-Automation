"""Locators package.

Encapsulates selectors for Page Objects.
Raw locators should never be placed directly inside test cases.
"""
from .home_locators import HomeLocators
from .search_locators import SearchLocators
from .catalog_locators import CatalogLocators
from .pdp_locators import PdpLocators
from .registration_locators import RegistrationLocators
from .machine_registration_locators import MachineRegistrationLocators
from .software_locators import SoftwareLocators
from .club_silhouette_locators import ClubSilhouetteLocators
from .login_locators import LoginLocators
from .order_purchase_locators import OrderPurchaseLocators
from .different_pdp_locators import Different_PDP_Locators
from .my_account_locators import MyAccountLocators
from .footer_locators import FooterLocators
from .header_locators import HeaderLocators
from .product_user_manuals_locators import ProductUserManualsLocators
from .creator_rewards_locators import CreatorRewardsLocators
from .clearance_locators import ClearanceLocators

__all__ = [
    "HomeLocators",
    "SearchLocators",
    "CatalogLocators",
    "PdpLocators",
    "RegistrationLocators",
    "MachineRegistrationLocators",
    "SoftwareLocators",
    "ClubSilhouetteLocators",
    "LoginLocators",
    "OrderPurchaseLocators",
    "Different_PDP_Locators",
    "MyAccountLocators",
    "FooterLocators",
    "HeaderLocators",
    "ProductUserManualsLocators",
    "CreatorRewardsLocators",
    "ClearanceLocators",
]


