from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "A1232_b1232?"

pizzas = {
    "Маргаріта": {"price": 200, "ingredients": "Томатний соус, моцарела, помідори, базилік"},
    "Гавайська": {"price": 240, "ingredients": "Консервований ананас, ніжне куряче філе, сири моцарела та пармезан"},
    "4 сира": {"price": 220, "ingredients": "Вершковий соус, сир: моцарела, чеддер, твердий, блакитний сир"},
    "Пепероні": {"price": 240, "ingredients": "Сир моцарела, гостра салямі та соус на основі томатів"},
    "Салямі": {"price": 260, "ingredients": "Томатний соус, сиров'ялена ковбаса та ніжна моцарелла"},
}

discount_codes = {
    "SUMMER20": 20,
    "WINTER15": 15,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/menu/")
def menu():
    return render_template("menu.html", pizzas=pizzas)


@app.route("/order/")
def order():
    return render_template("order.html", pizzas=pizzas)


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    print("Форма отримана: ", request.form)

    try:
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone = request.form.get('phone')
        country = request.form.get('country')
        city = request.form.get('city')
        phone_prefix = request.form.get('phone_prefix')
        delivery_option = request.form.get('delivery_option')
        discount_code = request.form.get('discount_code', '').strip()

        print(f"Дані користувача: {name}, {email}, {address}, {phone_prefix} {phone}, {country}, {city}")

        #pizzas_ordered = request.form.getlist('order_summary')
        pizzas_ordered = session.get('cart')
        print("Замовлені піци: ", pizzas_ordered)

        if not pizzas_ordered:
            flash("Проблема з замовленням: не вибрано жодної піци!", "danger")
            return redirect(url_for('order'))

        order_summary = {}
        for pizza in pizzas_ordered:
            if pizza in order_summary:
                order_summary[pizza] += 1
            else:
                order_summary[pizza] = 1

        total_price = sum(pizzas[pizza]['price'] * quantity for pizza, quantity in order_summary.items())

        discount = 0
        if discount_code in discount_codes:
            discount = discount_codes[discount_code]
            total_price *= (1 - discount / 100)
            flash(f"Вітаємо! Ви отримали знижку {discount}%.", "success")
        elif discount_code:
            flash("Невірний код знижки.", "danger")

        delivery_time = "Піца буде готова через 20 хвилин." if delivery_option == 'pickup' else "Доставка займе приблизно 30-40 хвилин."

        reset_cart()

        order_details = {
            'name': name,
            'email': email,
            'address': address,
            'phone': f"{phone_prefix} {phone}",
            'country': country,
            'city': city
        }

        return render_template(
            "order_confirmation.html",
            order_details=order_details,
            order_summary=order_summary,
            total_price=total_price,
            pizzas=pizzas,
            delivery_time=delivery_time
        )

    except KeyError as e:
        flash(f"Виникла помилка: не знайдено ключа {e.args[0]}", "danger")
        return redirect(url_for('order'))


def reset_cart():
    print("Очищення корзини...")
    session.pop('cart', None)
    session.modified = True


@app.route('/reset_cart')
def reset_cart_route():
    reset_cart()
    return redirect(url_for('index'))


@app.get("/cart/")
def cart():
    order_summary = {pizza: quantity for pizza, quantity in session.get('cart', {}).items() if quantity > 0}
    total = sum(pizzas[pizza]['price'] * quantity for pizza, quantity in order_summary.items())
    return render_template("cart.html", order_summary=order_summary, pizzas=pizzas, total=total)


@app.route("/update_cart", methods=["POST"])
def update_cart():
    pizza = request.form.get("pizza")
    quantity = request.form.get("quantity", type=int)

    if 'cart' in session and pizza in session['cart']:
        if quantity > 0:
            session['cart'][pizza] = quantity
        else:
            session['cart'].pop(pizza, None)

    session.modified = True
    return redirect(url_for("cart"))


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    pizza = request.form.get("pizza")
    if 'cart' in session and pizza in session['cart']:
        session['cart'].pop(pizza, None)
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    pizza = request.form.get("pizza")
    quantity = request.form.get("quantity", type=int)

    if 'cart' not in session:
        session['cart'] = {}
    if pizza in session['cart']:
        session['cart'][pizza] += quantity
    else:
        session['cart'][pizza] = quantity

    session.modified = True
    return redirect(url_for("add_confirmation", pizza=pizza, quantity=quantity))


@app.route("/add_confirmation")
def add_confirmation():
    pizza = request.args.get("pizza")
    quantity = request.args.get("quantity")

    return render_template("add_confirmation.html", pizza=pizza, quantity=quantity)


if __name__ == "__main__":
    app.run(debug=True)


