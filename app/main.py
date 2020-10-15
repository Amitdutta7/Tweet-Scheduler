from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import gspread

# Create instance of flask
app = Flask(__name__)
# Create a Service account
gc = gspread.service_account(filename='gsheet_credentials.json')
# Access a spreadsheet through sh
sh = gc.open_by_key('1pAlPkiCRRtkXDEwunnOIM1kSIpCaaakG2wK-dktpVAw')
# Acces the worksheet through sh
worksheet = sh.sheet1

class Tweet:
    def __init__(self, time, message, done, row_idx):
        self.time = time
        self.message = message
        self.done = done
        self.row_idx = row_idx

def get_date_time(date_time_str):
    date_time_obj = None
    error = None
    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        error = f'ERROR! {e}'
    
    if date_time_obj is not None:
        ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
    if not date_time_obj > ist:
        error = "ERROR! Time must be in the future"
    
    return date_time_obj, error

@app.route('/')
def tweet_list():
    tweet_records = worksheet.get_all_records()
    tweets = []
    for idx, tweet in enumerate(tweet_records, start=2):
        tweet = Tweet(**tweet, row_idx=idx) 
        tweets.append(tweet)
    
    tweets.reverse()
    n_open_tweets = sum(1 for tweet in tweets if not tweet.done)
    return render_template('base.html', tweets=tweets, n_open_tweets=n_open_tweets)

@app.route('/tweet', methods=['GET', 'POST'])
def add_tweet():
    message = request.form['message']
    if not message:
        return "Message Field is Empty"
    time = request.form['time']
    if not time:
        return "Time Field is Empty"
    pw = request.form['pw']
    if not pw:
        return "Password Field is Empty"
    if len(message) > 280:
        return "Message lenth exceeds limit" 

    date_time_obj, error = get_date_time(time)
    if error is not None:
        return error

    tweet = [str(date_time_obj), message, 0]
    worksheet.append_row(tweet)
    return redirect('/')

@app.route('/delete/<int:row_idx>')
def delete_tweet(row_idx):
    worksheet.delete_row(row_idx)
    return redirect('/')