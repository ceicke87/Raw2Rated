from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/grade", methods=["POST"])
def grade():
    card_data = request.form.get("card_data")
    # Placeholder logic for grading
    if "perfect" in card_data.lower():
        grade_result = "10 - Gem Mint"
    else:
        grade_result = "8 - Near Mint"

    return render_template("result.html", grade=grade_result)

# 👇 This part is essential for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    
