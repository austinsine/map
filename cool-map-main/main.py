import gspread
from flask import Flask, render_template
import folium
import webbrowser
import pandas as pd
from folium.plugins import MarkerCluster
import branca
import re

app = Flask(__name__)

gc = gspread.service_account()

worksheet = gc.open('colorado_springs')
sheet = worksheet.get_worksheet(0)

get_worksheet_re = re.compile(r'(?<=\').*(?=\')')
# header title
worksheet_value = get_worksheet_re.search(str(worksheet)).group(0)

df = pd.DataFrame(sheet.get_all_records())
df = df.astype(str)

location = df[['Latitude', 'Longitude']]
location_list = location.values.tolist()


def __init__(self, center, zoom_start):
    self.center = center
    self.zoom_start = zoom_start


def propertyColors(df):
    if df['Status'] == 'Loaded':
        return 'green'

    elif df['Status'] == 'Waiting to hear back':
        return 'orange'

    elif df['Status'] == 'Not an option':
        return 'red'

    else:
        return 'darkblue'


df['color'] = df.apply(propertyColors, axis=1)


@app.route('/')
def root():
        # Create the map
    my_map = folium.Map(
        location=[38.8339, -104.8214], zoom_start=12, location_list=location_list)

    marker_cluster = MarkerCluster().add_to(my_map)

    for marker in range(0, len(location_list)):
        property_name = df['Property Name'].iloc[marker]
        year_built = df['Year Built'].iloc[marker]
        parking_ratio = df['Parking Ratio'].iloc[marker]
        bldg_size = df['RBA'].iloc[marker]
        available_space = df['Total Available Space (SF)'].iloc[marker]
        broker_co = df['Leasing Company Name'].iloc[marker]
        broker_name = df['Leasing Company Contact'].iloc[marker]
        broker_phone = df['Leasing Company Phone'].iloc[marker]
        notes = df['Notes'].iloc[marker]

        left_col_color = "#19a7bd"
        right_col_color = "#f2f0d3"

        html = '''<head>
            <h4 style="margin-bottom:10"; width="200px">{}</h4>'''.format(property_name) + '''
            </head>
            <table style="height: 126px; width: 375px;">
            <tbody>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Year Built</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(year_built) + '''
            </tr>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Parking Ratio</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(parking_ratio) + '''
            </tr>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Total Building Size (SF)</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(bldg_size) + '''
            </tr>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Total Available Space (SF)</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(available_space) + '''
            </tr>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Brokerage Company</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(broker_co) + '''
            </tr>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Broker Name</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(broker_name) + '''
            </tr>
            <tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Broker Phone</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(broker_phone) + '''
            </tr>
            <td style="background-color: ''' + left_col_color + ''';"><span style="color: #ffffff;">Notes</span></td>
            <td style="width: 200px;background-color: ''' + right_col_color + ''';">{}</td>'''.format(notes) + '''
            </tbody>
            </table>
            </html>
            '''

        iframe = folium.IFrame(html, width=510, height=280)
        popup = folium.Popup(iframe, max_width=500)

        folium.Marker(location_list[marker],
                      popup=popup,
                      icon=folium.Icon(color=df['color'][marker], icon_color='white', icon='info-sign', angle=0, prefix='fa')).add_to(marker_cluster)

    my_map.save("templates/map.html")
    webbrowser.open("templates/map.html")

    return render_template('index.html', map=map, header=worksheet_value)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
