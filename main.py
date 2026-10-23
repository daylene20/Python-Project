import json
from decimal import Decimal, ROUND_HALF_UP
from pyscript import document, when, window
from pyodide.ffi import create_proxy
from data import CATEGORIES, COLORS, LEGACY_FAVORITES_KEY, PAGE_TITLES, PRODUCTS, PROMOTIONS, STORAGE_KEY
from illustrations import flower_svg

selected_category = 'All'
selected_color = 'All'
valid_product_ids = {product['id'] for product in PRODUCTS}
storage_notices = []
saved_text = window.localStorage.getItem(STORAGE_KEY)
saved_state = {}

if saved_text:
    try:
        saved_state = json.loads(saved_text)
    except json.JSONDecodeError:
        storage_notices.append('Saved data was unreadable; invalid information was reset.')
    if not isinstance(saved_state, dict):
        saved_state = {}
        storage_notices.append('Saved data had an invalid format; invalid information was reset.')
else:
    legacy_favorites_text = window.localStorage.getItem(LEGACY_FAVORITES_KEY)
    if legacy_favorites_text:
        try:
            legacy_favorites = json.loads(legacy_favorites_text)
        except json.JSONDecodeError:
            legacy_favorites = []
            storage_notices.append('Older saved favorites were unreadable and were reset.')
        if isinstance(legacy_favorites, list):
            saved_state = {'favorites': legacy_favorites}
        else:
            storage_notices.append('Older saved favorites had an invalid format and were reset.')

saved_favorites = saved_state.get('favorites', [])
if not isinstance(saved_favorites, list):
    saved_favorites = []
    storage_notices.append('Saved favorites had an invalid format and were reset.')

favorites = []
for product_id in saved_favorites:
    if not isinstance(product_id, str) or product_id not in valid_product_ids:
        storage_notices.append('Unknown or invalid saved favorites were skipped.')
        continue
    if product_id not in favorites:
        favorites.append(product_id)

saved_cart = saved_state.get('cart', {})
if not isinstance(saved_cart, dict):
    saved_cart = {}
    storage_notices.append('Saved cart had an invalid format and was reset.')

cart = {}
products_by_id = {product['id']: product for product in PRODUCTS}
for product_id, quantity in saved_cart.items():
    product = products_by_id.get(product_id) if isinstance(product_id, str) else None
    if product is None or isinstance(quantity, bool) or (not isinstance(quantity, int)) or (quantity < 1) or (quantity > product['stock']):
        storage_notices.append('Invalid saved cart items were skipped.')
        continue
    cart[product_id] = quantity

applied_promo = saved_state.get('promotion', '')
if not isinstance(applied_promo, str) or applied_promo not in PROMOTIONS:
    if applied_promo:
        storage_notices.append('An invalid saved discount code was removed.')
    applied_promo = ''

saved_requests = saved_state.get('custom_requests', [])
if not isinstance(saved_requests, list):
    saved_requests = []
    storage_notices.append('Saved custom request summaries had an invalid format and were reset.')
custom_requests = [summary[:1200] for summary in saved_requests if isinstance(summary, str) and summary.strip()][-10:]
toast_timer = None
toast_callback = None

@when("click", "[data-page]")
def navigate_pages(event):
    target_page = event.currentTarget.getAttribute("data-page")
    if target_page in PAGE_TITLES:
        document.getElementById('app-title').textContent = PAGE_TITLES[target_page]
    for btn in document.querySelectorAll("[data-page]"):
        is_current = "page" if btn.getAttribute("data-page") == target_page else "false"
        btn.setAttribute("aria-current", is_current)
    for section in document.querySelectorAll("main > section.page"):
        if section.id == f"page-{target_page}":
            section.classList.add("active")
        else:
            section.classList.remove("active")

@when("input", "#search-input")
def search_products(event):
    render_products()

def reset_filters(event):
    global selected_category, selected_color
    selected_category = 'All'
    selected_color = 'All'
    document.getElementById('search-input').value = ''
    render_products()

