
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Union

import arabic_reshaper
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from hazm import Normalizer, sent_tokenize, word_tokenize
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """Analize a chat of telegram by json file
    """
    def __init__(self, json_chat: Union[str, Path]):
        """
        Args:
            json_chat : export json file from telegram group
        """

        # load chat dada
        with open(json_chat) as f:
            self.json_chat = json.load(f)
        self.normalizer = Normalizer()

        # load stop words
        stop_words = open(DATA_DIR / 'stop_words.txt').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = self.normalizer.normalize(' '.join(stop_words))

    @staticmethod
    def delete_stop_words(text, stop_words):
        """delete stop words

        Args:
            text : the text to remove its stop words
            stop_words : the string of stop words

        Returns:
            string: a text with out stop words
        """
        text_tokenize = word_tokenize(text)
        text_content = list(filter(lambda item : item not in stop_words, text_tokenize))
        return ''.join(text_content)

    @staticmethod                   
    def rebuild_text(mylist: list):
        """conver list of texts to a new string

        Args:
            mylist: list of texts

        Returns:
            text: return new text
        """
        msg_text = ''
        for item in mylist:
            if 'text' in item and isinstance(item, dict):
                msg_text += item['text']
            elif isinstance(item, str):
                msg_text += item
        return msg_text

    def msg_has_question(self, msg: str):
        """detect a sentence has question or not

        Args:
            messages (_type_): _description_
        """
        
        if not isinstance(msg['text'], str):
            msg['text'] = self.rebuild_text(msg['text'])
                
        sentences = sent_tokenize(msg['text'])
        for sentence in sentences:
            if ('?' in sentence) or ('؟' in sentence):
                return True
                
        return False
                
    def get_top_users(self, top_n: int=10):
        """Return top_n active users from a chat

        Args:
            top_n: number of top users. Defualt to 10

        Returns:
            dict: top_n users
        """
        # chech if a message is question or not
        is_question = defaultdict(bool)
        for msg in self.json_chat['messages']:
            is_question[msg['id']] = self.msg_has_question(msg)

        # check users who answer the questions
        users = []
        for msg in self.json_chat['messages']:
            if not msg.get('reply_to_message_id'):
                continue
                
            # users[msg['from_id']].append(msg['reply_to_message_id'])
            if is_question[msg['reply_to_message_id']] is False:
                continue
            users.append(msg['from'])
        return dict(Counter(users).most_common(top_n))
        
    def genrate_word_cloud(self, output_file: Union[Path, str]):
        """generate a word cloud by json file

        Args:
            output_file : path to store a word cloud image
        """
        text_content = ''
        for message in self.json_chat['messages']:
            if type(message['text']) is str:
                deleted_words = self.delete_stop_words(message['text'], self.stop_words)
                text_content += deleted_words
                
            elif type(message['text']) is list:
                for txt in message['text']:
                    if 'text' in txt:
                        deleted_words = self.delete_stop_words(txt['text'], self.stop_words)
                        text_content += deleted_words
        
        # normalize and reshape of word cloud
        text_content = arabic_reshaper.reshape(self.normalizer.normalize(text_content))
        text_content = get_display(text_content)

        # generate word cloud -> final step
        wordcloud = WordCloud(
            font_path=str(DATA_DIR / 'NotoNaskhArabic-Regular.ttf') ,
            background_color='white').generate(text_content)

        # store final word cloud
        wordcloud.to_file(str(Path(output_file) / 'word_cloud.png'))


if __name__ == '__main__':
    test = ChatStatistics(json_chat=DATA_DIR / 'python_gp.json')
    # test.genrate_word_cloud(DATA_DIR)
    print(test.get_top_users())
    print('done')
