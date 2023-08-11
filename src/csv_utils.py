import csv


def load_csv(file_path):
    data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append({
                'stid': row['stid'],
                'time': row['time'],
                'elev': float(row['elev']),
                'lat': float(row['lat']),
                'lon': float(row['lon']),
                'tair': float(row['tair'])
            })
    return data
