"""Product catalog and shared page configuration."""

PRODUCTS = [
    {
        "id": "single-tulip",
        "name": "Single Tulip",
        "price": 49,
        "category": "Single Flowers",
        "color": "Pink",
        "stock": 24,
        "description": "One soft pink fuzzy-wire tulip on a bendy green stem.",
        "flower_color": "#e987a3",
        "center_color": "#f8cf63",
        "blooms": 1,
    },
    {
        "id": "mini-daisy-bouquet",
        "name": "Mini Daisy Bouquet",
        "price": 149,
        "category": "Bouquets",
        "color": "White",
        "stock": 10,
        "description": "A small, sweet bunch of white daisies for desks and shelves.",
        "flower_color": "#fffdf4",
        "center_color": "#f3c44d",
        "blooms": 3,
    },
    {
        "id": "rose-bouquet",
        "name": "Rose Bouquet",
        "price": 299,
        "category": "Bouquets",
        "color": "Red",
        "stock": 6,
        "description": "Five velvety red roses that never wilt, tied with a ribbon.",
        "flower_color": "#cc5268",
        "center_color": "#f1be79",
        "blooms": 5,
    },
    {
        "id": "premium-mixed-bouquet",
        "name": "Premium Mixed Bouquet",
        "price": 499,
        "category": "Bouquets",
        "color": "Mixed",
        "stock": 3,
        "description": "Our fullest bouquet, with roses and daisies in garden colors.",
        "flower_color": "#bc7db4",
        "center_color": "#f4ca5b",
        "blooms": 6,
    },
    {
        "id": "sunshine-daisy",
        "name": "Sunshine Daisy",
        "price": 45,
        "category": "Single Flowers",
        "color": "Yellow",
        "stock": 30,
        "description": "One bright yellow daisy that lights up any corner.",
        "flower_color": "#f3c548",
        "center_color": "#a86d44",
        "blooms": 1,
    },
    {
        "id": "purple-tulip-pair",
        "name": "Purple Tulip Pair",
        "price": 89,
        "category": "Gift Sets",
        "color": "Purple",
        "stock": 12,
        "description": "Two purple tulips, wrapped and ready to hand over.",
        "flower_color": "#9b75c9",
        "center_color": "#f1ce68",
        "blooms": 2,
    },
    {
        "id": "white-flower-bundle",
        "name": "White Flower Bundle",
        "price": 179,
        "category": "Gift Sets",
        "color": "White",
        "stock": 8,
        "description": "A clean, calm bundle of white blooms with a mauve ribbon.",
        "flower_color": "#fffdf6",
        "center_color": "#efc354",
        "blooms": 4,
    },
    {
        "id": "pastel-gift-set",
        "name": "Pastel Gift Set",
        "price": 249,
        "category": "Gift Sets",
        "color": "Mixed",
        "stock": 5,
        "description": "Pastel flowers in a pretty gift box, ready to give.",
        "flower_color": "#e995ac",
        "center_color": "#f2ca5e",
        "blooms": 3,
    },
]

CATEGORIES = ["Single Flowers", "Bouquets", "Gift Sets"]

COLORS = {
    "Pink": "#e987a3",
    "Red": "#cc5268",
    "Yellow": "#f3c548",
    "Purple": "#9b75c9",
    "White": "#fffdf4",
    "Mixed": (
        "linear-gradient(135deg, #e987a3 0 25%, #f3c548 25% 50%, "
        "#9b75c9 50% 75%, #fffdf4 75%)"
    ),
}

PAGE_TITLES = {
    "home": "Welcome",
    "products": "Products",
    "services": "Services",
    "favorites": "Favorites",
    "cart": "My Cart",
    "promotions": "Promotions",
    "about": "About Us",
    "contact": "Contact",
}

PROMOTIONS = {
    "BLOOM10": {"kind": "percent", "value": 10, "minimum": 0},
    "GIFT20": {"kind": "fixed", "value": 20, "minimum": 200},
}

STORAGE_KEY = "jadxl_floral_state_v1"
LEGACY_FAVORITES_KEY = "jadxl_favorites"