def handle_product_action(event):
    button = event.target.closest('[data-action]')
    action = button.getAttribute('data-action')
    product_id = button.getAttribute('data-id')
    product = products_by_id.get(product_id)
    if product is None:
        return

    if action in ('cart', 'favorite-cart'):
        quantity = cart.get(product_id, 0)
        if quantity >= product['stock']:
            return
        cart[product_id] = quantity + 1
        save_data()
        render_products()
    elif action == 'favorite':
        if product_id in favorites:
            favorites.remove(product_id)
        else:
            favorites.append(product_id)
        save_data()
        render_products()
    elif action == 'remove-favorite':
        if product_id in favorites:
            favorites.remove(product_id)
            save_data()
            render_products()
    elif action == 'increase-quantity':
        quantity = cart.get(product_id, 0)
        if quantity < product['stock']:
            cart[product_id] = quantity + 1
            save_data()
            render_products()
    elif action == 'decrease-quantity':
        quantity = cart.get(product_id, 0)
        if quantity > 1:
            cart[product_id] = quantity - 1
        elif quantity == 1:
            del cart[product_id]
        save_data()
        render_products()
    elif action == 'remove-cart-item':
        cart.pop(product_id, None)
        save_data()
        render_products()

def handle_dynamic_click(event):
    global selected_category, selected_color
    target = event.target.closest('[data-category], [data-color], [data-reset], [data-action]')
    if target is None:
        return
    if target.hasAttribute('data-category'):
        selected_category = target.getAttribute('data-category')
        render_products()
    elif target.hasAttribute('data-color'):
        selected_color = target.getAttribute('data-color')
        render_products()
    elif target.hasAttribute('data-reset'):
        reset_filters(event)
    elif target.hasAttribute('data-action'):
        handle_product_action(event)

@when("click", "#clear-saved-data")
def clear_saved_data(event):
    if not window.confirm('Clear saved favorites, cart items, and custom request summaries on this device?'):
        return
    favorites.clear()
    cart.clear()
    custom_requests.clear()
    global applied_promo
    applied_promo = ''
    window.localStorage.removeItem(STORAGE_KEY)
    window.localStorage.removeItem(LEGACY_FAVORITES_KEY)
    render_products()
    render_custom_request_summary()
    document.getElementById('request-message').textContent = ''
    document.getElementById('request-message').classList.remove('error', 'success')
    document.getElementById('promo-message').textContent = ''
    document.getElementById('promo-message').classList.remove('error', 'success')
    document.getElementById('promo-code').value = ''

@when("submit", "#promo-form")
def apply_promotion(event):
    global applied_promo
    event.preventDefault()
    code = document.getElementById('promo-code').value.strip().upper()
    message = document.getElementById('promo-message')
    message.classList.remove('error', 'success')
    if code not in PROMOTIONS:
        message.classList.add('error')
        message.textContent = 'That promotion code is not valid.'
        return
    if not cart:
        message.classList.add('error')
        message.textContent = 'Add a flower to your cart before applying a code.'
        return
    promotion = PROMOTIONS[code]
    subtotal = cart_subtotal()
    if subtotal < promotion['minimum']:
        message.classList.add('error')
        message.textContent = f"Your subtotal must be at least {format_money(promotion['minimum'])} for this code."
        return
    applied_promo = code
    save_data()
    message.classList.add('success')
    message.textContent = f'{code} applied to your cart.'
    render_cart()

@when("click", "#remove-promo")
def remove_promotion(event):
    global applied_promo
    applied_promo = ''
    save_data()
    document.getElementById('promo-message').textContent = 'Promotion removed.'
    document.getElementById('promo-message').classList.remove('error')
    document.getElementById('promo-message').classList.add('success')
    render_cart()

def product_card(product, favorites_page=False):
    in_cart = cart.get(product['id'], 0)
    available = product['stock'] - in_cart
    is_favorite = product['id'] in favorites
    stock_class = 'tag stock low' if available <= 5 else 'tag stock'
    cart_text = 'Add to Cart' if available > 0 else 'Out of Stock'
    favorite_text = '♥ Favorited' if is_favorite else '♡ Add to Favorites'
    favorite_pressed = 'true' if is_favorite else 'false'
    if favorites_page:
        actions = f'''<button class="btn" type="button" data-action="favorite-cart" data-id="{product['id']}" {('disabled' if available <= 0 else '')}>Add to Cart</button><button class="btn secondary" type="button" data-action="remove-favorite" data-id="{product['id']}">Remove</button>'''
    else:
        actions = f'''<button class="btn" type="button" data-action="cart" data-id="{product['id']}" {('disabled' if available <= 0 else '')}>{cart_text}</button><button class="btn secondary" type="button" data-action="favorite" data-id="{product['id']}" aria-pressed="{favorite_pressed}">{favorite_text}</button>'''
    return f'''<article class="card"><div class="art">{flower_svg(product)}</div><div class="card-info"><h2>{product['name']}</h2><p class="description">{product['description']}</p><div class="meta"><span class="tag">{product['category']}</span><span class="{stock_class}">{available} in stock</span></div><p class="price">₱{product['price']:,}</p><div class="card-actions">{actions}</div></div></article>'''

