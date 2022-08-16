# sustuli1
Ein Twitterbot, der einmal täglich Variationen über ein zufällig ausgewähltes Sprichwort (deutsch oder lateinisch) tweet.
Die Sprichwörter entstammen Wiktionary und Wikiquote. Variationen bzw. Verfremdung erfolgt mittels Übersetzung durch eine Folge von 1-5 Sprachen und am Ende ins Deutsche. Als Übersetzer wird (aktuell) Google Translate genutzt, da es eine sehr große Zahl an Sprachen unterstützt.
Die Sprachfolge wird beim Tweet in eckigen Klammern angegeben.
Der Bot kommentiert passende Tweets seiner Follower mit Sprichwörtern (ohne Verfremdung) und reagiert auf Kommentare und @Mentions (mit Verfremdung).
Ein Tweet wird dann als passend eingestuft, wenn es mindestens eine Übereinstimmung mit Verben, Substantiven, Adjektiven oder Adverbien eines Sprichworts gibt. 
Bei mehreren Übereinstimmungen gibt die weniger häufige den Ausschlag (nach Häufigkeiten der Verwendung im Web). Dazu wird die Häufigkeitstabelle der Uni Tübingen verwendet:
https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/applications-tools/
Die Lemmatisierung erfolgt mit spaCy.
