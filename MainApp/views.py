# Standard Library Imports
import sys
import time
from datetime import datetime
from io import TextIOWrapper

# Third-Party Library Imports
import pandas as pd
from asgiref.sync import sync_to_async

# Django Imports
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.http import HttpResponse
from django.conf import settings

# Local Imports
from .utils import save_file_async, save_json_file_async


def index(request):
    if request.method == 'GET':
        context = {
            'file_url': request.session.pop('file_url', None),
            'error': request.session.pop('error', None),
        }

        return render(request, 'MainApp/upload_csv.html', context)

    return HttpResponse("Method Not Allowed", status=405)


async def upload_csv(request, *args, **kwargs):
    """
    Handles POST requests. Processes the uploaded CSV, generates timeframe specific candles,
    and saves the result in a JSON file.

    Returns:
        Redirects to the same view after processing the data with the file url to download or
        an error message.
    """
    try:
        if request.method == 'POST':
            st = time.time()

            # Retrieve CSV file and timeframe from the form
            csvfile = request.FILES.get('csv_file')
            timeframe = int(request.POST.get('timeframe'))
            timestamp = datetime.now().strftime('%Y-%b-%d-%H-%M-%S')

            # Use TextIOWrapper to handle encoding
            data = TextIOWrapper(csvfile.file, encoding=request.encoding)

            # Generate a unique filename based on the current datetime
            file_path = f'{settings.MEDIA_ROOT}/uploads/{timestamp}.csv'

            # Save the file content to the storage asynchronously
            await save_file_async(data.read(), file_path)

            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Data cleaning
            # Convert 'VOLUME' column to numeric, handling non-numeric values
            df['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')

            # Combine 'DATE' and 'TIME' columns into a single 'DATETIME' column
            df['DATETIME'] = pd.to_datetime(df['DATE'].astype(str) + ' ' + df['TIME'], format='%Y%m%d %H:%M')

            # Sort DataFrame by 'DATETIME'
            df = df.sort_values(by='DATETIME')

            # Add an 'INDEX' column as a range of integers
            df['INDEX'] = range(len(df))

            # Group by timeframe and aggregate
            candles = (
                df.groupby(df['INDEX'] // timeframe)
                .agg({
                    'BANKNIFTY': 'first',
                    'DATE': 'first',
                    'TIME': 'first',
                    'OPEN': 'first',
                    'HIGH': 'max',
                    'LOW': 'min',
                    'CLOSE': 'last',
                    'VOLUME': 'sum'
                })
            )

            candles.reset_index(drop=True, inplace=True)

            # Save the DataFrame to a JSON file asynchronously
            filename = f'{timeframe}-min-candles-{timestamp}.json'
            await save_json_file_async(candles, filename)

            # Store the file URL in the session
            await sync_to_async(request.session.__setitem__)('file_url', f'{settings.HOST_URL}{settings.MEDIA_URL}converted/{filename}')

            print(f'Time taken - {time.time() - st}')
        else:
            return HttpResponse("Method Not Allowed", status=405)
    except Exception as e:
        _, __, exc_tb = sys.exc_info()
        print(f'Error - {str(e)} at {exc_tb.tb_lineno}')
        await sync_to_async(request.session.__setitem__)('error', 'Error while procesing the file')

    return redirect('mainapp:index')