def render_chips():
    category_html = ['<button class="chip" type="button" data-category="All">All categories</button>']
    category_html.extend((f'<button class="chip" type="button" data-category="{category}">{category}</button>' for category in CATEGORIES))
    document.getElementById('category-chips').innerHTML = ''.join(category_html)
    color_html = ['<button class="chip" type="button" data-color="All">All colors</button>']
    color_html.extend((f'<button class="chip" type="button" data-color="{name}"><span class="swatch" style="background:{swatch}"></span>{name}</button>' for name, swatch in COLORS.items()))
    document.getElementById('color-chips').innerHTML = ''.join(color_html)

def matching_products():
    words = document.getElementById('search-input').value.strip().lower().split()
    matching = []
    for product in PRODUCTS:
        if selected_category != 'All' and product['category'] != selected_category:
            continue
        if selected_color != 'All' and product['color'] != selected_color:
            continue
        searchable = ' '.join([product['name'], product['description'], product['category'], product['color']]).lower()
        if all((word in searchable for word in words)):
            matching.append(product)
    return matching

def update_chip_states():
    for chip in document.querySelectorAll('[data-category]'):
        chip.setAttribute('aria-pressed', 'true' if chip.getAttribute('data-category') == selected_category else 'false')
    for chip in document.querySelectorAll('[data-color]'):
        chip.setAttribute('aria-pressed', 'true' if chip.getAttribute('data-color') == selected_color else 'false')

def render_products():
    shown = matching_products()
    document.getElementById('products-grid').innerHTML = ''.join((product_card(product) for product in shown))
    document.getElementById('no-results').hidden = bool(shown)
    document.getElementById('result-count').textContent = f'Showing {len(shown)} of {len(PRODUCTS)} products'
    update_chip_states()
    update_counts()
    render_featured()
    render_favorites()
    render_cart()

def render_featured():
    featured_ids = {'sunshine-daisy', 'rose-bouquet', 'pastel-gift-set'}
    featured_products = [product for product in PRODUCTS if product['id'] in featured_ids]
    document.getElementById('featured-grid').innerHTML = ''.join((product_card(product) for product in featured_products))

def save_data():
    saved_state = {'version': 1, 'favorites': favorites, 'cart': cart, 'promotion': applied_promo, 'custom_requests': custom_requests}
    window.localStorage.setItem(STORAGE_KEY, json.dumps(saved_state))
    window.localStorage.removeItem(LEGACY_FAVORITES_KEY)

def render_favorites():
    favorite_products = [product for product_id in favorites for product in PRODUCTS if product['id'] == product_id]
    target_grid = document.getElementById('favorites-grid')
    if target_grid:
        target_grid.innerHTML = ''.join((product_card(product, favorites_page=True) for product in favorite_products))
    target_empty = document.getElementById('favorites-empty')
    if target_empty:
        target_empty.hidden = bool(favorite_products)

def render_custom_request_summary():
    preview = document.getElementById('request-preview')
    if preview:
        preview.hidden = not custom_requests
        preview.textContent = custom_requests[-1] if custom_requests else ''

@when("submit", "#custom-request-form")
def submit_custom_request(event):
    event.preventDefault()
    style = document.getElementById('request-style')
    colors = document.getElementById('request-colors')
    details = document.getElementById('request-details')
    message = document.getElementById('request-message')

    invalid_field = None
    if not style.value:
        invalid_field = style
        error_text = 'Choose a flower style before submitting.'
    elif not colors.value.strip():
        invalid_field = colors
        error_text = 'Enter your preferred colors before submitting.'
    elif len(details.value.strip()) < 10:
        invalid_field = details
        error_text = 'Please add at least 10 characters of request details.'

    for field in (style, colors, details):
        field.removeAttribute('aria-invalid')
    message.classList.remove('success')
    if invalid_field:
        invalid_field.setAttribute('aria-invalid', 'true')
        message.classList.add('error')
        message.textContent = error_text
        invalid_field.focus()
        return

    summary = (
        f"Flower style: {style.value}\n"
        f"Preferred colors: {colors.value.strip()}\n"
        f"Request details: {details.value.strip()}"
    )
    custom_requests.append(summary)
    del custom_requests[:-10]
    save_data()
    render_custom_request_summary()
    message.classList.remove('error')
    message.classList.add('success')
    message.textContent = 'Your request summary was saved on this device. It was not sent to the business.'

