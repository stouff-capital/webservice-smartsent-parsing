import os
import datetime

from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename

import pandas as pd
import numpy as np

ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)

# utilities
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def scoring_SmartSend(indicator, performancePercentile):
    if np.isnan(performancePercentile) or np.isnan(performancePercentile):
        return np.nan
    else:
        ten = (indicator-1)
        if indicator <= 5:
            dec = int( (100-performancePercentile)/10 )
        else:
            dec = int( performancePercentile/10 )
        return ten*10 + dec


def parse_smartSent(file):
    df = pd.read_csv(file, header=1)

    df['BloombergTickerFull'] = df['Bloomberg Ticker'] + " EQUITY"
    df['dateEOD'] = datetime.datetime.now()
    df['scoring_SmartSent'] = df.apply( lambda row: scoring_SmartSend(row['Indicator'], row['Performance Percentile']), axis=1 )

    df = df.dropna( subset=['scoring_SmartSent'] )

    return df


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        if 'file' not in request.files:
            app.logger.warning('missing file')
            return render_template('index.html')

        file = request.files['file']
        if file.filename == '':
            app.logger.warning('file is empty')
            return render_template('index.html')

        if file and allowed_file(file.filename):
            df = parse_smartSent(file)
            app.logger.info('data: %s', len(df) )

            return Response(df.to_csv(columns=['BloombergTickerFull', 'dateEOD', 'scoring_SmartSent'], index =False, date_format="%Y%m%d"),
                mimetype="text/csv",
                headers={"Content-disposition": "attachment; filename=" + secure_filename(file.filename).split(".")[0] + "_" + datetime.datetime.now().strftime("%Y%m%d") + "_parsed.csv"})

        else:
            app.logger.warning('wrong extension')
            return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
