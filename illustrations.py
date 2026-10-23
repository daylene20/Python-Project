"""SVG illustrations used by the product cards."""


def flower_svg(product):
    """Create a small flower illustration without external image assets."""
    colors = [
        product["flower_color"],
        "#f3c98d",
        "#c98bb9",
        "#fffdf4",
        "#e78e9f",
        "#8eafd0",
    ]
    centers = [(150, 64), (103, 89), (197, 91), (126, 105), (175, 108), (150, 91)]
    flowers = []

    for index in range(product["blooms"]):
        cx, cy = centers[index]
        petal_color = (
            colors[index % len(colors)]
            if product["color"] == "Mixed"
            else product["flower_color"]
        )
        petals = "".join(
            f'<ellipse cx="0" cy="-13" rx="7" ry="13" fill="{petal_color}" '
            f'transform="rotate({angle})"/>'
            for angle in range(0, 360, 45)
        )
        flowers.append(
            f'<line x1="{cx}" y1="{cy + 8}" '
            f'x2="{150 + (cx - 150) * 1.35}" y2="184" '
            'stroke="#668966" stroke-width="4" stroke-linecap="round"/>'
            f'<g transform="translate({cx} {cy})">{petals}'
            f'<circle r="7" fill="{product["center_color"]}"/></g>'
        )

    return (
        '<svg viewBox="0 0 300 205" role="img" '
        'aria-label="Handmade flower illustration" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<path d="M85 194 Q150 180 215 194" fill="none" '
        'stroke="#b8a28d" stroke-width="3" stroke-linecap="round"/>'
        + "".join(flowers)
        + '<path d="M146 151 Q128 134 117 149 Q130 161 146 151Z" fill="#769878"/>'
        '<path d="M154 164 Q172 144 185 157 Q174 170 154 164Z" fill="#769878"/>'
        "</svg>"
    )
