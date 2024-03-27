
import os
import pandas as pd
from flask_bootstrap import Bootstrap4, Bootstrap5
from flask import Flask, render_template

current = "Everywhere"


def main():
    sheet_id = "14idxG2e0n9WdDR35Ae-0APELlpl3sSNZvhRK_r1UR90"
    sheet_name = 'hackathonMarchs'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    df = pd.read_csv(url)
    df.fillna("unknown", inplace=True)
    products_list = df.values.tolist()
    return products_list

sheet_data = main()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

@app.route("/")
def hackathon():
    return render_template("home.html", list = sheet_data, filter = current)

@app.route("/hackathons")
def landing():
    return render_template("landingpage.html", list = sheet_data)




if __name__ == '__main__':
    app.run(debug=True)