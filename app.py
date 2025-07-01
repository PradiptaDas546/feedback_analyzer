from flask import Flask, render_template, request
from textblob import TextBlob
import csv
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
import pandas as pd
from wordcloud import WordCloud

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = None
    if request.method == "POST":
        name = request.form["name"]
        feedback = request.form["feedback"]

        # Sentiment analysis
        blob = TextBlob(feedback)
        polarity = blob.sentiment.polarity

        if polarity > 0:
            sentiment = "Positive"
        elif polarity < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # Save to CSV
        with open("feedback.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, feedback, sentiment])

    return render_template("index.html", sentiment=sentiment)

@app.route("/chart")
def chart():
    sentiments = []
    try:
        with open("feedback.csv", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    sentiments.append(parts[2])
    except FileNotFoundError:
        sentiments = []

    counts = Counter(sentiments)
    labels = counts.keys()
    sizes = counts.values()
    colors = ['#66b3ff', '#ff9999', '#99ff99']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return render_template("chart.html", chart_type="Sentiment Pie Chart", chart_url=chart_url)

@app.route("/wordcloud")
def wordcloud_route():
    text = ""
    try:
        with open("feedback.csv", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    text += parts[1] + " "
    except FileNotFoundError:
        text = "No feedback yet"

    wc = WordCloud(width=600, height=400, background_color="black", colormap="viridis").generate(text)
    img = io.BytesIO()
    wc.to_image().save(img, format="PNG")
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    return render_template("chart.html", chart_type="Feedback Word Cloud", chart_url=chart_url)

@app.route("/download")
def download():
    try:
        df = pd.read_csv("feedback.csv", names=["Name", "Feedback", "Sentiment"])
        df.to_excel("feedback.xlsx", index=False)
        return "✅ Excel file 'feedback.xlsx' exported successfully!"
    except Exception as e:
        return f"❌ Failed to export: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
