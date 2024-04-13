import pandas as pd
from django.shortcuts import render


def fetch_data():
    sheet_id = "14idxG2e0n9WdDR35Ae-0APELlpl3sSNZvhRK_r1UR90"
    sheet_name = "hackathonMarchs"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    # print(url)
    df = pd.read_csv(url)
    df.fillna("unknown", inplace=True)
    products_list = df.values.tolist()
    return products_list


def index(request):
    sheet_data = fetch_data()
    return render(request, "home.html", {"list": sheet_data, "filter": "everywhere"})


def hackathon(request, current):
    sheet_data = fetch_data()
    return render(request, "home.html", {"list": sheet_data, "filter": current})


def landing(request):
    sheet_data = fetch_data()
    return render(request, "landingpage.html", {"list": sheet_data})
