# telegram_statistics
Export statistical information from telegram's chats

## How to Run
First, in main repo directory, run the following code to add `src` to your `PYTHONPATH`:
```
export PYTHONPATH=${PWD}
```
Then run:
```
python src/chat_statistics/stats.py
```
to generate a word cloud of your json data in `DATA_DIR` 