def cart_subtotal():
    subtotal = 0
    for product in PRODUCTS:
        quantity = cart.get(product['id'], 0)
        subtotal += product['price'] * quantity
    return subtotal

def format_money(amount):
    value = Decimal(amount).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return f"₱{value:,}"

def update_counts():
    fav_count = len(favorites)
    cart_count = sum(cart.values())
    fav_el = document.getElementById('favorite-count')
    if fav_el:
        fav_el.textContent = str(fav_count)
    fav_nav = document.getElementById('favorites-nav-count')
    if fav_nav:
        fav_nav.textContent = str(fav_count)
        fav_nav.hidden = (fav_count == 0)
    cart_el = document.getElementById('cart-count')
    if cart_el:
        cart_el.textContent = str(cart_count)
    cart_nav = document.getElementById('cart-nav-count')
    if cart_nav:
        cart_nav.textContent = str(cart_count)
        cart_nav.hidden = (cart_count == 0)

def render_cart():
    target_items = document.getElementById('cart-items')
    empty_state = document.getElementById('cart-empty')
    cart_layout = document.getElementById('cart-layout')
    items = [product for product in PRODUCTS if cart.get(product['id'], 0) > 0]
    empty_state.hidden = bool(items)
    cart_layout.hidden = not bool(items)

    item_html = []
    for product in items:
        quantity = cart[product['id']]
        available = product['stock'] - quantity
        item_html.append(
            f'''<article class="cart-item">
              <div class="cart-item-art">{flower_svg(product)}</div>
              <div>
                <h3>{product['name']}</h3>
                <p class="cart-item-price">{format_money(product['price'])} each</p>
                <p class="cart-line-total">Line total: {format_money(product['price'] * quantity)}</p>
              </div>
              <div class="cart-item-controls">
                <div class="quantity-control" aria-label="Quantity for {product['name']}">
                  <button type="button" data-action="decrease-quantity" data-id="{product['id']}" aria-label="Decrease quantity of {product['name']}">−</button>
                  <span class="quantity-value">{quantity}</span>
                  <button type="button" data-action="increase-quantity" data-id="{product['id']}" aria-label="Increase quantity of {product['name']}" {('disabled' if available <= 0 else '')}>+</button>
                </div>
                <button class="remove-item" type="button" data-action="remove-cart-item" data-id="{product['id']}">Remove</button>
              </div>
            </article>'''
        )
    target_items.innerHTML = ''.join(item_html)

    subtotal = cart_subtotal()
    discount = 0
    promo_message = document.getElementById('promo-message')
    if applied_promo:
        promotion = PROMOTIONS[applied_promo]
        if subtotal >= promotion['minimum']:
            if promotion['kind'] == 'percent':
                discount = int(
                    (Decimal(subtotal) * Decimal(promotion['value']) / Decimal(100))
                    .quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                )
            else:
                discount = min(subtotal, promotion['value'])
        else:
            promo_message.classList.remove('success')
            promo_message.classList.add('error')
            promo_message.textContent = (
                f"{applied_promo} requires a subtotal of at least "
                f"{format_money(promotion['minimum'])}."
            )

    document.getElementById('cart-subtotal').textContent = format_money(subtotal)
    document.getElementById('cart-discount').textContent = f"−{format_money(discount)}"
    document.getElementById('cart-discount-row').hidden = discount == 0
    document.getElementById('cart-total').textContent = format_money(subtotal - discount)
    document.getElementById('remove-promo').hidden = not bool(applied_promo)

dynamic_click_proxy = create_proxy(handle_dynamic_click)
document.addEventListener('click', dynamic_click_proxy)

render_chips()
render_products()
render_custom_request_summary()