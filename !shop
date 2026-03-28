from flask import Flask, request, jsonify

app = Flask(__name__)

# Данные магазина с двумя разделами
shop_sections = {
    "Военный": [
        {"id": 1, "name": "Пехота", "price": 50},
        {"id": 2, "name": "БТР", "price": 500},
        {"id": 3, "name": "Танк", "price": 1000},
    ],
    "Инфраструктура": [
        {"id": 4, "name": "Жилой комплекс", "price": 2000},
        {"id": 5, "name": "Завод", "price": 3000},
        {"id": 6, "name": "Электростанция", "price": 4000},
    ]
}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').strip()

    if message == '!shop':
        response_message = "Добро пожаловать в наш магазин!\n\n"
        for section, items in shop_sections.items():
            response_message += f"**{section}**:\n"
            for item in items:
                response_message += f"  {item['id']}. {item['name']} - ${item['price']}\n"
            response_message += "\n"
        return jsonify({"reply": response_message})
    else:
        return jsonify({"reply": "Команда не распознана."})

if __name__ == '__main__':
    app.run(port=5000)
