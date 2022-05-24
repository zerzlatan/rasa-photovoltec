import spacy
nlp = spacy.load("de_core_news_md",disable=['parser','ner'])
text3 = "Gerahmte Module? Hier sind 15. Du brauchst 33? 223. gerahmtes modul, weiße farbe blaues, Gerahmtes, gerahmtere, gerahmteres Gerahmteres"
text2 = "15. 221."
text4 = "alufarbene Schiene, weißes stück, weißaluminiumfarbenes bauteil, schwarze schiene, schwarzes bauteil weisses teil"
text5 = "weißem, dunkel dunkles dunkler dunklen dunkele"
text6 = "metallen metallenen metallenes metallener metallene metallern metallfarben metallig"
text7 = "schwarz schwarze schwarzer schwarzes schwarzen schwarz"
text8 = "hell helle heller helles hellen hellem hell von dem hellem "
text9 = "dunkler ausfuehrung, dunkle version, dunkler farbe, seitliche Nutung seitliches nutung seitlicher nutung seitlichen nutung seitlichem nutung"
text10 = "breite Standardmontageschienen, breit gebaut, breiter Durchschnitt, breites Ende, breiten Kasper, breitem Grund, breiteres Folgen"
text11 = "breites profil, breiter profile, breite profil, breiteres profil, hohes profil, hoches profil, hohe ausführung, hoher kerl, hohes kerle, breite 80er Montageschienen, breites Montageschienen"
text12 = "ultraleichtes Profil, ultraleichte Schiene, ultraleichter Kerl, ultraleichten Ausführung ultraleichtem Charakter ultra-leichter ultra-leichte"
text13 = "Mittelklemmen, Mittelklemme, Klemmen, Solarmodule, Module, des Moduls"
text14 = "vierziger Montageschienen Vierziger Achtziger Nutensteine achtziger Montageschiene"
text = "wasiclip , wasi, wasi-clip, glas, gerahmt, gerahmte"
doc = nlp(text.replace(".",""))
text_no_punct = [token for token in doc if not token.is_punct]

f = ' '.join(t.text for t in text_no_punct)
print(f)
print('SpaCy:' + str([token.lemma_ for token in nlp(text)][0]))
print(str([token.lemma_ for token in nlp(text)])) 
#text = "helles"
doc = nlp(text)
print(str([token.lemma_ for token in nlp(text)]))
f = [token.lemma_ for token in nlp(text7)]
print(f)