import csv
import json


def extract_csv():
    data_list = []
    csvpath = "../Data_collection.csv"
    jsonPath = "../Data_collection.json"

    with open(csvpath, "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            data_list.append(row)

        with open(jsonPath, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(data_list, indent=4))
    print("Done")

extract_csv()

