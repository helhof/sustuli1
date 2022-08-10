from deep_translator import GoogleTranslator
import tweepy
import logging
import spacy
import datetime
import os
import random

# Zugangsschlüssel lesen (als Systemumgebungsvariablen gespeichert)
api_key = os.getenv('API_KEY')
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')


class Proverb:
    def __init__(self):
        # Klasse ruft die API auf und liefert Übersetzungen zurück
        goo_tr = GoogleTranslator()
        self.all_langs = goo_tr.get_supported_languages(as_dict=True)
        # Deutsche Sprichwörter
        with open('c:/Users/Alonso/PycharmProjects/Twitterbot_sustuli1/proverbs_ger.txt', 'r', encoding='UTF-8') as q:
            self.all_lines = q.readlines()
        # Lateinische Sprichwörter
        with open('c:/Users/Alonso/PycharmProjects/Twitterbot_sustuli1/proverbs_lat.txt', 'r', encoding='UTF-8') as q:
            self.latin_lines = q.readlines()
        self.proverb = ''
        self.start_proverb = ''
        # Lemmata für die Analyse lesen
        self.lemmata = {}
        with open(r'c:/Users/Alonso/PycharmProjects/Twitterbot_sustuli1/lemmata_score.txt', 'r', encoding='UTF-8') as f:
            text_fr = f.readlines()
        for lemma in text_fr:
            x = lemma.strip().split("\t")
            self.lemmata[(x[0], x[1])] = x[2:]
        self.nlp = spacy.load('de_core_news_md')

    def translate(self, proverb='', lat=False, quot_mark=False):
        while True:
            # Mit Wahrscheinlichkeit 1:5 wird ein lateinisches Sprichwort gewählt
            lat_rand = random.randint(0, 4) == 4
            if proverb == '':
                if lat and lat_rand:
                    proverb = random.choice(self.latin_lines).strip()
                else:
                    proverb = random.choice(self.all_lines).strip()
            self.proverb = proverb
            self.start_proverb = proverb
            lang_way = []
            l_way = []
            l_nr = random.randint(1, 5)
            # Zufällige Sprachenfolge für die Übersetzung generieren
            while len(l_way) < l_nr:
                rnd_l = random.randint(0, len(list(self.all_langs.keys())) - 1)
                la = list(self.all_langs.values())[rnd_l]
                lang = list(self.all_langs.keys())[rnd_l]
                # Wiederholung von Sprachen unterbinden
                if la not in l_way:
                    l_way.append(la)
                    lang_way.append(lang)
            l_way.append('de')
            lang_way.append('german')
            # Von Sprache zu Sprache übersetzen
            for targ_l in l_way:
                self.proverb = GoogleTranslator(source='auto', target=targ_l).translate(self.proverb)
            if self.proverb != self.start_proverb:
                # Weg der Übersetzung anhängen
                if lat and lat_rand:
                    lang_way.insert(0, 'latin')
                else:
                    lang_way.insert(0, 'german')
                # Anführungszeichen bei Kommentaren
                if quot_mark:
                    self.proverb = '"' + self.proverb + '"'
                self.proverb = self.proverb + "\n" + "[" + "->".join(lang_way) + "]"
                return self.proverb
            else:
                self.proverb = ''

    def find_fitting_proverb(self, tweet_dict):
        # passendes Sprichwort zu Kommentar finden

        minimum = 999999999
        proverb = []
        tweet_id = 0
        for prov in tweet_dict.keys():
            # Tweet lemmatisieren
            doc = self.nlp(prov)
            for token in doc:
                a = token.pos_
                # Adverbien in gleiche Klasse wie Adjektive
                if a == 'ADV':
                    a = 'ADJ'
                b = token.lemma_.lower()
                if (a, b) in self.lemmata:
                    wert = int(self.lemmata[(a, b)][0])
                    # das seltenste Lemma bestimmt die Auswahl des Tweets
                    if wert < minimum:
                        minimum = wert
                        proverb = self.lemmata[(a, b)][1:]
                        tweet_id = tweet_dict[prov]

        if len(proverb) == 0:
            pr = ''
        else:
            # Bei mehreren passenden Sprichwörtern -> zufällig auswählen
            pr = self.all_lines[int(random.choice(proverb))]
        return pr, tweet_id


def create_api():
    # Twitter-API anlegen
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
    except Exception as er:
        logger.error("Error creating API", exc_info=True)
        raise er
    logger.info("API created")
    return api


def account_tweets(account_name):
    # Tweets eines Followers seit dem letzten Like abrufen, Retweets und Antworten weglassen
    acc_tweet = {}
    logger.info("Fetching tweets from account")
    # Maximal 60 Tweets
    tweet_list = tweepy.Cursor(s_api.user_timeline, screen_name=account_name,
                               tweet_mode='extended',
                               include_rts=False,
                               exclude_replies=True).items(60)
    for n in tweet_list:
        if n.favorited:
            # aber mindestens 20 Tweets
            if len(list(acc_tweet)) > 20:
                return acc_tweet
            else:
                return False
        acc_tweet[n.full_text] = n.id
    return acc_tweet


# Neues Sprichwort erzeugen
Prv = Proverb()
text = Prv.translate(lat=True)
# und tweeten
logger = logging.getLogger()
s_api = create_api()
s_api.update_status(status=text, auto_populate_reply_metadata=True)

# Follower ggf. mit Sprichwörtern versorgen
to_tweet = {}
logger.info("Retrieving followers")
for page in tweepy.Cursor(s_api.get_followers, screen_name='sustuli1',
                          count=200).pages(1):
    for user in page:
        tweets = account_tweets(user.screen_name)
        if tweets:
            proverb_sel, tweet_no = Prv.find_fitting_proverb(tweets)
            # nur wenn passendes Sprichwort gefunden wurde
            if proverb_sel != '':
                to_tweet[tweet_no] = proverb_sel

# Kommentare und Mentions verarbeiten
logger.info("Retrieving comments & mentions")
# nur letzte 24 h berücksichtigen
yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
for page in tweepy.Cursor(s_api.mentions_timeline, tweet_mode='extended', count=200).pages(1):
    for tweet in page:
        # nur Tweets, die noch nicht verarbeitet wurden
        if tweet.created_at > yesterday and not tweet.favorited:
            proverb_sel, tweet_nr = Prv.find_fitting_proverb({tweet.full_text: tweet.id})
            text = Prv.translate(proverb=proverb_sel, lat=True, quot_mark=True)
            to_tweet[tweet.id] = text

# Tweets kommentieren
for nr in to_tweet:
    # Tweet mit Like versehen (zugleich Bearbeitungsmerkmal für nächsten Lauf)
    logger.info(f"Liking tweet {nr}")
    try:
        s_api.create_favorite(nr)
    except tweepy.errors as e:
        logger.error("Error on like", exc_info=True)
    # Tweet mit Sprichwort beantworten
    logger.info(f"Commenting on tweet {nr}")
    try:
        s_api.update_status(to_tweet[nr], in_reply_to_status_id=nr, auto_populate_reply_metadata=True)
    except tweepy.errors as e:
        logger.error("Error on comment", exc_info=True)
