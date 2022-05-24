from itertools import islice
from typing import Any, Text, Dict, List
from attr import asdict
from numpy import append
import io
import re
from spellchecker import SpellChecker
import json
import spacy
import csv
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import datetime as dt
from sqlalchemy import false, true 
import zahlwort2num as w2n
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import EventType, SlotSet, AllSlotsReset, ConversationPaused, ConversationResumed
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
nlp = spacy.load("de_core_news_md",disable=['parser','ner'])            #spacys NER for citys and companies is useless here -> hoping to achieve better performance with this

class ActionTellTime(Action):
    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        response = "Die aktuelle Uhrzeit ist " + dt.datetime.now().strftime("%H:%M:%S")
        dispatcher.utter_message(text=response)
        
        return []
        
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []



def umlaut(txt):
    """
    Replace umlauts for a given text
    
    :param word: text as string
    :return: manipulated text as str
    """
    
    tempVar = txt # local variable
    
    # Using str.replace() 
    
    tempVar = tempVar.replace('ä', 'ae')
    tempVar = tempVar.replace('ö', 'oe')
    tempVar = tempVar.replace('ü', 'ue')
    tempVar = tempVar.replace('Ä', 'Ae')
    tempVar = tempVar.replace('Ö', 'Oe')
    tempVar = tempVar.replace('Ü', 'Ue')
    tempVar = tempVar.replace('ß', 'ss')
    
    return tempVar
# class ActionInterpret(Action):        geloest mit genauerer Analyse der FormValidationActions, es koennen zwar in derart Methoden keine Events ausgefuehrt werden,  jedoch besteht die Moeglichkeit der Modifikation von weiterne Slots
    
#     def name(self) -> Text:
#         return "action_interpret"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> Dict[Text, Any]:
#         print("validate hook data (action_interpret)")
#         print(tracker.get_slot(key="requested_slot"))
#         print(tracker.get_slot("requested_slot"))
#         if tracker.get_slot("requested_slot") == 'adjustable':
#                 print("start interpreting")
#                 print(tracker.get_intent_of_latest_message())
#                 intent = tracker.get_intent_of_latest_message()
#                 print(str(type(intent)))
#                 if intent is None:
#                     return [SlotSet("adjustable", None),SlotSet("requested_slot", "adjustable")]    #start with step 1 of conversation over again
#                 if intent.lower() == 'deny':
#                     return [SlotSet("adjustable", "verstellbar"),SlotSet("requested_slot", "heavy_versions")]
#                 if intent.lower() == 'affirm':
#                     return [SlotSet("adjustable", "nicht verstellbar"),SlotSet("heavy_versions", "leichte Ausfuehrung"),SlotSet("requested_slot","sales_units")]
#                 else:
#                     return [SlotSet("adjustable", None),SlotSet("requested_slot", "adjustable")]
        # if tracker.get_slot("requested_slot") == 'heavy_versions':
        #         print("start interpreting heavy_versions")
        #         intent = tracker.get_intent_of_latest_message()
        #         print(intent)
        #         if intent.lower() == 'affirm':
        #             return [SlotSet("heavy_versions", "schwere Ausfuehrung")]
        #         if intent.lower() == 'deny':
        #             return [SlotSet("heavy_versions", "leichte Ausfuehrung")]
        #         else:
        #             return [SlotSet("heavy_versions", None)]

class ActionDeleteNumberPosition(Action):
    def name(self) -> Text:
        return "action_delete_number_position"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Dict[Text, Any]:
        print("delete_number_position")
        counter = 0
        fdata = [] #final set to be uploaded
        tdata = []
        spellcheck = SpellChecker(language='de')
        with open("./db.txt") as f1:
            csvdata = csv.reader(f1, delimiter=";")
        # get current_state of db.txt
            for row in csvdata:
                data = []
                counter = counter + 1
                posnr = counter
                menge = row[0]
                ANR = row[1]
                data.append(posnr)
                data.append(menge)
                data.append(ANR)
                tdata.append(data)
        
        f1.close()
        # delete the position and upload the new state of db.txt
        curr_su = tracker.get_slot("sales_units")
        curr_sufs = tracker.get_latest_entity_values("sales_units")
        print("curr_su")
        print(curr_su)
        print("curr_sufs")
        print(curr_sufs)
        list_of_delete = []
        for i in curr_sufs:
            list_of_delete.append(i)
        
        if len(list_of_delete) > 1:
            print("multiple positions to delete")
            print("here from high to low")
            for elem in range(len(list_of_delete)):
                print(list_of_delete[elem])
                # make non-numeric values numeric
                if list_of_delete[elem].isnumeric():
                    print("numeric value")
                else:
                    print("vor Spellcheck" + list_of_delete[elem])
                    helperone = spellcheck.correction(list_of_delete[elem].replace(".",""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    list_of_delete[elem] = response_proc
            print("end for, all values numeric, before sorting (descending):")
            print(list_of_delete)
            print("sorting now. sorted list: ")
            list_of_delete = sorted(list_of_delete, key=int, reverse=True)
            print(list_of_delete)
            print("start deletion of multiple values")
            for number in list_of_delete:
                if int(number) <= len(tdata):
                    print("this number is not greater as the list " + str(number))
                    calc = int(number) - 1
                    tdata.pop(calc)
                else:
                    print("resetting all slots")
                    AllSlotsReset()
                    dispatcher.utter_message("Die zu löschende Position existiert nicht!")
                    return []
            for i in tdata:
                data = []
                pos = i[0]
                menge = i[1]
                anr = i[2]
                data.append(pos)
                data.append(menge)
                data.append(anr)
                fdata.append(data)
            print("finished for-loop delete multiple position")
            open('db.txt', 'w').close()
            print("tdata length: ")
            print(len(tdata))
            print("fdata length: ")
            print(len(fdata))
            file_object = open('db.txt', 'a')
            for i in fdata:
                temp_string = "" + i[1] +";" + i[2] + "\n"
                file_object.write(temp_string)
            file_object.close()
            message = "Positionen: "
            for i in list_of_delete:
                message = message + i + ", "
            message = message[:-2] # delete the last comma
            message = message + " wurde erfolgreich entfernt! Wie kann ich sonst noch helfen?"
            dispatcher.utter_message(message)
            print("resetting all slots")
            AllSlotsReset()
            return []
        
        else:
            print("single deletion")
            print("position to delete: ")
            print(str(curr_su))
            print("is smaller than length:")
            print(len(tdata))
            if curr_su.isnumeric():
                print("value is numeric single")
            else:
                print("vor Spellcheck" + curr_su)
                helperone = spellcheck.correction(curr_su.replace(".",""))
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                curr_su = response_proc
            if int(curr_su) <= len(tdata):
                for i in tdata:
                    if int(i[0]) == int(curr_su): # spare this entry
                        print("do_nothing at position: ")
                        print(str(i[0]))
                    else:
                        data = []
                        pos = i[0]
                        menge = i[1]
                        anr = i[2]
                        data.append(pos)
                        data.append(menge)
                        data.append(anr)
                        fdata.append(data)
                print("finished for-loop")
                open('db.txt', 'w').close()
                print("tdata length: ")
                print(len(tdata))
                print("fdata length: ")
                print(len(fdata))
                file_object = open('db.txt', 'a')
                for i in fdata:
                    temp_string = "" + i[1] +";" + i[2] + "\n"
                    file_object.write(temp_string)
                file_object.close()
                dispatcher.utter_message("Position " + str(curr_su) + " wurde erfolgreich entfernt! Wie kann ich sonst noch helfen?")
                print("resetting all slots")
                AllSlotsReset()
                return []
            else:
                print("resetting all slots")
                AllSlotsReset()
                dispatcher.utter_message("Die zu löschende Position existiert nicht!")
                return []

class ActionDeleteLatestPosition(Action):
    def name(self) -> Text:
        return "action_delete_latest_position"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Dict[Text, Any]:
        print("delete_latest_position")
        counter = 0
        fdata = [] #final set to be uploaded
        tdata = []
        with open("./db.txt") as f1:
            csvdata = csv.reader(f1, delimiter=";")
        # get current_state of db.txt
            for row in csvdata:
                data = []
                counter = counter + 1
                posnr = counter
                menge = row[0]
                ANR = row[1]
                data.append(posnr)
                data.append(menge)
                data.append(ANR)
                tdata.append(data)
        
        f1.close()
        calc = len(tdata) - 1
        tdata.pop(calc)
        print("tdata")
        print(len(tdata))
        print("fdata")
        print(len(tdata))
        open('db.txt', 'w').close()
        file_object = open('db.txt', 'a')
        for i in tdata:
            print(i[1])
            temp_string = "" + i[1] +";" + i[2] + "\n"
            file_object.write(temp_string)
        file_object.close()
        dispatcher.utter_message("Position " + str(calc) + " wurde erfolgreich entfernt! Wie kann ich sonst noch helfen?")
        print("resetting all slots")
        AllSlotsReset()





        

        


class ActionInterpretID(Action):
    
    def name(self) -> Text:
        return "action_interpret_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Dict[Text, Any]:
        
        print("validate_id")
        print(umlaut("März"))
        m_id = tracker.get_slot("w_mount_id")
        c_id = tracker.get_slot("w_clamp_id")
        i = 0
        anr = ""
        label = ""
        print(m_id)
        print(c_id)
        if c_id is None:
            if re.match("([0-9]{4})-([0-9]{1})(.{3,13})", m_id):
                print("funktioniert!!, Dachhaken, Stockschrauben oder Adapterbleche")
                if m_id == '9543-2-82X30X5':
                    return [SlotSet("article","Adapterblech"),SlotSet("ascrew_type", "M10"), SlotSet("w_mount_id", "9543-2-82X30X5")]
                if m_id == '9544-2-82X30X5':
                    return [SlotSet("article","Adapterblech"),SlotSet("ascrew_type", "M12"), SlotSet("w_mount_id", "9544-2-82X30X5")]
                if m_id == '9216-2-10X200':
                    return [SlotSet("article", "Stockschraube"),SlotSet("alength", "200 mm"),SlotSet("build_permit", "nein"), SlotSet("w_mount_id", "9216-2-10X200")]
                if m_id == '9216-2-10X250':
                    return [SlotSet("article", "Stockschraube"),SlotSet("alength", "250 mm"),SlotSet("build_permit", "nein"), SlotSet("w_mount_id", "9216-2-10X250")]
                if m_id == '9216-2-10X200-BZ':
                    return [SlotSet("article", "Stockschraube"),SlotSet("alength", "200 mm"), SlotSet("build_permit", "ja"), SlotSet("w_mount_id", "9216-2-10X200-BZ")]
                if m_id == '9216-2-10X250-BZ':
                    return [SlotSet("article", "Stockschraube"),SlotSet("alength", "250 mm"),SlotSet("build_permit", "ja"), SlotSet("w_mount_id", "9216-2-10X200-BZ")]
                if m_id == '9525-2-140X56X8K':
                    print("Haken heavy")
                    return [SlotSet("adjustable", "verstellbar"), SlotSet("heavy_versions", "schwere Ausfuehrung"), SlotSet("article", "Dachhaken")]
                if m_id == '9525-2-140X56K':
                    print("Haken leicht, 3-fach verstellbar")
                    return [SlotSet("adjustable", "verstellbar"), SlotSet("heavy_versions", "leichte Ausfuehrung"), SlotSet("article", "Dachhaken")]
                if m_id == '9521-2-150X60W':
                    print("Haken leicht, nicht verstellbar")
                    return [SlotSet("adjustable", "nicht verstellbar"), SlotSet("heavy_versions", "leichte Ausfuehrung"), SlotSet("article", "Dachhaken")]
                else:
                    return [SlotSet("article",m_id)]
        if m_id is None:
            if re.match("([0-9]{4})-([A-Z]{2})(.{3,13})", c_id):
                counter = 0
                n = False
                print("interpret w_clamp_id")
                print("schienen interpret")
                if c_id == '9664-AL-40X40X6400UL':
                    return [SlotSet("article","schiene"),SlotSet("rail_bfeature", "ultraleicht"), SlotSet("rail_color", "weissaluminium"),SlotSet( "rail_adesign","40er Montageschienen"),SlotSet("w_clamp_id","9664-AL-40X40X6400UL")]
                if c_id == '9664-WASI15UL':
                    return [SlotSet("article","schiene"),SlotSet("rail_bfeature", "seitliche Nutung"), SlotSet("rail_color", "weissaluminium"), SlotSet("rail_adesign","40er Montageschienen"),SlotSet("w_clamp_id", "9664-WASI15UL")]
                if c_id == '9664-AL-80X40X6200':
                    return [SlotSet("article","schiene"),SlotSet("rail_bfeature", "breites profil"),SlotSet("rail_color","weissaluminium"),SlotSet("rail_adesign","80er Montageschienen"),SlotSet("w_clamp_id","9664-AL-80X40X6200")]
                if c_id == '9664-AL-40X40X6200':
                    return [SlotSet("article","schiene"),SlotSet("rail_bfeature", "standard"),SlotSet("rail_color","weissaluminium"),SlotSet("rail_adesign","40er Montageschienen"), SlotSet("w_clamp_id", "9664-AL-40X40X6200")]
                if c_id == '9664-AL-90X60X6200':
                    return [SlotSet("article","schiene"),SlotSet("rail_adesign","40er Montageschiene"), SlotSet("rail_color", "weissaluminium"), SlotSet("rail_bfeature", "trapezdach"), SlotSet("w_clamp_id", "9664-AL-90X60X6200")]
                
                
                with open('./zclamp_knowledge_base.json', 'r') as f:
                    data = json.load(f)
                

                ct = ""
                height = ""
                color = ""
                su_2 = ""
                f.close()
                print(type(data['clamp'][0]))
                for ite in data['clamp']:
                    print("----")
                    print(ite)
                    for key, value in ite.items():
                        if key == 'Artikelnummer':
                            anr = value
                            print(anr)
                            if anr == c_id:
                                print("erfolgreiche Pruefung, anr" + str(counter))
                                n = True
                                i = counter
                                print(n)
                        if key == 'Beschreibung':
                            label = value
                            if label == c_id:
                                    print("erfolgreiche Labelpruefung")
                                    n = True
                                    i = counter
                                    print(n)
                        if key == 'sales_units':
                            counter = counter + 1
                
                print("action_interpret_id, of for (40 values)")
                print(data['clamp'][i].get('Artikelnummer'))
                height_str = str(data['clamp'][i].get('height')) + " mm"
                if data['clamp'][i] is None:
                    return [SlotSet("w_clamp_id", "DATABASEERROR")]
                return [SlotSet("article", "Klemme"),SlotSet("framed", data['clamp'][i].get('besonderheit')), SlotSet("rail_color",data['clamp'][i].get('color')),SlotSet("clamp_type", data['clamp'][i].get('clamp_type')), SlotSet("height",height_str), SlotSet("w_clamp_id",data['clamp'][i].get('Artikelnummer'))]

            else:
                counter = 0
                with open('./zclamp_knowledge_base.json', 'r') as f:
                    data = json.load(f)
                for ite in data['clamp']:
                    print("----")
                    print(ite)
                    for key, value in ite.items():
                        if key == 'Artikelnummer':
                            anr = value
                            print(anr)
                            if anr == c_id:
                                print("erfolgreiche Pruefung, anr" + str(counter))
                                n = True
                                i = counter
                                print(n)
                        if key == 'Beschreibung':
                            label = value
                            if label == c_id:
                                    print("erfolgreiche Labelpruefung")
                                    n = True
                                    i = counter
                                    print(n)
                        if key == 'sales_units':
                            counter = counter + 1
                print(data['clamp'][i].get('Artikelnummer'))
                height_str = str(data['clamp'][i].get('height')) + " mm"
                f.close()
                if data['clamp'][i] is None:
                    return [SlotSet("w_clamp_id", "DATABASEERROR")]
                return [SlotSet("article", "Klemme"), SlotSet("framed", data['clamp'][i].get('besonderheit')), SlotSet("rail_color",data['clamp'][i].get('color')),SlotSet("clamp_type", data['clamp'][i].get('clamp_type')), SlotSet("height",height_str), SlotSet("w_clamp_id",data['clamp'][i].get('Artikelnummer'))]


class ActionUtterBauvorhabenSlots(Action):
    def name(self) -> Text:
        return "action_utter_bauvorhaben_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            abv = tracker.get_slot('abv')
            bstreet = tracker.get_slot('bstreet')
            cplz = tracker.get_slot('cplz')
            dcity = tracker.get_slot('dcity')
            message = "Bauvorhaben: " + abv + " in " + cplz +  ", " + dcity + " in der " + bstreet
            dispatcher.utter_message(message)
class ActionResetAllFormSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            print("resetting all slots")
            AllSlotsReset()
            return [AllSlotsReset()]


class ActionReadCurrentPositions(Action):
    def name(self) -> Text:
        return "action_read_current_positions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            print("reading, current positions:")
            with open('./mapping.json', 'r') as z:
                    data = json.load(z)
                    print(type(data))
            z.close()
            utter_response = "Aktuell im Angebot enthaltene Positionen sind: \n"
            f = io.open("db.txt", mode="r", encoding="utf-8")
            lis = [line.split(';', 1) for line in f]
            if len(lis) == 0:
                dispatcher.utter_message("Es befinden sich keine Positionen im derzeitigen Angebot, fuegen Sie zuerst Artikel hinzu.")
                return []
            for line in lis:
                line[1] = line[1].replace('\n', '')
            for i, x in enumerate(lis):
                for item in data['article']:
                    if x[1] == item['Id']:
                        x[1] = item['Full']
                utter_response = utter_response + "Pos {0}: {1} mal {2}".format(i+1, x[0], x[1]) + "\n"

            utter_response = utter_response + 'Sind die Positionen vollständig? So erzeugen sie die Rechnung, andernfalls fügen Sie weitere Artikel hinzu!'
            print(utter_response)
            f.close()
            dispatcher.utter_message(utter_response)
            return []


class ActionGenerateTask(Action):
    def name(self) -> Text:
        return "action_generate_final_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("generating PDF:")
        
        utter_response = " "
        pdf = PDF('P', 'mm', 'A4')
        pdf.alias_nb_pages()
        #Set auto page break

        pdf.set_auto_page_break(auto=True, margin = 22)
        pdf.add_page()
        counter = 0
        gespreis = 0.0
        tdata = []
        with open('./mapping.json', 'r') as z:
            jsondata = json.load(z)
            print(type(jsondata))
        
        with open("./db.txt") as f1:
            csvdata = csv.reader(f1, delimiter=";")
            print("csvdata length not working")
            for row in csvdata:
                data = []
                counter = counter + 1
                posnr = counter
                menge = row[0]
                preisjeeinheit = 1
                einheit = 'Stück'
                ANR = None
                print("working_sofar")
                for item in jsondata['article']:
                    if row[1] == item['Id']:
                        ANR = item['Full']
                        preisjeeinheit = item['Preis']
                        print(item['Preis'])
                print(type(ANR))
                print(str(counter))
                preis = int(row[0]) * int(preisjeeinheit)
                data.append(posnr)
                data.append(menge)
                data.append(einheit)
                data.append(ANR)
                data.append(preisjeeinheit)
                data.append(preis)
                print(data)
                tdata.append(data)
        #specify font
        # 'B' (bold), 'U' (underline), 'I' (italics), '' regular
        pdf.set_font('times', '', 12)
        counter = 0
        netto = 0
        print("laenge tdata")
        print(str(len(tdata)))
        if len(tdata) == 0:
            dispatcher.utter_message("Es befinden sich keine Positionen im derzeitigen Angebot, fuegen Sie zuerst Artikel hinzu.")
            return []
        for i in tdata:
            pdf.set_x(10)
            der_y = pdf.get_y()
            if der_y > 220:
                pdf.add_page()
            else:
                counter = counter + 1
                pdf.cell(0,5,str(counter))
                pdf.line(20, 106, 20, 223)
                pdf.line(110, 106, 110, 223)
                pdf.line(125, 106, 125, 223)
                pdf.line(146, 106, 146, 223)
                pdf.line(164, 106, 164, 223)
                pdf.line(181, 106, 181, 223)
                pdf.set_x(21)
                pdf.cell(0,5,str(i[3]))
                pdf.set_x(111)
                pdf.cell(0,5,str(i[1]))
                pdf.set_x(125)
                pdf.cell(21,5,str(i[4])+' Euro', align='R')
                pdf.set_x(145)
                buffer = float(i[5])
                mb = float("{:.1f}".format(buffer))
                pdf.cell(19,5,str(mb), align='R')
                pdf.set_x(162)
                netto = netto + float(buffer)
                mws = float(buffer) * 0.19
                mt = float("{:.1f}".format(mws))
                pdf.cell(19,5,str(mt), align='R')
                pdf.set_x(180)
                ges = buffer+mws
                gespreis = gespreis + ges
                gt = float("{:.2f}".format(ges))
                pdf.cell(0,5,str(gt), align='R')
                pdf.ln(5)
                

        gspreis = str(float("{:.2f}".format(gespreis))) #reduce to 2 digits after
        pdf.set_fill_color(0,80,180)
        pdf.cell(0,10,gspreis,align='R',fill=1)
        pdf.set_x(21)
        pdf.cell(0,10,'Nettopreis: '+ str(netto)+' Euro', align='L')
        pdf.set_x(167)
        pdf.cell(0,10, '+ 19%')
        pdf.ln(10)
        this_curr_y = pdf.get_y()
        print('Curr_y: ' + str(this_curr_y))
        this_space_to_bottom = float(225) - this_curr_y #vertical lines reach to 223
        pdf.set_fill_color(255,255,255)
        pdf.cell(200, this_space_to_bottom, '                  ' , align='L', fill=1)
        
        name_of_doc = "PV-Offer_" + dt.datetime.now().strftime("%Y%d%b%H%M%S") +".pdf"
        pdf.output("Tasks/"+str(name_of_doc))
        z.close()
        final_mess = "Das Angebot wurde erstellt und steht Ihnen nun per Mail oder im OneDrive unter '"+ name_of_doc + "' zur Verfügung, kann ich dir bei noch etwas helfen?"
        dispatcher.utter_message(final_mess)
        open('db.txt', 'w').close()
        return []

class ValidateSimpleBrickForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_brick_form"

    def validate_brick_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate 'brick_type' value"""
        print("Validation of brick_type")
        ALLOWED_ALL_BRICK_TYPES = {"ton250", "ton 250", "ziegel ton-zweifünfzig", "ziegel ton-zwei-fünfzig" ,"ziegel ton-zweihundertfünfzig", "ton-zweifünfzig-ziegel", "ton-zwei-fünfzig-ziegel", "ton-zweihundertfünfzig-ziegel", "zweifünfzig-ton-ziegel", "zwei-fünfzig-ton-ziegel", "zweihundertfünfzig-ton-ziegel" ,"zweifünfzig-tonziegel", "zwei-fünfzig-tonziegel", "zweihundertfünfzig-tonziegel", "ziegel ton zweifünfzig", "ziegel ton zwei fünfzig", "ziegel ton zweihundertfünfzig", "ton zweifünfzig ziegel", "ton zwei fünfzig ziegel", "ton zweihundertfünfzig ziegel","zweifünfzig ton ziegel", "zwei fünfzig ton ziegel", "zweihundertfünfzig ton ziegel", "zweifünfzig tonziegel" ,"zwei fünfzig tonziegel", "zweihundertfünfzig tonziegel", "ziegel ton 250", "ton 250 ziegel", "250 ton ziegel", "250 tonziegel", "ziegel ton-250", "ton-250-ziegel", "250-ton-ziegel", "250-tonziegel","ton260", "ton 260", "ziegel ton-zweisechzig","ziegel ton-zwei-sechzig", "ziegel ton-zweihundertsechzig", "ton-zweisechzig-ziegel", "ton-zwei-sechzig-ziegel", "ton-zweihundertsechzig-ziegel", "zweisechzig-ton-ziegel", "zwei-sechzig-ton-ziegel", "zweihundertsechzig-ton-ziegel", "zweisechzig-tonziegel", "zwei-sechzig-tonziegel", "zweihundertsechzig-tonziegel", "ziegel ton zweisechzig", "ziegel ton zwei sechzig", "ziegel ton zweihundertsechzig", "ton zweisechzig ziegel", "ton zwei sechzig ziegel", "ton zweihundertsechzig ziegel", "zweisechzig ton ziegel", "zwei sechzig ton ziegel", "zweihundertsechzig ton ziegel", "zweisechzig tonziegel", "zwei sechzig tonziegel", "zweihundertsechzig tonziegel", "ziegel ton 260", "ton 260 ziegel", "260 ton ziegel", "260 tonziegel", "ziegel ton-260", "ton-260-ziegel", "260-ton-ziegel", "260-tonziegel","beton", "ziegel beton", "betonziegel", "beton-ziegel", "beton ziegel","sonderziegel", "sonder-ziegel", "besondere-ziegel","sonder ziegel","besondere ziegel","ziegel ausserhalb des sortiments", "sonder", "ziegel ausserhalb der sortiment"}
        ALLOWED_BRICK_TYPES250 = {"ton250", "ton 250", "ziegel ton-zweifünfzig", "ziegel ton-zwei-fünfzig" ,"ziegel ton-zweihundertfünfzig", "ton-zweifünfzig-ziegel", "ton-zwei-fünfzig-ziegel", "ton-zweihundertfünfzig-ziegel", "zweifünfzig-ton-ziegel", "zwei-fünfzig-ton-ziegel", "zweihundertfünfzig-ton-ziegel" ,"zweifünfzig-tonziegel", "zwei-fünfzig-tonziegel", "zweihundertfünfzig-tonziegel", "ziegel ton zweifünfzig", "ziegel ton zwei fünfzig", "ziegel ton zweihundertfünfzig", "ton zweifünfzig ziegel", "ton zwei fünfzig ziegel", "ton zweihundertfünfzig ziegel","zweifünfzig ton ziegel", "zwei fünfzig ton ziegel", "zweihundertfünfzig ton ziegel", "zweifünfzig tonziegel" ,"zwei fünfzig tonziegel", "zweihundertfünfzig tonziegel", "ziegel ton 250", "ton 250 ziegel", "250 ton ziegel", "250 tonziegel", "ziegel ton-250", "ton-250-ziegel", "250-ton-ziegel", "250-tonziegel"}
        ALLOWED_BRICK_TYPES260 = {"ton260", "ton 260", "ziegel ton-zweisechzig","ziegel ton-zwei-sechzig", "ziegel ton-zweihundertsechzig", "ton-zweisechzig-ziegel", "ton-zwei-sechzig-ziegel", "ton-zweihundertsechzig-ziegel", "zweisechzig-ton-ziegel", "zwei-sechzig-ton-ziegel", "zweihundertsechzig-ton-ziegel", "zweisechzig-tonziegel", "zwei-sechzig-tonziegel", "zweihundertsechzig-tonziegel", "ziegel ton zweisechzig", "ziegel ton zwei sechzig", "ziegel ton zweihundertsechzig", "ton zweisechzig ziegel", "ton zwei sechzig ziegel", "ton zweihundertsechzig ziegel", "zweisechzig ton ziegel", "zwei sechzig ton ziegel", "zweihundertsechzig ton ziegel", "zweisechzig tonziegel", "zwei sechzig tonziegel", "zweihundertsechzig tonziegel", "ziegel ton 260", "ton 260 ziegel", "260 ton ziegel", "260 tonziegel", "ziegel ton-260", "ton-260-ziegel", "260-ton-ziegel", "260-tonziegel"}
        ALLOWED_BRICK_TYPESBT = {"beton", "ziegel beton", "betonziegel", "beton-ziegel", "beton ziegel"}
        ALLOWED_BRICK_TYPESOTHER = {"sonderziegel", "sonder-ziegel", "besondere-ziegel","sonder ziegel","besondere ziegel","ziegel ausserhalb des sortiments", "sonder", "ziegel ausserhalb der sortiment"}
        NOT_ALLOWED_BLECHZIEGEL_INCIDENT = {"ziegel","blech-ziegel", "blecherne ziegel","blechpfannen","blech-pfanne","blech-pfannen", "pfannen","blechziegel"}
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            f = [token.lemma_ for token in nlp(buffer)]
            print("entity is List brick_type")
            print(f)
            if buffer.lower() in NOT_ALLOWED_BLECHZIEGEL_INCIDENT:
                print("brick_type for blechziegel -> correcting this with code")
                return {"brick_type":None, "article":"blechziegel"}
            if buffer.lower() in ALLOWED_BRICK_TYPES250 or f[0].lower() in ALLOWED_BRICK_TYPES250:
                print("Okay! brick_type festgelegt 250-01.")
                return {"brick_type": "ton250"}
            if buffer.lower() in ALLOWED_BRICK_TYPES260 or f[0].lower() in ALLOWED_BRICK_TYPES260:
                print("Okay! brick_type festgelegt 260-01.")
                return {"brick_type": "ton260"}
            if buffer.lower() in ALLOWED_BRICK_TYPESBT or f[0].lower() in ALLOWED_BRICK_TYPESBT:
                print("Okay! brick_type festgelegt beton-01.")
                return {"brick_type": "beton"}
            if buffer.lower() in ALLOWED_BRICK_TYPESOTHER or f[0].lower() in ALLOWED_BRICK_TYPESOTHER:
                print("Okay! brick_type festgelegt sonderziegel-01.")
                return {"brick_type": "sonderziegel"}
            if f[0].lower() == 'ton':       #information in multiple words
                    if f[1].lower() == 'zweisechzig' or f[1].lower() == '260' or f[1].lower() == 'zweihundertsechzig':
                        return {"brick_type": "ton260", "sales_units":None}
                    if f[1].lower() == 'zweihundertfünfzig' or f[1].lower() == '250' or f[1].lower() == 'zweifünfzig':
                        return {"brick_type": "ton250", "sales_units":None}
            else:
                print(buffer.lower())
                dispatcher.utter_message(text=f"Unser Inventar verfuegt nur ueber folgende Ziegelarten: 'Ton250', 'Ton260','Betonziegel', 'Ziegel in Sonderausführung'.")
                return {"brick_type": None}

        else:
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            if slot_value.lower() in NOT_ALLOWED_BLECHZIEGEL_INCIDENT:
                print("brick_type for blechziegel -> correcting this with code")
                return {"brick_type":None, "article":"blechziegel"}
            if slot_value.lower() in ALLOWED_BRICK_TYPES250 or f[0].lower() in ALLOWED_BRICK_TYPES250:
                print("Okay! brick_type festgelegt 25001.")
                return {"brick_type": "ton250"}
            if slot_value.lower() in ALLOWED_BRICK_TYPES260 or f[0].lower() in ALLOWED_BRICK_TYPES260:
                print("Okay! brick_type festgelegt 26001.")
                return {"brick_type": "ton260"}
            if slot_value.lower() in ALLOWED_BRICK_TYPESBT or f[0].lower() in ALLOWED_BRICK_TYPESBT:
                print("Okay! brick_type festgelegt beton01.")
                return {"brick_type": "beton"}
            if slot_value.lower() in ALLOWED_BRICK_TYPESOTHER or f[0].lower() in ALLOWED_BRICK_TYPESOTHER:
                print("Okay! brick_type festgelegt sonderziegel01.")
                return {"brick_type": "sonderziegel"}
            if f[0].lower() == 'ton':       #information in multiple words
                    if f[1].lower() == 'zweisechzig' or f[1].lower() == '260' or f[1].lower() == 'zweihundertsechzig':
                        return {"brick_type": "ton260", "sales_units":None}
                    if f[1].lower() == 'zweihundertfünfzig' or f[1].lower() == '250' or f[1].lower() == 'zweifünfzig':
                        return {"brick_type": "ton250", "sales_units":None}
            else:
                print(slot_value.lower())
                dispatcher.utter_message(text=f"Unser Inventar verfuegt nur ueber folgende Ziegelarten: 'Ton250', 'Ton260','Betonziegel', 'Ziegel in Sonderausführung'.")
                return {"brick_type": None}

    def validate_sales_units(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """Validate sales_units value"""
        print("validation of sales_units brick")
        ALLOWED_ALL_BRICK_TYPES = {"ton250", "ton 250", "ziegel ton-zweifünfzig", "ziegel ton-zwei-fünfzig" ,"ziegel ton-zweihundertfünfzig", "ton-zweifünfzig-ziegel", "ton-zwei-fünfzig-ziegel", "ton-zweihundertfünfzig-ziegel", "zweifünfzig-ton-ziegel", "zwei-fünfzig-ton-ziegel", "zweihundertfünfzig-ton-ziegel" ,"zweifünfzig-tonziegel", "zwei-fünfzig-tonziegel", "zweihundertfünfzig-tonziegel", "ziegel ton zweifünfzig", "ziegel ton zwei fünfzig", "ziegel ton zweihundertfünfzig", "ton zweifünfzig ziegel", "ton zwei fünfzig ziegel", "ton zweihundertfünfzig ziegel","zweifünfzig ton ziegel", "zwei fünfzig ton ziegel", "zweihundertfünfzig ton ziegel", "zweifünfzig tonziegel" ,"zwei fünfzig tonziegel", "zweihundertfünfzig tonziegel", "ziegel ton 250", "ton 250 ziegel", "250 ton ziegel", "250 tonziegel", "ziegel ton-250", "ton-250-ziegel", "250-ton-ziegel", "250-tonziegel","ton260", "ton 260", "ziegel ton-zweisechzig","ziegel ton-zwei-sechzig", "ziegel ton-zweihundertsechzig", "ton-zweisechzig-ziegel", "ton-zwei-sechzig-ziegel", "ton-zweihundertsechzig-ziegel", "zweisechzig-ton-ziegel", "zwei-sechzig-ton-ziegel", "zweihundertsechzig-ton-ziegel", "zweisechzig-tonziegel", "zwei-sechzig-tonziegel", "zweihundertsechzig-tonziegel", "ziegel ton zweisechzig", "ziegel ton zwei sechzig", "ziegel ton zweihundertsechzig", "ton zweisechzig ziegel", "ton zwei sechzig ziegel", "ton zweihundertsechzig ziegel", "zweisechzig ton ziegel", "zwei sechzig ton ziegel", "zweihundertsechzig ton ziegel", "zweisechzig tonziegel", "zwei sechzig tonziegel", "zweihundertsechzig tonziegel", "ziegel ton 260", "ton 260 ziegel", "260 ton ziegel", "260 tonziegel", "ziegel ton-260", "ton-260-ziegel", "260-ton-ziegel", "260-tonziegel","beton", "ziegel beton", "betonziegel", "beton-ziegel", "beton ziegel","sonderziegel", "sonder-ziegel", "besondere-ziegel","sonder ziegel","besondere ziegel","ziegel ausserhalb des sortiments", "sonder", "ziegel ausserhalb der sortiment"}
        ALLOWED_BRICK_TYPES250 = {"ton250", "ton 250", "ziegel ton-zweifünfzig", "ziegel ton-zwei-fünfzig" ,"ziegel ton-zweihundertfünfzig", "ton-zweifünfzig-ziegel", "ton-zwei-fünfzig-ziegel", "ton-zweihundertfünfzig-ziegel", "zweifünfzig-ton-ziegel", "zwei-fünfzig-ton-ziegel", "zweihundertfünfzig-ton-ziegel" ,"zweifünfzig-tonziegel", "zwei-fünfzig-tonziegel", "zweihundertfünfzig-tonziegel", "ziegel ton zweifünfzig", "ziegel ton zwei fünfzig", "ziegel ton zweihundertfünfzig", "ton zweifünfzig ziegel", "ton zwei fünfzig ziegel", "ton zweihundertfünfzig ziegel","zweifünfzig ton ziegel", "zwei fünfzig ton ziegel", "zweihundertfünfzig ton ziegel", "zweifünfzig tonziegel" ,"zwei fünfzig tonziegel", "zweihundertfünfzig tonziegel", "ziegel ton 250", "ton 250 ziegel", "250 ton ziegel", "250 tonziegel", "ziegel ton-250", "ton-250-ziegel", "250-ton-ziegel", "250-tonziegel"}
        ALLOWED_BRICK_TYPES260 = {"ton260", "ton 260", "ziegel ton-zweisechzig","ziegel ton-zwei-sechzig", "ziegel ton-zweihundertsechzig", "ton-zweisechzig-ziegel", "ton-zwei-sechzig-ziegel", "ton-zweihundertsechzig-ziegel", "zweisechzig-ton-ziegel", "zwei-sechzig-ton-ziegel", "zweihundertsechzig-ton-ziegel", "zweisechzig-tonziegel", "zwei-sechzig-tonziegel", "zweihundertsechzig-tonziegel", "ziegel ton zweisechzig", "ziegel ton zwei sechzig", "ziegel ton zweihundertsechzig", "ton zweisechzig ziegel", "ton zwei sechzig ziegel", "ton zweihundertsechzig ziegel", "zweisechzig ton ziegel", "zwei sechzig ton ziegel", "zweihundertsechzig ton ziegel", "zweisechzig tonziegel", "zwei sechzig tonziegel", "zweihundertsechzig tonziegel", "ziegel ton 260", "ton 260 ziegel", "260 ton ziegel", "260 tonziegel", "ziegel ton-260", "ton-260-ziegel", "260-ton-ziegel", "260-tonziegel"}
        ALLOWED_BRICK_TYPESBT = {"beton", "ziegel beton", "betonziegel", "beton-ziegel", "beton ziegel"}
        ALLOWED_BRICK_TYPESOTHER = {"sonderziegel", "sonder-ziegel", "besondere-ziegel","sonder ziegel","besondere ziegel","ziegel ausserhalb des sortiments", "sonder", "ziegel ausserhalb der sortiment"}
        f = [token.lemma_ for token in nlp(slot_value)]
        print("slot_value")
        print(f)
        if slot_value.isnumeric():
            brick_id = tracker.get_slot('brick_type')
            temp_brick_id = ""
            print(brick_id)
            #list reduce brick_id to fitting values (falsche zuweisungen vorbeugen)
            if type(brick_id) == list:
                print("multiple brickids:")
                for elem in range(len(brick_id)):                
                    f = [token.lemma_ for token in nlp(brick_id[elem])]
                    print(brick_id[elem])
                    print("f")
                    print(f[0])
                    if f[0].lower() in ALLOWED_ALL_BRICK_TYPES:
                        print("it is in the brick type set")
                        print(f[0].lower())
                        temp_brick_id = f[0].lower()               #buffer is a fitting value
                    else:
                        print("NO")
                        print(f[0].lower())
            if temp_brick_id == "":
                brick_id = brick_id
            else:
                brick_id = temp_brick_id

            print("final brickid is")
            print(brick_id.lower())
            if brick_id.lower() == 'beton' or brick_id.lower() == 'ton250' or brick_id.lower() == 'ton260' or brick_id.lower() == 'sonderziegel': # 
                print("id is set in right format sales_unit brick")
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(slot_value)+";"+ brick_id.lower()+"\n")
                file_object.close()
                #save
                return {"sales_units": slot_value}
            else:
                print("slot_value is numeric (brick) 01 todo save to list")
                dispatcher.utter_message("Spezifizieren Sie den Ziegeltypen bevor Sie ihn dem Angebot hinzufügen")
                return {"sales_units": None, "brick_type":None}
        else:
            print("slot_value sales units (brick) 02 todo save to list")
            print(slot_value.lower())
            if slot_value.lower() in ALLOWED_BRICK_TYPES250 or f[0].lower() in ALLOWED_BRICK_TYPES250:
                print("Okay! brick_type festgelegt 250 sales units 01.")
                return {"brick_type": "ton250", "sales_units":None}
            if slot_value.lower() in ALLOWED_BRICK_TYPES260 or f[0].lower() in ALLOWED_BRICK_TYPES260:
                print("Okay! brick_type festgelegt 260 sales units 01.")
                return {"brick_type": "ton260", "sales_units":None}
            if slot_value.lower() in ALLOWED_BRICK_TYPESBT or f[0].lower() in ALLOWED_BRICK_TYPESBT:
                print("Okay! brick_type festgelegt beton sales units01.")
                return {"brick_type": "beton", "sales_units":None}
            if slot_value.lower() in ALLOWED_BRICK_TYPESOTHER or f[0].lower() in ALLOWED_BRICK_TYPESOTHER:
                print("Okay! brick_type festgelegt sonderziegel sales units01.")
                return {"brick_type": "sonderziegel", "sales_units":None}
            print("nlp-slot value in brick_type sales_units")
            if f[0].lower() == 'ton':       #information in multiple words
                if f[1].lower() == 'zweisechzig' or f[1].lower() == '260' or f[1].lower() == 'zweihundertsechzig':
                    return {"brick_type": "ton260", "sales_units":None}
                if f[1].lower() == 'zweihundertfünfzig' or f[1].lower() == '250' or f[1].lower() == 'zweifünfzig':
                    return {"brick_type": "ton250", "sales_units":None}
            print("slot_value is not numeric (brick) 02 todo save to list")
            spellcheck = SpellChecker(language='de')
            print("vor Spellcheck" + slot_value)
            helperone = spellcheck.correction(slot_value.replace(".", ""))
            print("nach Spellcheck:" + helperone)
            response_proc = w2n.convert(helperone)
            print("slotvalue response_proc" + str(response_proc))
            brick_id = tracker.get_slot('brick_type')
            print(brick_id)
            print("numeric value for slot value brick")
            if brick_id.lower() == 'beton' or brick_id.lower() == 'ton250' or brick_id.lower() == 'ton260' or brick_id.lower() == 'sonderziegel': # 
                print("id is set in right format sales_unit brick")
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(response_proc)+";"+ brick_id.lower()+"\n")
                file_object.close()
                #save
                return {"sales_units": response_proc}
            return {"sales_units":response_proc}
            #return{"sales_units":response_proc}

class ValidateSimpleRailForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_rail_form"

    def validate_rail_adesign(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'rail_adesign' value NLP included"""
        print("validate rail_adesign")
        ALLOWED_DESIGN_TYPES = {"40er montageschienen", "standardmontageschienen", "standardschienen", "schwarze standardmontageschienen", "montageschienen", "schwarze schienen", "schwarz schienen", "schwarz schiene"} #Todo
        ALLOWED_OTHER_DESIGNS = {"80er montageschienen","breite montageschienen", "hohe montageschienen","breit montageschiene","breit montageschienen", "80er montageschiene", "achtziger montageschiene", "achtziger montageschienen"}
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            buffertwo = nlp(buffer)
            f = [token.lemma_ for token in nlp(buffer)]
            print("entity is List adesign")
            print(f)
            print(buffertwo)
            if f[0].lower() == '40er' or f[0].lower() == 'vierziger' or buffer.lower() in ALLOWED_DESIGN_TYPES:
                print(buffer.lower())
                return {"rail_adesign": "40er Montageschienen","article": "schiene"}
            if f[0].lower() == 'breit' or f[0].lower() == 'hoch' or f[0].lower() == '80er' or f[0].lower() == 'achtziger' or buffer.lower() in ALLOWED_OTHER_DESIGNS:
                return {"rail_bfeature": "breites profil", "rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
            if buffer.lower() in {"trapezdach-montageschienen", "trapezdach"}:
                return {"rail_adesign":"40er Montageschiene" ,"rail_color": "weissaluminium", "rail_bfeature": "trapezdach", "w_clamp_id": "9664-AL-90X60X6200"}
            else:
                print("Fehlerhafter Ausdruck: " + buffer.lower())
                #dispatcher.utter_message(text=f"Sie uebergaben einen Schienentyp, der nicht in unserem Sortiment ist")
                return {"rail_adesign": None}
        else:
            buffertwo = nlp(slot_value)
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            if f[0].lower() == '40er' or f[0].lower() == 'vierziger' or slot_value.lower() in ALLOWED_DESIGN_TYPES:
                print(slot_value.lower())
                return {"rail_adesign": "40er Montageschienen","article": "schiene"}
            if slot_value.lower() in ALLOWED_OTHER_DESIGNS or f[0].lower() == 'breit' or f[0].lower() == 'hoch' or f[0].lower() == '80er' or f[0].lower() == 'achtziger':
                return {"rail_bfeature": "breites profil", "rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
            if slot_value.lower() in {"trapezdach-montageschienen", "trapezdach"}:
                return {"rail_adesign":"40er Montageschiene" ,"rail_color": "weissaluminium", "rail_bfeature": "trapezdach", "w_clamp_id": "9664-AL-90X60X6200"}
            else:
                print("Fehlerhafter Ausdruck: " + slot_value.lower())
                #dispatcher.utter_message(text=f"Sie uebergaben einen Schienentyp, der nicht in unserem Sortiment ist")
                return {"rail_adesign": None}


    def validate_rail_color(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'rail_color' value""" #schwarze Schienen gibt es nicht in Sonderausfuehrungen im Shop, daher setzt diese Methode auch weitere Slots sollte eine schwarze Farbe gewuenscht sein

        print("validate_rail_color")
        ALLOWED_COLOR_TYPES = {"weissaluminium", "metall", "alufarben", "alufarbene", "alufarber", "metallen","metallene","metallenen","weissaluminium","weiss","hell","weißaluminium", "weiß", "weiße", "weißaluminiumfarbene","weißaluminiumfarbenes","weißaluminiumfarbener", "heller", "hellem","schwarz", "black", "schwarze","schwarzes", "schwarzen", "dunkel","dunkeln"}
        if type(slot_value) == list:
            buffer = umlaut(slot_value[0])      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            buffertwo = nlp(buffer)
            f = [token.lemma_ for token in nlp(buffer)]
            print("type: List")
            print(f)
            for item in slot_value:
                buffertwo = buffertwo + item
            print(buffertwo)
            if buffer.lower() not in ALLOWED_COLOR_TYPES:
                dispatcher.utter_message(text=f"Beachten Sie die gueltigen Farbkombinationen 01")
                return{"rail_color": None}    
            if buffer.lower() in {"schwarz","black","schwarze","schwarzem","schwarzen","dunkel","dunkeln"} or f[0].lower() == 'schwarz' or f[0].lower() == 'schwarze' or f[0].lower() == 'dunkel' or f[0].lower() == 'dunkeln':      #NLP
                return {"rail_color": "schwarz", "rail_adesign":"40er Montageschienen", "rail_bfeature":"Keine"}
            else: 
                return{"rail_color": "weissaluminium"}
        else:
            print("railcolor no_list")
            buffertwo = nlp(slot_value)
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            print(str(f[0].lower()))
            if umlaut(slot_value.lower()) not in ALLOWED_COLOR_TYPES:
                dispatcher.utter_message(text=f"Beachten Sie die gueltigen Farbkombinationen 01-1")
                return{"rail_color": None}    
            if slot_value.lower() in {"schwarz","black","schwarze","schwarzem","schwarzen","dunkel","dunkeln"} or f[0].lower() == 'schwarz' or f[0].lower() == 'schwarze' or f[0].lower() == 'dunkel' or f[0].lower() == 'dunkeln':      #NLP
                return {"rail_color": "schwarz", "rail_adesign":"40er Montageschienen", "rail_bfeature":"Keine","w_clamp_id":"9664-AL-40X40X6,4LSE"}
            else: 
                return{"rail_color": "weissaluminium"}
        

    def validate_rail_bfeature(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'rail_bfeature' value"""

        print("validate_rail_bfeature")
        for i in slot_value:
            print(i)

        ALLOWED_SPECIAL_FEATURES = {"seitliche nutung", "seitlicher nutung","seitliche","seitlicher"}
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            buffertwo = nlp(buffer)
            f = [token.lemma_ for token in nlp(buffer)]
            print("type: List")
            print(f)
            for item in slot_value:
                buffertwo = buffertwo + item
            print(buffertwo)
            if buffer.lower() in {"ultraleicht", "ultra leicht", "ultra-leicht", "ultraleichte", "ultraleichter", "ultraleichten", "ultra-leichtes", "ultraleichtes"}:          #SPACY HERE NOT WORKING! ultra-leicht zusammengesetzt, Lemmatizer greift nicht
                return {"rail_bfeature": "ultraleicht", "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen","w_clamp_id":"9664-AL-40X40X6400UL"}
            if f[0].lower() == 'seitlich' or buffer.lower() in ALLOWED_SPECIAL_FEATURES:        #check first word post-processing
                return {"rail_bfeature": "seitliche Nutung", "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen","w_clamp_id": "9664-WASI15UL"}
            if buffer.lower() in {"trapezdach", "trapez", "trapezmontageschiene", "trapezmontageschienen", "trapezdachmontage","trapezdach-montageschiene","trapezdach-montageschienen"}:
                return{"rail_bfeature":"trapezdach", "rail_color":"weissaluminium", "rail_adesign":"40er Montageschienen", "w_clamp_id":"9664-AL-90X60X6200"}
            if buffer.lower() in {"keine", "standard","standardmontage","normal"}:
                return{"rail_bfeature": "standard", "rail_color":"weissaluminium","rail_adesign":"40er Montageschienen", "w_clamp_id": "9664-AL-40X40X6200"}
            if buffer.lower() in {"breites profil", "breite profil", "breite ausfuehrung","breit","breite"} or f[0].lower() == 'breit' or f[0].lower() == 'hoch' or f[0].lower() == '80er' or f[0].lower() == 'achtziger':
                return {"rail_bfeature": "breites profil", "rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
            dispatcher.utter_message(text="Ihre Sonderausfuehrung wurde vom Chatbot nicht verstanden, ist jedoch im System vermerkt und ein Mitarbeiter wird sich in Kuerze bei Ihnen melden")
            return{"rail_bfeature": buffer}
        else:
            buffertwo = nlp(slot_value)
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            if slot_value.lower() in {"ultraleicht", "ultra leicht", "ultra-leicht", "ultraleichte", "ultraleichter", "ultraleichten", "ultra-leichtes", "ultraleichtes"}:
                return {"rail_bfeature": "ultraleicht", "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen","w_clamp_id":"9664-AL-40X40X6400UL"}
            if f[0].lower() == 'seitlich' or slot_value.lower() in ALLOWED_SPECIAL_FEATURES: #check first word post-processing
                return {"rail_bfeature": "seitliche Nutung", "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen","w_clamp_id": "9664-WASI15UL"}
            if slot_value.lower() in {"trapezdach", "trapez", "trapezmontageschiene", "trapezmontageschienen", "trapezdachmontage","trapezdach-montageschiene","trapezdach-montageschienen"}:
                return {"rail_bfeature":"trapezdach", "rail_color":"weissaluminium", "rail_adesign":"40er Montageschienen", "w_clamp_id":"9664-AL-90X60X6200"}
            if slot_value.lower() in {"keine", "standard","standardmontage","normal"}:
                return {"rail_bfeature": "standard", "rail_color":"weissaluminium","rail_adesign":"40er Montageschienen", "w_clamp_id": "9664-AL-40X40X6200"}
            if f[0].lower() == 'breit' or f[0].lower() == 'hoch' or f[0].lower() == '80er' or f[0].lower() == 'achtziger' or slot_value.lower() in {"breites profil", "breite profil", "breite ausfuehrung","breit","breite","achtziger montageschiene", "achtziger montageschienen"}:
                return {"rail_bfeature": "breites profil", "rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
            dispatcher.utter_message(text="Ihre Sonderausfuehrung wurde vom Chatbot nicht verstanden, ist jedoch im System vermerkt und ein Mitarbeiter wird sich in Kuerze bei Ihnen melden")
            return{"rail_bfeature": None}

    def validate_sales_units(self,      #hier wird die Liste befüllt, sollte erst geschehen wenn die Artikelnummer identifiziert und somit genügend Artikelinformationen bekannt
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """Validation of numeric attribute 'sales_units' value, if its a written number in german text this method will turn it into an integer """
                
        print("validate_rail_sales_unit")
        spellcheck = SpellChecker(language='de')
        lv_cid = tracker.get_slot('w_clamp_id')
        if lv_cid is None:
            print("No Sales_Units before mc_id is not known [RAIL]")
            if type(slot_value) == list: 
                print("slot_value is list")
                buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
                if buffer.isnumeric():
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Schiene")
                    return{"sales_units":None}
                else:
                    print("td")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Schiene")
                    #response_proc = w2n.convert(buffer.replace(".", ""))
                    return{"sales_units":None}
            else:
                if slot_value.isnumeric():
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Schiene")
                    return{"sales_units":None}
                else:
                    print("td")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Schiene")
                    #response_proc = w2n.convert(slot_value.replace(".", ""))
                    return{"sales_units":None}
        else:
            if type(slot_value) == list:
                buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
                if buffer.isnumeric():
                    if lv_cid == '9664-AL-40X40X6,4LSE':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":buffer, "rail_color": "schwarz", "rail_adesign":"40er Montageschienen", "rail_bfeature":"Keine","w_clamp_id":"9664-AL-40X40X6,4LSE"}
                    if lv_cid == '9664-AL-40X40X6400UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"rail_bfeature":"ultraleicht","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id":"9664-AL-40X40X6400UL"}
                    if lv_cid == '9664-WASI15UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"rail_bfeature": "seitliche Nutung","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id": "9664-WASI15UL"}
                    if lv_cid == '9664-AL-80X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"rail_bfeature": "breites profil","rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
                    if lv_cid == '9664-AL-40X40X6200':  
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"rail_bfeature": "standard","rail_color":"weissaluminium","rail_adesign":"40er Montageschienen", "w_clamp_id": "9664-AL-40X40X6200"}
                    if lv_cid == '9664-AL-90X60X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"rail_adesign":"40er Montageschiene", "rail_color": "weissaluminium","rail_bfeature": "trapezdach", "w_clamp_id": "9664-AL-90X60X6200"}
                    #return{"sales_units":buffer}
                else:
                    print("vor Spellcheck" + buffer)
                    helperone = spellcheck.correction(buffer.replace(".", ""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    print("buffer response_proc" + str(response_proc))
                    if lv_cid == '9664-AL-40X40X6,4LSE':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc, "rail_color": "schwarz", "rail_adesign":"40er Montageschienen", "rail_bfeature":"Keine","w_clamp_id":"9664-AL-40X40X6,4LSE"}
                    if lv_cid == '9664-AL-40X40X6400UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature":"ultraleicht","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id":"9664-AL-40X40X6400UL"}
                    if lv_cid == '9664-WASI15UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature": "seitliche Nutung","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id": "9664-WASI15UL"}
                    if lv_cid == '9664-AL-80X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature": "breites profil","rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
                    if lv_cid == '9664-AL-40X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature": "standard","rail_color":"weissaluminium","rail_adesign":"40er Montageschienen", "w_clamp_id": "9664-AL-40X40X6200"}
                    if lv_cid == '9664-AL-90X60X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_adesign":"40er Montageschiene", "rail_color": "weissaluminium","rail_bfeature": "trapezdach", "w_clamp_id": "9664-AL-90X60X6200"}
                    #return{"sales_units":response_proc}
            else:
                if slot_value.isnumeric():
                    print("slot_value is numeric")
                    if lv_cid == '9664-AL-40X40X6,4LSE':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value, "rail_color": "schwarz", "rail_adesign":"40er Montageschienen", "rail_bfeature":"Keine","w_clamp_id":"9664-AL-40X40X6,4LSE"}
                    if lv_cid == '9664-AL-40X40X6400UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"rail_bfeature":"ultraleicht","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id":"9664-AL-40X40X6400UL"}
                    if lv_cid == '9664-WASI15UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"rail_bfeature": "seitliche Nutung","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id": "9664-WASI15UL"}
                    if lv_cid == '9664-AL-80X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"rail_bfeature": "breites profil","rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
                    if lv_cid == '9664-AL-40X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"rail_bfeature": "standard","rail_color":"weissaluminium","rail_adesign":"40er Montageschienen", "w_clamp_id": "9664-AL-40X40X6200"}
                    if lv_cid == '9664-AL-90X60X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"rail_adesign":"40er Montageschiene", "rail_color": "weissaluminium","rail_bfeature": "trapezdach", "w_clamp_id": "9664-AL-90X60X6200"}
                else:
                    print("vor Spellcheck" + slot_value)
                    helperone = spellcheck.correction(slot_value.replace(".", ""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    print("slotvalue response_proc" + str(response_proc))
                    if lv_cid == '9664-AL-40X40X6,4LSE':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc, "rail_color": "schwarz", "rail_adesign":"40er Montageschienen", "rail_bfeature":"Keine","w_clamp_id":"9664-AL-40X40X6,4LSE"}
                    if lv_cid == '9664-AL-40X40X6400UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature":"ultraleicht","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id":"9664-AL-40X40X6400UL"}
                    if lv_cid == '9664-WASI15UL':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature": "seitliche Nutung","rail_color": "weissaluminium","rail_adesign":"40er Montageschienen","w_clamp_id": "9664-WASI15UL"}
                    if lv_cid == '9664-AL-80X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature": "breites profil","rail_color":"weissaluminium","rail_adesign":"80er Montageschienen","w_clamp_id":"9664-AL-80X40X6200"}
                    if lv_cid == '9664-AL-40X40X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_bfeature": "standard","rail_color":"weissaluminium","rail_adesign":"40er Montageschienen", "w_clamp_id": "9664-AL-40X40X6200"}
                    if lv_cid == '9664-AL-90X60X6200':
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_cid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"rail_adesign":"40er Montageschiene", "rail_color": "weissaluminium","rail_bfeature": "trapezdach", "w_clamp_id": "9664-AL-90X60X6200"}
                    #return{"sales_units":response_proc}
                 


class ActionAskRailtype(Action):

    def name(self) -> Text:
        return "action_ask_rail_adesign"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:
            """Response rail_type"""
                
            print("ActionAskRailtype startet")
            buttonset = []
            buttonset.append({'title':'Standardmontageschienen', 'payload': '/give_info{"rail_adesign":"40er Montageschienen","rail_bfeature":"standard","rail_color":"weissaluminium", "w_clamp_id": "9664-AL-40X40X6200"}'})
            buttonset.append({'title':'Montageschienen Ultra Light', 'payload': '/give_info{"rail_adesign":"40er Montageschienen","rail_bfeature":"ultraleicht","rail_color":"weissaluminium","w_clamp_id": "9664-AL-40X40X6400UL"}'})
            buttonset.append({'title':'schwarze Standardmontageschienen', 'payload': '/give_info{"rail_adesign":"40er Montageschienen","rail_bfeature":"schwarz eloxiert","rail_color":"schwarz","w_clamp_id:"9664-AL-40X40X6,4LSE"}'})
            buttonset.append({'title':'80er Montageschienen in weissaluminium mit breitem Profil', 'payload': '/give_info{"rail_adesign":"80er Montageschienen","rail_bfeature":"breites profil","rail_color":"weissaluminium","w_clamp_id":"9664-AL-80X40X6200"}'})
            buttonset.append({'title':'40er Montageschienen in weissaluminium mit seitlicher Nutung', 'payload': '/give_info{"rail_adesign":"40er Montageschienen","rail_bfeature":"seitliche nutung","rail_color":"weissaluminium, "w_clamp_id": "9664-WASI15UL""}'})
            dispatcher.utter_message(text='Welchen Profiltyp der Aluminiumschienen moechten Sie bestellen?', buttons=buttonset)
            return[]

class ActionDefaultAskAffirmation(Action):
    def name(self):
            return "action_default_ask_affirmation"
    async def run(self, dispatcher, tracker, domain):
        predicted_intents = tracker.latest_message["intent_ranking"][1:4]
        # select the top three intents from the tracker, ignore the first one -- nlu fallback
        message = "Ich habe dich nicht verstanden, was möchtest du tun?"
        intent_mappings = {
            "request_tutorial_simple": "Eine Einfuehrung in die Funktionen",
            "define_bauvorhaben": "Bauvorhaben modifizieren",
            "generate_final_task": "Rechnung in PDF generieren",
            "give_info": "Eckdaten zu einem Artikel ergaenzen",
            "affirm": "Zustimmen",
            "read_current_positions": "Positionen der Rechnung vorlesen",
            "give_sales_unit": "Menge vermitteln",
            "thanks": "Danke sagen",
            "give_height": "Hoehe bestimmen",
            "goodbye": "Auf Wiedersehen",
            "want_article": "Artikelwunsch äußern",
            "give_mount_id": "Artikel ID vermitteln (Mount)",
            "give_clamp_id": "Klemmen ID vermitteln",
            "stop": "Derzeitiges Vorgehen unterbrechen",
            "bot_challenge": "Chatbot Challenge",
            "greet": "Grüßen",
            "deny": "Nicht zustimmen"
        }
        
        # show the top three intents as buttons to the user
        buttons = [
            {
                "title": intent_mappings[intent['name']],
                "payload": "/{}".format(intent['name'])
            }
            for intent in predicted_intents
        ]
        buttons.append({
            "title": "None of These",
            "payload": "/out_of_scope"
        })
        dispatcher.utter_message(text=message, buttons=buttons)
        return []

class ValidateSimpleHookForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_hook_form"

    def validate_adjustable(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """validate adjustable"""

        print(type(slot_value))
        print("validate adjustable")
        intent = tracker.get_intent_of_latest_message()
        if intent == "affirm":
            print("true,true")
            return {"adjustable": "nicht verstellbar","heavy_versions": "leichte Ausfuehrung", "w_mount_id": "9521-2-150X60W"}
        if intent == 'deny':
            #evt.append(SlotSet("requested_slot", "heavy_version")) #NEED FOR LATER CODE #ES WERDEN KEINE EVENTS IN VALIDATE METHODEN ABGESPIELT
            return {"adjustable": "verstellbar"}
        if intent == 'give_give_mount_id':
            return {"adjustable": "verstellbar","heavy_versions": "leichte Ausfuehrung", "w_mount_id": "9521-2-150X60W"}
        # intent = tracker.latest_message['intent'].get('name')
        # print(intent)
        # if intent.lower() == 'affirm':
        #     return {"adjustable":"true"}
        # if intent.lower() == 'deny':
        #     return {"adjustable":"false","heavy_version":"false"}
        # else:
        #     return {"adjustable":"unknown"}
        
    
    def validate_heavy_versions(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate heavy_versions"""

        print("validate heavy_versions")
        print(type(slot_value))
        if slot_value.lower() == 'schwere ausfuehrung':
            return {"heavy_versions": "schwere Ausfuehrung","w_mount_id": "9525-2-140X56X8K"}
        if slot_value.lower() == 'leichte ausfuehrung':
            return {"heavy_versions": "leichte Ausfuehrung", "w_mount_id": "9525-2-140X56K"}
        if slot_value.lower() == 'none':
            return {"heavy_versions": None}
        # intent = tracker.latest_message['intent'].get('name')
        # print(intent)
        # if intent.lower() == 'affirm':
        #     return {"heavy_version":"true"}
        # if intent.lower() == 'deny':
        #     return {"heavy_version":"false"}
        # else:
        #     return {"heavy_version":slot_value}

    
    def validate_sales_units(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """Validation of numeric attribute 'sales_units' value, if its a written number in german text this method will turn it into an integer """

        print("validate sales units (hook)...") #w_mount_id
        lv_mid = tracker.get_slot('w_mount_id')
        spellcheck = SpellChecker(language='de')
        print(type(lv_mid))
        if lv_mid is None:
            print("No Sales_Units before m_id is not known [HOOK]")
            if type(slot_value) == list:
                buffer = slot_value[0]      #if multiple entities are delivered due a bug, check the first one (always 2 entities duplicate) 
                if buffer.isnumeric():
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zum Dachhaken")
                    return{"sales_units":None}
                else:
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zum Dachhaken")
                    #response_proc = w2n.convert(buffer.replace(".", ""))
                    return{"sales_units":None}
            else:
                if slot_value.isnumeric():
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zum Dachhaken")
                    return{"sales_units":None}
                else:
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zum Dachhaken")
                    #response_proc = w2n.convert(slot_value.replace(".", ""))
                    return{"sales_units":None}
        else:
            print(lv_mid)
            print("id bekannt!!")
            if type(slot_value) == list:
                buffer = slot_value[0]      #if multiple entities are delivered due a bug, check the first one (always 2 entities duplicate) 
                if buffer.isnumeric():
                    if lv_mid == '9525-2-140X56X8K':
                        print("Haken heavy")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"adjustable": "verstellbar","heavy_versions": "schwere Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9525-2-140X56K':
                        print("Haken leicht, 3-fach verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"adjustable": "verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9521-2-150X60W':
                        print("Haken leicht, nicht verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(buffer)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":buffer,"adjustable": "nicht verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                            #return{"sales_units":buffer}
                else:
                    print("vor Spellcheck" + buffer)
                    helperone = spellcheck.correction(buffer.replace(".",""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    if lv_mid == '9525-2-140X56X8K':
                        print("Haken heavy")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"adjustable": "verstellbar","heavy_versions": "schwere Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9525-2-140X56K':
                        print("Haken leicht, 3-fach verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"adjustable": "verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9521-2-150X60W':
                        print("Haken leicht, nicht verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"adjustable": "nicht verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                    #return{"sales_units":response_proc}
            else:
                if slot_value.isnumeric():
                    if lv_mid == '9525-2-140X56X8K':
                        print("Haken heavy")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"adjustable": "verstellbar","heavy_versions": "schwere Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9525-2-140X56K':
                        print("Haken leicht, 3-fach verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"adjustable": "verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9521-2-150X60W':
                        print("Haken leicht, nicht verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(slot_value)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":slot_value,"adjustable": "nicht verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                        #return{"sales_units":slot_value}
                else:
                    #print(umlaut(slot_value))          #UMLAUT FUNKTION AUS SALES_UNITS raus! oder Methode umprogrammieren
                    #helpertwo = umlaut(slot_value)
                    #response_test = w2n.convert(helpertwo)
                    #print("test funktioniert mit Umlautfunktion!!!" + str(response_test))
                    print("vor Spellcheck" + slot_value)
                    helperone = spellcheck.correction(slot_value.replace(".", ""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    print(response_proc)
                    print(type(lv_mid))
                    if lv_mid == '9525-2-140X56X8K':
                        print("Haken heavy")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"adjustable": "verstellbar","heavy_versions": "schwere Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9525-2-140X56K':
                        print("Haken leicht, 3-fach verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"adjustable": "verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                    if lv_mid == '9521-2-150X60W':
                        print("Haken leicht, nicht verstellbar")
                        file_object = open('db.txt', 'a')   #Schreiben auf Liste
                        file_object.write(str(response_proc)+";"+ lv_mid+"\n")
                        file_object.close()
                        return {"sales_units":response_proc,"adjustable": "nicht verstellbar","heavy_versions": "leichte Ausfuehrung","article": "Dachhaken"}
                    #return{"sales_units":response_proc}
    


    def validate_w_mount_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """validate w_mount_id"""
        print("validate w_mount_id")
        entity = tracker.get_slot("w_mount_id")
        if entity == '9521-2-150X60W':
            return{"adjustable":"nicht verstellbar", "heavy_versions": "leichte Ausfuehrung", "w_mount_id": "9521-2-150X60W"}
        if entity == '9525-2-140X56K':
            return{"adjustable": "verstellbar", "heavy_versions": "leichte Ausfuehrung", "w_mount_id":"9525-2-140X56K"}
        if entity == '9525-2-140X56X8K':
            return{"adjustable": "verstellbar", "heavy_versions": "schwere Ausfuehrung", "w_mount_id":"9525-2-140X56X8K"}
        else:
            return{"adjustable":None, "w_mount_id":None}




class ValidateSimpleClampForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_clamp_form"

    def validate_clamp_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'clamp_type' value"""
        
        if type(tracker.get_slot("article")) is None:
            print("is None")
        else:
            if tracker.get_slot("article") == 'Klemme':
                print("Klemme already set, very good")
            else: 
                print(tracker.get_slot("article"))
        print("validate clamp_type")
        ALLOWED_MIDDLE_TYPES = {"mittelklemme", "mittelklemmen", "mittel", "die mittleren", "mitte", "mittelklemm","mittel-klemme", "mittel-klemmen"} #Todo
        ALLOWED_OTHER_DESIGNS = {"endklemme","endeklemme", "endklemmen", "endklemm", "end-klemme", "end-klemmen"}
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            f = [token.lemma_ for token in nlp(buffer)]
            print("type: List")
            print(f)
            if buffer.lower() in ALLOWED_MIDDLE_TYPES:
                print("Buffer ist mittelklemme")
                return {"clamp_type": "mittelklemme", "article": "klemme"}
            if buffer.lower() in ALLOWED_OTHER_DESIGNS:
                return {"clamp_type": "endklemme","article":"klemme"}
            else:
                dispatcher.utter_message(text=f"Sie uebergaben einen Klemmentyp, der nicht in unserem Sortiment ist")
                return {"clamp_type": None}
        else:
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            if slot_value.lower() in ALLOWED_MIDDLE_TYPES:
                print("slot_value ist mittelklemme")
                #SlotSet("article", "Mittelklemme")
                return {"clamp_type": "mittelklemme", "article": "klemme"}
            if slot_value.lower() in ALLOWED_OTHER_DESIGNS:
                return {"clamp_type": "endklemme","article":"klemme"}
            else:
                dispatcher.utter_message(text=f"Sie uebergaben einen Klemmentyp, der nicht in unserem Sortiment ist")
                return {"clamp_type": None}

    def validate_framed(            #NLP ineffective, tested lemma LOWERCASING only
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validation of framed"""
        lv_clamp_t = tracker.get_slot('clamp_type')
        print("validate framed: " + lv_clamp_t)
        ALLOWED_FRAMED_TYPES = {"wasiclip", "wasi", "wasi-clip", "glas", "glasmodule", "gerahmt", "rahmen"}
        if type(slot_value) == list:
            print("multiple frameds:")
            for elem in range(len(slot_value)):                
                f = [token.lemma_ for token in nlp(slot_value[elem])]
                print(slot_value[elem])
                print("f")
                print(f[0])
                if f[0].lower() in ALLOWED_FRAMED_TYPES:
                    print("it is in the set")
                    print(f[0].lower())
                    buffer = f[0].lower()               #buffer is a fitting value
                else:
                    print("NO")
                    print(f[0].lower())
            print("type: List")
            print(f[0])
            if buffer.lower() == 'glas' or buffer.lower() == 'glasmodule':
                if lv_clamp_t.lower() == 'endklemme':
                    return{"w_clamp_id":"9742-GM L80/6-9", "label":"Endklemmen fuer Glasmodule, Hoehen 6-9mm", "height":"6 mm", "rail_color": "weissaluminium"}
                if lv_clamp_t.lower() == 'mittelklemme':
                    return{"w_clamp_id":"9745-GM L80/6-9", "label":"Endklemmen fuer Glasmodule, Hoehen 6-9mm", "height":"6 mm", "rail_color": "weissaluminium"}    
            if buffer.lower() == 'gerahmt' or buffer.lower() == 'gerahmte' or buffer.lower() == 'gerahmtes':
                return {"framed":"gerahmt"}
            if buffer.lower() == 'wasiclip':
                return {"framed":"WASICLIP"}
            else:
                return {"framed": None}
        else:
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            if slot_value.lower() == 'glas' or slot_value.lower() == 'glasmodule':
                if lv_clamp_t == 'endklemme':
                    return{"w_clamp_id":"9742-GM L80/6-9", "label":"Endklemmen fuer Glasmodule, Hoehen 6-9mm", "height":"6 mm", "rail_color": "weissaluminium"}
                if lv_clamp_t == 'mittelklemme':
                    return{"w_clamp_id":"9745-GM L80/6-9", "label":"Endklemmen fuer Glasmodule, Hoehen 6-9mm", "height":"6 mm", "rail_color": "weissaluminium"}    
            if slot_value.lower() == 'gerahmt' or slot_value.lower() == 'gerahmte' or slot_value.lower() == 'gerahmtes':
                return {"framed":"gerahmt"}
            if slot_value.lower() == 'wasiclip':
                return {"framed":"WASICLIP"}
            else:
                return {"framed": None}
        

                
    def validate_rail_color(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'rail_color' value""" #schwarze Schienen gibt es nicht in Sonderausfuehrungen im Shop, daher setzt diese Methode auch weitere Slots sollte eine schwarze Farbe gewuenscht sein

        print("validate_rail_color")
        ALLOWED_WHITE_COLOR_TYPES = {"alufarben", "alufarbene", "alufarber", "metallen","metallene","metallenen","weissaluminium", "weiss", "hell", "helle","hellen", "weißaluminium", "weiß","weiße","weisse","metall","metallen"}
        ALLOWED_BLACK_COLOR_TYPES = {"schwarz", "black", "schwarze","schwarzes", "schwarzen", "dunkel", "dunkeln", "dunkler"}
        ALLOWED_FRAMED_TYPES = {"wasiclip", "wasi", "wasi-clip", "glas", "glasmodule", "gerahmt", "rahmen"}
        lv_framed = tracker.get_slot("framed")
        lv_clamp = tracker.get_slot("clamp_type")
        if type(lv_framed) == list:
            print("multiple frameds:")
            f = [token.lemma_ for token in nlp(lv_framed)]
            for elem in range(len(f)):                
                print(f[elem])
                if f[elem].lower() in ALLOWED_FRAMED_TYPES:
                    print("it is in the set")
                    print(f[elem].lower())
                    lv_framed = f[elem].lower()
        else: 
            print("one framed: ")
            print(lv_framed)

        if type(lv_clamp) == list:
            print("multiple elements")
            for elem in lv_clamp:
                print(elem)
        else: 
            print("ct: ")
            print(lv_clamp)
    
        lv_height = tracker.get_slot('height')
        if lv_height == None:
            dispatcher.utter_message("hoehe muss vor farbe spezifiziert sein")
            return{"rail_color": None}
        la_height = lv_height.split()
        lv_h = la_height[0]
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            f = [token.lemma_ for token in nlp(buffer)]
            print("type: List")
            print(f[0])       
            print("1: value of height number: " + str(lv_h))
            print(buffer)
            if f[0].lower() in ALLOWED_BLACK_COLOR_TYPES and lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'endklemme':              #gerahmt, EK, black
                if lv_h == '30' or '32' or '34' or '35' or '38' or '40' or '46' or '50':
                    return{"rail_color":"schwarz", "w_clamp_id":"9742-WASI4-"+str(lv_h)+"SE"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer gerahmte Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            if f[0].lower() in ALLOWED_BLACK_COLOR_TYPES:
                print("Allowed_BlackColors")
                if lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'mittelklemme':                                                       # gerahmt, MK, black
                    print("accepted, gerahmt, MittelKlemme, schwarz")
                    print(lv_h)
                    if lv_h == '36':
                        print("this should be working")
                        return{"rail_color":"schwarz", "w_clamp_id": "9745-WASI13SE"} 
                    else:
                        dispatcher.utter_message(text="ungueltige Farbkombination fuer gerahmte Module in schwarz und gerahmt")
                        return{"rail_color":None,"height": None}

            if f[0].lower() in ALLOWED_WHITE_COLOR_TYPES:
                if lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'mittelklemme':                                                       #gerahmt, MK, white
                    if lv_h == '36':
                        print("this should be working")
                        return{"rail_color":"weissaluminium", "w_clamp_id": "9745-WASI13"} 
                    else:
                        dispatcher.utter_message(text="ungueltige Farbkombination fuer gerahmte Module in weiss und gerahmt")
                        return{"rail_color":None,"height": None}
            if f[0].lower() not in ALLOWED_WHITE_COLOR_TYPES or ALLOWED_BLACK_COLOR_TYPES:
                dispatcher.utter_message(text=f"Beachten Sie die gueltigen Farbkombinationen 02")
                return{"rail_color": None}
            else:
                print("ERROR bei AND verknuepfung 1")    
            if f[0].lower() in ALLOWED_BLACK_COLOR_TYPES and lv_framed.lower() == 'wasiclip' and lv_clamp.lower() == 'endklemme':             #wasiclip, EK, black
                print("wasiclip, schwarz")
                if lv_h == '28' or lv_h =='29' or lv_h =='30' or lv_h =='31' or lv_h =='32' or lv_h =='33' or lv_h =='34':
                    return{"rail_color": "schwarz", "w_clamp_id": "9745-WASICLIPM1SE"}
                if lv_h == '35':
                    return{"rail_color": "schwarz", "w_clamp_id": "9745-WASICLIPM2SE"}
                if lv_h == '36' or lv_h =='37' or lv_h == '38' or lv_h =='39' or lv_h == '40' or lv_h == '41' or lv_h == '42' or lv_h == '43' or lv_h == '44':
                    return{"rail_color": "schwarz", "w_clamp_id": "9745-WASICLIPM3SE"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer WASICLIP Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            if f[0].lower() in ALLOWED_WHITE_COLOR_TYPES and lv_framed.lower() == 'wasiclip' and lv_clamp.lower() == 'endklemme':             #wasiclip, EK, white
                print("wasiclip, schwarz")
                if lv_h == '28' or lv_h =='29' or lv_h =='30' or lv_h =='31' or lv_h =='32' or lv_h =='33' or lv_h =='34':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9745-WASICLIPM1"}
                if lv_h == '35':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9745-WASICLIPM2"}
                if lv_h == '36' or lv_h =='37' or lv_h == '38' or lv_h =='39' or lv_h == '40' or lv_h == '41' or lv_h == '42' or lv_h == '43' or lv_h == '44':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9745-WASICLIPM3"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer WASICLIP Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
        else:
            print("2: value of height number: " + str(lv_h))
            print(type(lv_h))
            print(lv_h)
            print(lv_clamp)
            print(lv_framed) 
            f = [token.lemma_ for token in nlp(slot_value)]
            print("slot_value")
            print(f)
            print(f[0].lower())
            if umlaut(f[0].lower()) in ALLOWED_BLACK_COLOR_TYPES and lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'endklemme':          #gerahmt, EK, black
                if lv_h == '30' or lv_h == '32' or lv_h == '34' or lv_h == '35' or lv_h == '38' or lv_h == '40' or lv_h == '46' or lv_h == '50':
                    return{"rail_color":"schwarz", "w_clamp_id":"9742-WASI4-"+str(lv_h)+"SE"}        #9742-WASI4-"+str(lv_h)+"
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer gerahmte Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            
            if umlaut(f[0].lower()) in ALLOWED_WHITE_COLOR_TYPES:
                print("Allowed White Colors EK" + lv_framed + lv_clamp)
                if lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'endklemme':                                                              # gerahmt, EK, white
                    print("hier_auch")
                    if lv_h == '30' or lv_h == '32' or lv_h == '34' or lv_h == '35' or lv_h == '38' or lv_h == '40' or lv_h == '42' or lv_h == '43' or lv_h == '50':
                        return{"rail_color":"weissaluminium", "w_clamp_id": "9742-WASI4-" + str(lv_h) + ""}

            if umlaut(f[0].lower()) in ALLOWED_BLACK_COLOR_TYPES:                                                                                 # gerahmt, MK, black
                print("Allowed_BlackColors")
                if lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'mittelklemme':
                    print("accepted, gerahmt, MittelKlemme, schwarz")
                    print(lv_h)
                    if lv_h == '36':
                        print("this should be working")
                        return{"rail_color":"schwarz", "w_clamp_id": "9745-WASI13SE"} 
                    else:
                        dispatcher.utter_message(text="ungueltige Farbkombination fuer gerahmte Module in schwarz und gerahmt")
                        return{"rail_color":None,"height": None}
            if umlaut(f[0].lower()) in ALLOWED_WHITE_COLOR_TYPES:
                print("Allowed_WhiteColors mk")
                if lv_framed.lower() == 'gerahmt' and lv_clamp.lower() == 'mittelklemme':                                                         # gerahmt, MK, white
                    print("accepted, gerahmt, MittelKlemme")
                    print(lv_h)
                    if lv_h == '36':
                        print("this should be working")
                        return{"rail_color":"weissaluminium", "w_clamp_id": "9745-WASI13"} 
                    else:
                        dispatcher.utter_message(text="ungueltige Farbkombination fuer gerahmte Module in weiss und gerahmt")
                        return{"rail_color":None,"height": None}
            
            print(f[0].lower())
            if f[0].lower() in ALLOWED_BLACK_COLOR_TYPES and lv_framed.lower() == 'wasiclip' and lv_clamp.lower() == 'endklemme':                 # wasiclip, EK, black
                print("wasiclip, schwarz, endklemme")
                if lv_h == '28' or lv_h =='29' or lv_h =='30' or lv_h =='31' or lv_h =='32' or lv_h =='33' or lv_h =='34':
                    print("yep")
                    print(lv_h)
                    return{"rail_color": "schwarz", "w_clamp_id": "9742-WASICLIPE32SE"}
                if lv_h == '35':
                    return{"rail_color": "schwarz", "w_clamp_id": "9742-WASICLIPE35SE"}
                if lv_h == '36' or lv_h =='37' or lv_h == '38' or lv_h =='39':
                    return{"rail_color": "schwarz", "w_clamp_id": "9742-WASICLIPE38SE"}
                if lv_h == '40' or lv_h == '41' or lv_h == '42' or lv_h == '43' or lv_h == '44' or lv_h == '45':                
                    return{"rail_color": "schwarz", "w_clamp_id": "9742-WASICLIPE40SE"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer WASICLIP Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            if umlaut(f[0].lower()) in ALLOWED_WHITE_COLOR_TYPES and lv_framed.lower() == 'wasiclip' and lv_clamp.lower() == 'endklemme':             #wasiclip, EK, white
                print("wasiclip, weiss, endklemme")
                if lv_h == '28' or lv_h =='29' or lv_h =='30' or lv_h =='31' or lv_h =='32' or lv_h =='33' or lv_h =='34':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9742-WASICLIPE32"}
                if lv_h == '35':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9742-WASICLIPE35"}
                if lv_h == '36' or lv_h =='37' or lv_h == '38' or lv_h =='39':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9742-WASICLIPE38"}
                if  lv_h == '40' or lv_h == '41' or lv_h == '42' or lv_h == '43' or lv_h == '44' or lv_h == '45':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9742-WASICLIPE40"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer WASICLIP Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            if umlaut(f[0].lower()) in ALLOWED_BLACK_COLOR_TYPES and lv_framed.lower() == 'wasiclip' and lv_clamp.lower() == 'mittelklemme':           #wasiclip, MK, black
                print("wasiclip, schwarz, mittel")
                if lv_h == '28' or lv_h =='29' or lv_h =='30' or lv_h =='31' or lv_h =='32' or lv_h =='33' or lv_h =='34':
                    return{"rail_color": "schwarz", "w_clamp_id": "9745-WASICLIPM1SE"}
                if lv_h == '35':
                    return{"rail_color": "schwarz", "w_clamp_id": "9745-WASICLIPM2SE"}
                if lv_h == '36' or lv_h =='37' or lv_h == '38' or lv_h =='39' or lv_h == '40' or lv_h == '41' or lv_h == '42' or lv_h == '43' or lv_h == '44':
                    return{"rail_color": "schwarz", "w_clamp_id": "9745-WASICLIPM3SE"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer WASICLIP Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            if umlaut(f[0].lower()) in ALLOWED_WHITE_COLOR_TYPES and lv_framed.lower() == 'wasiclip' and lv_clamp.lower() == 'mittelklemme':          #wasiclip, MK, white
                print("wasiclip, weiss, mittel")
                if lv_h == '28' or lv_h =='29' or lv_h =='30' or lv_h =='31' or lv_h =='32' or lv_h =='33' or lv_h =='34':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9745-WASICLIPM1"}
                if lv_h == '35':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9745-WASICLIPM2"}
                if lv_h == '36' or lv_h =='37' or lv_h == '38' or lv_h =='39' or lv_h == '40' or lv_h == '41' or lv_h == '42' or lv_h == '43' or lv_h == '44':
                    return{"rail_color": "weissaluminium", "w_clamp_id": "9745-WASICLIPM3"}
                else:
                    dispatcher.utter_message(text="ungueltige Farbkombination fuer WASICLIP Module in schwarz und gerahmt")
                    return{"rail_color":None,"height": None}
            else:
                if umlaut(f[0].lower()) not in ALLOWED_WHITE_COLOR_TYPES or ALLOWED_BLACK_COLOR_TYPES:
                    print(umlaut(f[0].lower()))
                    dispatcher.utter_message(text=f"Beachten Sie die gueltigen Farbkombinationen 02-2")
                    return{"rail_color": None}   
        

    def validate_height(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'height' value"""

        print("validate_height, check first word if its not numeric use sales_units logic")
        print(slot_value)
        spellcheck = SpellChecker(language='de')
        yo = slot_value.split() #always 2 values e. g.: 32 mm
        slot_value = yo[0]
        millimeter = " mm"
        print(slot_value + " after preprocessing...")
        ALLOWED_FRAMED_TYPES = {"wasiclip", "wasi", "wasi-clip", "glas", "glasmodule","gerahmt", "rahmen"}
        lv_framed = tracker.get_slot("framed")
        lv_clamp = tracker.get_slot("clamp_type")
        if type(lv_framed) == list:
            print("multiple frameds:")
            f = [token.lemma_ for token in nlp(lv_framed)]
            for elem in range(len(f)):                
                print(f[elem])
                if f[elem].lower() in ALLOWED_FRAMED_TYPES:
                    print("it is in the set")
                    print(f[elem].lower())
                    lv_framed = f[elem].lower()
        else: 
            print("one framed: ")
            print(lv_framed)
        print("ct: " + lv_clamp)
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            if buffer.isnumeric():
                if lv_clamp.lower() == 'endklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if buffer == '30':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '32':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '34':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '35':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '38':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '40':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '42':
                            return {"height":str(buffer)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-42"}
                        if buffer == '43':
                            return {"height":str(buffer)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-43"}
                        if buffer == '46':
                            return {"height":str(buffer)+millimeter,"rail_color":"schwarz","w_clamp_id":"9742-WASI4-46SE"}
                        if buffer == '50':
                            return {"height":str(buffer)+millimeter}
                    if lv_framed.lower() == 'wasiclip':
                        if buffer == '32':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '35':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '38':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '40':
                            return {"height":str(buffer)+millimeter}
                if lv_clamp.lower() == 'mittelklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if buffer == '36':
                            return {"height":str(buffer)+millimeter}
                        else:
                            dispatcher.utter_message(text="Die Kombination der Hoehe und 'gerahmt' passen nicht zusammen. Sehen Sie im Sortiment nach.")
                            return {"height":None}
                    if lv_framed.lower() == 'wasiclip':
                        if buffer == '28' or buffer =='29' or buffer =='30' or buffer =='31' or buffer =='32' or buffer =='33' or buffer =='34':
                            return {"height":str("28")+millimeter}
                        if buffer == '35':
                            return {"height":str(buffer)+millimeter}
                        if buffer == '36' or buffer =='37' or buffer =='38' or buffer =='39' or buffer =='40' or buffer =='41' or buffer =='42' or buffer =='43' or buffer =='44':
                            return {"height":str("36")+millimeter}
                        else: 
                            dispatcher.utter_message(text="Die Kombination von Hoehe und WASICLIP ist ungueltig, derartige Schienen haben wir nicht")
                            return{"height":None}
            else:
                print("vor Spellcheck: " + buffer)
                helperuno = spellcheck.correction(slot_value)
                print("nach Spellcheck: " + helperuno)
                response_proc = w2n.convert(helperuno)
                if lv_clamp.lower() == 'endklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if response_proc == '30':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '32':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '34':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '35':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '38':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '40':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '42':
                            return {"height":str(response_proc)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-42"}
                        if response_proc == '43':
                            return {"height":str(response_proc)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-43"}
                        if response_proc == '46':
                            return {"height":str(response_proc)+millimeter,"rail_color":"schwarz","w_clamp_id":"9742-WASI4-46SE"}
                        if response_proc == '50':
                            return {"height":str(response_proc)+millimeter}
                    if lv_framed.lower() == 'wasiclip':
                        if response_proc == '32':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '35':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '38':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '40':
                            return {"height":str(response_proc)+millimeter}
                if lv_clamp.lower() == 'mittelklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if response_proc == '36':
                            return {"height":str(response_proc)+millimeter}
                        else:
                            dispatcher.utter_message(text="Die Kombination der Hoehe und 'gerahmt' passen nicht zusammen. Sehen Sie im Sortiment nach.")
                            return {"height":None}
                    if lv_framed.lower() == 'wasiclip':
                        if response_proc == '28' or response_proc == '29' or response_proc == '30' or response_proc == '31' or response_proc == '32' or response_proc == '33' or response_proc == '34':
                            return {"height":str("28")+millimeter}
                        if response_proc == '35':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '36' or response_proc == '37' or response_proc == '38' or response_proc == '39' or response_proc == '40' or response_proc == '41' or response_proc == '42' or response_proc == '43' or response_proc == '44':
                            return {"height":str("36")+millimeter}
                        else: 
                            dispatcher.utter_message(text="Die Kombination von Hoehe und WASICLIP ist ungueltig, derartige Schienen haben wir nicht")
                            return{"height":None}
                    return{"height":str(response_proc)+millimeter}
        else:
            if slot_value.isnumeric():
                if lv_clamp.lower() == 'endklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if slot_value == '30':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '32':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '34':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '35':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '38':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '40':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '42':
                            return {"height":str(slot_value)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-42"}
                        if slot_value == '43':
                            return {"height":str(slot_value)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-43"}
                        if slot_value == '46':
                            return {"height":str(slot_value)+millimeter,"rail_color":"schwarz","w_clamp_id":"9742-WASI4-46SE"}
                        if slot_value == '50':
                            return {"height":str(slot_value)+millimeter}
                    if lv_framed.lower() == 'wasiclip':
                        if slot_value == '32':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '35':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '38':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '40':
                            return {"height":str(slot_value)+millimeter}
                if lv_clamp.lower() == 'mittelklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if slot_value == '36':
                            return {"height":str(slot_value)+millimeter}
                        else:
                            dispatcher.utter_message(text="Die Kombination der Hoehe und 'gerahmt' passen nicht zusammen. Sehen Sie im Sortiment nach.")
                            return {"height":None}
                    if lv_framed.lower() == 'wasiclip':
                        if slot_value == '28' or slot_value == '29' or slot_value == '30' or slot_value == '31' or slot_value == '32' or slot_value == '33' or slot_value == '34':
                            return {"height":str("28")+millimeter}
                        if slot_value == '35':
                            return {"height":str(slot_value)+millimeter}
                        if slot_value == '36' or slot_value == '37' or slot_value == '38' or slot_value == '39' or slot_value == '40' or slot_value == '41' or slot_value == '42' or slot_value == '43' or slot_value == '44':
                            return {"height":str("36")+millimeter}
                        else: 
                            dispatcher.utter_message(text="Die Kombination von Hoehe und WASICLIP ist ungueltig, derartige Schienen haben wir nicht")
                            return{"height":None}
                #return{"height":str(slot_value)+millimeter}
            else:
                print("vor Spellcheck" + slot_value)
                helperone = spellcheck.correction(slot_value)
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                if lv_clamp.lower() == 'endklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if response_proc == '30':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '32':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '34':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '35':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '38':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '40':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '42':
                            return {"height":str(response_proc)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-42"}
                        if response_proc == '43':
                            return {"height":str(response_proc)+millimeter,"rail_color":"weissaluminium", "w_clamp_id":"9742-WASI4-43"}
                        if response_proc == '46':
                            return {"height":str(response_proc)+millimeter,"rail_color":"schwarz","w_clamp_id":"9742-WASI4-46SE"}
                        if response_proc == '50':
                            return {"height":str(response_proc)+millimeter}
                    if lv_framed.lower() == 'wasiclip':
                        if response_proc == '32':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '35':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '38':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '40':
                            return {"height":str(response_proc)+millimeter}
                if lv_clamp.lower() == 'mittelklemme':
                    if lv_framed.lower() == 'gerahmt':
                        if response_proc == '36':
                            return {"height":str(response_proc)+millimeter}
                        else:
                            dispatcher.utter_message(text="Die Kombination der Hoehe und 'gerahmt' passen nicht zusammen. Sehen Sie im Sortiment nach.")
                            return {"height":None}
                    if lv_framed.lower() == 'wasiclip':
                        if response_proc == '28' or response_proc == '29' or response_proc == '30' or response_proc == '31' or response_proc == '32' or response_proc == '33' or response_proc == '34':
                            return {"height":str("28")+millimeter}
                        if response_proc == '35':
                            return {"height":str(response_proc)+millimeter}
                        if response_proc == '36' or response_proc == '37' or response_proc == '38' or response_proc == '39' or response_proc == '40' or response_proc == '41' or response_proc == '42' or response_proc == '43' or response_proc == '44':
                            return {"height":str("36")+millimeter}
                        else: 
                            dispatcher.utter_message(text="Die Kombination von Hoehe und WASICLIP ist ungueltig, derartige Schienen haben wir nicht")
                            return{"height":None}
                    return{"height":str(response_proc)+millimeter}
                #return{"height":str(response_proc)+millimeter}
        
        
        # ALLOWED_SPECIAL_FEATURES = {"seitliche nutung", "seitlicher nutung","seitliche","seitlicher"}
        # if type(slot_value) == list:
        #     buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
        #     buffertwo = ""
        #     for item in slot_value:
        #         buffertwo = buffertwo + item
        #     print(buffertwo)
        #     if buffer.lower() in {"ultraleicht", "ultra leicht", "ultra-leicht", "ultraleichte", "ultraleichter", "ultraleichten"}:
        #         return{"rail_bfeature": "ultraleicht", "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen"}
        #     if buffer.lower() in ALLOWED_SPECIAL_FEATURES:
        #         return{"rail_bfeature": buffer, "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen"}
        #     if buffer.lower() in {"trapezdach", "trapez", "trapezmontageschiene", "trapezmontageschienen", "trapezdachmontage"}:
        #         return{"rail_bfeature":"trapezdach", "rail_color":"weissaluminium", "rail_adesign":"40er Montageschienen"}
        #     if buffer.lower() in {"keine", "standard","standardmontage","normal"}:
        #         return{"rail_bfeature": "standard", "rail_color":"weissaluminium","rail_adesign":"40er Montageschienen"}
        #     if buffer.lower() in {"breites profil", "breite profil", "breite ausfuehrung","breit","breite"}:
        #         return{"rail_bfeature": "breites profil", "rail_color":"weissaluminium","rail_adesign":"80er Montageschienen"}
        #     dispatcher.utter_message(text="Ihre Sonderausfuehrung wurde vom Chatbot nicht verstanden, ist jedoch im System vermerkt und ein Mitarbeiter wird sich in Kuerze bei Ihnen melden")
        #     return{"rail_bfeature": buffer}
        # else:
        #     if slot_value.lower() in {"ultraleicht", "ultra leicht", "ultra-leicht", "ultraleichte", "ultraleichter", "ultraleichten"}:
        #         return{"rail_bfeature": "ultraleicht", "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen"}
        #     if slot_value.lower() in ALLOWED_SPECIAL_FEATURES:
        #         return{"rail_bfeature": slot_value, "rail_color": "weissaluminium", "rail_adesign":"40er Montageschienen"}
        #     if slot_value.lower() in {"trapezdach", "trapez", "trapezmontageschiene", "trapezmontageschienen", "trapezdachmontage"}:
        #         return{"rail_bfeature":"trapezdach", "rail_color":"weissaluminium", "rail_adesign":"40er Montageschienen"}
        #     if slot_value.lower() in {"keine", "standard","standardmontage","normal"}:
        #         return{"rail_bfeature": "standard", "rail_color":"weissaluminium","rail_adesign":"40er Montageschienen"}
        #     if slot_value.lower() in {"breites profil", "breite profil", "breite ausfuehrung","breit","breite"}:
        #         return{"rail_bfeature": "breites profil", "rail_color":"weissaluminium","rail_adesign":"80er Montageschienen"}
        #     dispatcher.utter_message(text="Ihre Sonderausfuehrung wurde vom Chatbot nicht verstanden, ist jedoch im System vermerkt und ein Mitarbeiter wird sich in Kuerze bei Ihnen melden")
        #     return{"rail_bfeature": slot_value}

    def validate_sales_units(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """Validation of numeric attribute 'sales_units' value, if its a written number in german text this method will turn it into an integer """

        print("validate_clamp_sales_unit")
        spellcheck = SpellChecker(language='de')
        c_id = tracker.get_slot("w_clamp_id")
        print(type(c_id))
        print(c_id)
        if not c_id:
            print("No Sales_Units before c_id is not known [CLAMP]")
            print("value for entity clamp_id is not set")
            if type(slot_value) == list:
                buffer = slot_value[0]      #temporary fix, if 2 values delivered
                if buffer.isnumeric():
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Klemme")
                    return{"sales_units":None}
                else:
                    print("vor Spellcheck" + buffer)
                    helperone = spellcheck.correction(buffer)
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Klemme")
                    return{"sales_units":None}
            else:
                if slot_value.isnumeric():
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Klemme")
                    return{"sales_units":None}
                else:
                    print("vor Spellcheck" + slot_value)
                    helperone = spellcheck.correction(slot_value)
                    print("nach Spellcheck:" + helperone)
                    #response_proc = w2n.convert(helperone)
                    print("Todo")
                    dispatcher.utter_message("Spezifizieren Sie den Artikel eindeutig bevor sie die Verkaufsmenge bestimmen, es fehlen noch Eckdaten zur Klemme")
                    return{"sales_units":None}
        else:
            print("clamp_id is set")
            if type(slot_value) == list:
                buffer = slot_value[0]      #temporary fix, if 2 values delivered
                if buffer.isnumeric():
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(buffer)+";"+ c_id+"\n")
                    file_object.close()
                    return{"sales_units":buffer}
                else:
                    print("vor Spellcheck" + buffer)
                    helperone = spellcheck.correction(buffer.replace(".",""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(response_proc)+";"+ c_id+"\n")
                    file_object.close()
                    return{"sales_units":response_proc}
            else:
                if slot_value.isnumeric():
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(slot_value)+";"+ c_id+"\n")
                    file_object.close()
                    return{"sales_units":slot_value}
                else:
                    print("vor Spellcheck" + slot_value)
                    helperone = spellcheck.correction(slot_value.replace(".",""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(response_proc)+";"+ c_id+"\n")
                    file_object.close()
                    return{"sales_units":response_proc}


class ValidateSimpleHangerScrewForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_hanger_screw_form"

    def validate_alength(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'alength' value"""

        print("validate_alength hanger_screw, check first word if its not numeric use sales_units logic")
        if slot_value is None:
            lv_h = tracker.get_slot('height')
            if lv_h is None:
                dispatcher.utter_message(text='Es wurden keine Laengen oder Hoehenmase erkannt')
            else: 
                slot_value = lv_h # Falsche Entitätenerkennung/ -zuweisung fix
        spellcheck = SpellChecker(language='de')
        yo = slot_value.split() #always 2 values e. g.: 32 mm
        slot_value = yo[0]
        millimeter = " mm"
        print(slot_value + " after preprocessing...")
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary working, facing bug where entities are delivered twice as often in a list instead of a string argument 
            if buffer.isnumeric():
                if buffer == '200':
                    return {"alength": str(buffer)+ millimeter}
                if buffer == '250':
                    return {"alength": str(buffer)+ millimeter}
                if buffer == '20':
                    return {"alength": '200' + millimeter}
                if buffer == '25':
                    return {"alength": '250' + millimeter}
                else:
                    dispatcher.utter_message(text='Ungueltiges Laengenmas für Stockschrauben01')
            else:
                print("vor Spellcheck: " + buffer)
                helperuno = spellcheck.correction(slot_value)
                print("nach Spellcheck: " + helperuno)
                response_proc = w2n.convert(helperuno)
                if response_proc == '200':
                    return {"alength": str(response_proc)+ millimeter}
                if response_proc == '250':
                    return {"alength": str(response_proc)+ millimeter}
                if response_proc == '20':
                    return {"alength": '200' + millimeter}
                if response_proc == '25':
                    return {"alength": '250' + millimeter}
                else:
                    dispatcher.utter_message(text='Ungueltiges Laengenmas für Stockschrauben02')    
        else:
            if slot_value.isnumeric():
                if slot_value == '200':
                    return {"alength": str(slot_value)+ millimeter}
                if slot_value == '250':
                    return {"alength": str(slot_value)+ millimeter}
                if slot_value == '20':
                    return {"alength": '200' + millimeter}
                if slot_value == '25':
                    return {"alength": '250' + millimeter}
                else:
                    dispatcher.utter_message(text='Ungueltiges Laengenmas für Stockschrauben03')
            else:
                print("vor Spellcheck" + slot_value)
                helperone = spellcheck.correction(slot_value)
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                if response_proc == '200':
                    return {"alength": str(response_proc)+ millimeter}
                if response_proc == '250':
                    return {"alength": str(response_proc)+ millimeter}
                if response_proc == '20':
                    return {"alength": '200' + millimeter}
                if response_proc == '25':
                    return {"alength": '250' + millimeter}
                else:
                    dispatcher.utter_message(text='Ungueltiges Laengenmas für Stockschrauben04')
        print("if no match at all alength")
        dispatcher.utter_message("Stockschrauben sind in den Laengen 200 mm und 250 mm verfügbar, andere Laengen sind noch nicht im Sortiment05")
        return{"alength": None}
        


    def validate_build_permit(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """validate build_permit"""
        
        print("validate build_permit")
        lv_alength = tracker.get_slot('alength')
        intent = tracker.get_intent_of_latest_message()
        if intent == "affirm":
            print("true, check alength now")
            yo = lv_alength.split() #always 2 values e. g.: 32 mm
            lv_l_num = yo[0]
            if lv_l_num == '200':
                return {"build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ"}
            if lv_l_num == '250':
                return {"build_permit": "ja", "w_mount_id": "9216-2-10X250-BZ"}
        if intent == 'deny':
            print("false, check alength now")
            yo = lv_alength.split() #always 2 values e. g.: 32 mm
            lv_l_num = yo[0]
            if lv_l_num == '200':
                return {"build_permit": "nein", "w_mount_id": "9216-2-10X200"}
            if lv_l_num == '250':
                return {"build_permit": "nein", "w_mount_id": "9216-2-10X250"}
        if intent == 'give_give_mount_id':
            lv_mid = tracker.get_slot('w_mount_id')
            return {"build_permit": "id given", "w_mount_id": lv_mid}
        print("no match at all build_permit")
        return {"bulid_permit":None}

    
                
    def validate_sales_units(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """Validation of numeric attribute 'sales_units' value, if its a written number in german text this method will turn it into an integer """

        print("validate_hanger_screw_sales_unit")
        spellcheck = SpellChecker(language='de')
        m_id = tracker.get_slot("w_mount_id")                        
        if not m_id:
            print("No Sales_Units before m_id is not known [HANGER_SCREW]")
            print("value for entity mount_id is not set")
            laenge = tracker.get_slot("alength")
            bauzulassung = tracker.get_slot("build_permit")
            yo = laenge.split() #mm
            lv_laenge = yo[0]
            if lv_laenge == '200':
                if bauzulassung == 'ja':
                    if type(slot_value) == list:
                        buffer = slot_value[0]      #temporary fix, if 2 values delivered
                        if buffer.isnumeric():
                            return{"alength": "200 mm","build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ","sales_units":buffer}
                        else:
                            print("vor Spellcheck" + buffer)
                            helperone = spellcheck.correction(buffer.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "200 mm","build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ","sales_units":response_proc}
                    else:
                        if slot_value.isnumeric():
                            return{"alength": "200 mm","build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ","sales_units":slot_value}
                        else:
                            print("vor Spellcheck" + slot_value)
                            helperone = spellcheck.correction(slot_value.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "200 mm","build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ","sales_units":response_proc}
                if bauzulassung == 'nein':
                    if type(slot_value) == list:
                        buffer = slot_value[0]      #temporary fix, if 2 values delivered
                        if buffer.isnumeric():
                            return{"alength": "200 mm","build_permit": "nein", "w_mount_id": "9216-2-10X200","sales_units":buffer}
                        else:
                            print("vor Spellcheck" + buffer)
                            helperone = spellcheck.correction(buffer.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "200 mm","build_permit": "nein", "w_mount_id": "9216-2-10X200","sales_units":response_proc}
                    else:
                        if slot_value.isnumeric():
                            return{"alength": "200 mm","build_permit": "nein", "w_mount_id": "9216-2-10X200","sales_units":slot_value}
                        else:
                            print("vor Spellcheck" + slot_value)
                            helperone = spellcheck.correction(slot_value.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "200 mm","build_permit": "nein", "w_mount_id": "9216-2-10X200","sales_units":response_proc}
            if lv_laenge == '250':
                if bauzulassung == 'ja':
                    if type(slot_value) == list:
                        buffer = slot_value[0]      #temporary fix, if 2 values delivered
                        if buffer.isnumeric():
                            return{"alength": "250 mm","build_permit": "ja", "w_mount_id": "9216-2-10X250-BZ","sales_units":buffer}
                        else:
                            print("vor Spellcheck" + buffer)
                            helperone = spellcheck.correction(buffer.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "250 mm","build_permit": "ja", "w_mount_id": "9216-2-10X250-BZ","sales_units":response_proc}
                    else:
                        if slot_value.isnumeric():
                            return{"alength": "250 mm","build_permit": "ja", "w_mount_id": "9216-2-10X250-BZ","sales_units":slot_value}
                        else:
                            print("vor Spellcheck" + slot_value)
                            helperone = spellcheck.correction(slot_value.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "250 mm","build_permit": "ja", "w_mount_id": "9216-2-10X250-BZ","sales_units":response_proc}
                if bauzulassung == 'nein':
                    if type(slot_value) == list:
                        buffer = slot_value[0]      #temporary fix, if 2 values delivered
                        if buffer.isnumeric():
                            return{"alength": "250 mm","build_permit": "nein", "w_mount_id": "9216-2-10X250","sales_units":buffer}
                        else:
                            print("vor Spellcheck" + buffer)
                            helperone = spellcheck.correction(buffer.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "250 mm","build_permit": "nein", "w_mount_id": "9216-2-10X250","sales_units":response_proc}
                    else:
                        if slot_value.isnumeric():
                            return{"alength": "250 mm","build_permit": "nein", "w_mount_id": "9216-2-10X250","sales_units":slot_value}
                        else:
                            print("vor Spellcheck" + slot_value)
                            helperone = spellcheck.correction(slot_value.replace(".",""))
                            print("nach Spellcheck:" + helperone)
                            response_proc = w2n.convert(helperone)
                            return{"alength": "250 mm","build_permit": "nein", "w_mount_id": "9216-2-10X250","sales_units":response_proc}
            else:
                return{"alength":None, "sales_units": None}
        else:
            print("mount_id is set")
            if type(slot_value) == list:
                buffer = slot_value[0]      #temporary fix, if 2 values delivered
                if buffer.isnumeric():
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(buffer)+";"+ m_id+"\n")
                    file_object.close()
                    return{"sales_units":buffer}
                else:
                    print("vor Spellcheck" + buffer)
                    helperone = spellcheck.correction(buffer.replace(".",""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(response_proc)+";"+ m_id+"\n")
                    file_object.close()
                    return{"sales_units":response_proc}
            else:
                if slot_value.isnumeric():
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(slot_value)+";"+ m_id+"\n")
                    file_object.close()
                    return{"sales_units":slot_value}
                else:
                    print("vor Spellcheck" + slot_value)
                    helperone = spellcheck.correction(slot_value.replace(".",""))
                    print("nach Spellcheck:" + helperone)
                    response_proc = w2n.convert(helperone)
                    file_object = open('db.txt', 'a')   #Schreiben auf Liste
                    file_object.write(str(response_proc)+";"+ m_id+"\n")
                    file_object.close()
                    return{"sales_units":response_proc}
    def validate_w_mount_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """validate w_mount_id"""
        print("validate w_mount_id")
        entity = tracker.get_slot("w_mount_id")
        if entity == '9216-2-10X200':
            return {"alength": "200 mm","build_permit": "nein", "w_mount_id": "9216-2-10X200"}
        if entity == '9216-2-10X250':
            return {"alength": "250 mm","build_permit": "nein", "w_mount_id": "9216-2-10X250"}
        if entity == '9216-2-10X200-BZ':
            return {"alength": "200 mm","build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ"}
        if entity == '9216-2-10X250-BZ':
            return {"alength": "250 mm","build_permit": "ja", "w_mount_id": "9216-2-10X200-BZ"}
        else:
            dispatcher.utter_message("ungueltige mount_id (Stockschraube):")
            print(entity)
            return {"w_mount_id": None}



class ValidateSimplePlateForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_plate_form"

    def validate_ascrew_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """ validate ascrew_type"""

        print("validate ascrew_type, plate")
        if type(slot_value) == list:
            buffer = slot_value[0]
            if buffer.lower() == 'm10' or buffer.lower() == 'm-zehn':
                return{"ascrew_type": "M10", "w_mount_id": "9543-2-82X30X5"}
            if buffer.lower() == 'm12' or buffer.lower() == 'm-zwölf':
                return{"ascrew_type": "M12", "w_mount_id": "9544-2-82X30X5"}
            else:
                dispatcher.utter_message("Adapterbleche sind nur für M12 oder M10 Schrauben verfügbar")
                return{"ascrew_type": None}
        else:
            if slot_value.lower() == 'm10' or slot_value.lower() == 'm-zehn':
                return{"ascrew_type": "M10", "w_mount_id": "9543-2-82X30X5"}
            if slot_value.lower() == 'm12' or slot_value.lower() == 'm-zwölf':
                return{"ascrew_type": "M12", "w_mount_id": "9544-2-82X30X5"}
            else:
                dispatcher.utter_message("Adapterbleche sind nur für M12 oder M10 Schrauben verfügbar")
                return{"ascrew_type": None}

    def validate_sales_units(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate sales_units plate"""

        print("sales_units plate")
        spellcheck = SpellChecker(language='de')
        print("mount_id is set")
        m_id = tracker.get_slot("w_mount_id")
        if m_id is None:
            print("M_ID is none")
            return{"ascrew_type":None,"sales_units": None}
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary fix, if 2 values delivered
            if buffer.isnumeric():
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(buffer)+";"+ m_id+"\n")
                file_object.close()
                return{"sales_units":buffer}
            else:
                print("vor Spellcheck" + buffer)
                helperone = spellcheck.correction(buffer.replace(".",""))
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(response_proc)+";"+ m_id+"\n")
                file_object.close()
                return{"sales_units":response_proc}
        else:
            if slot_value.isnumeric():
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(slot_value)+";"+ m_id+"\n")
                file_object.close()
                return{"sales_units":slot_value}
            else:
                print("vor Spellcheck" + slot_value)
                helperone = spellcheck.correction(slot_value.replace(".",""))
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(response_proc)+";"+ m_id+"\n")
                file_object.close()
                return{"sales_units":response_proc}

    def validate_w_mount_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict
    ) -> Dict[Text, Any]:
        """validate w_mount_id"""
        print("validate w_mount_id, plate")
        entity = tracker.get_slot("w_mount_id")
        if entity.lower() == 'm10':
            return{"ascrew_type": "M10", "w_mount_id": "9543-2-82X30X5"}
        if entity.lower() == 'm12':
            return{"ascrew_type": "M12", "w_mount_id": "9544-2-82X30X5"}
        print("no match at all for w_mount_id plate form")
        return {"ascrew_type": None,"w_mount_id": None}


class ValidateSimpleBauVorhabenForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_bauvorhaben_form"

    def validate_abv(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'abv' value"""

        
        open('bauvorhaben.txt', 'w').close()
        tlm = tracker.latest_message['text']
        print(tlm)
        file_object = open('bauvorhaben.txt', 'a')   #Schreiben auf Liste
        file_object.write(tlm+"\n")
        file_object.close()
        return{"abv": tlm}

    def validate_bstreet(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'bstreet' value"""
        
        tlm = tracker.latest_message['text']
        print(tlm)
        file_object = open('bauvorhaben.txt', 'a')   #Schreiben auf Liste
        file_object.write(tlm+"\n")
        file_object.close()
        return{"bstreet": tlm}


    def validate_cplz(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'cplz' value"""

        tlm = tracker.latest_message['text']
        print(tlm)
        file_object = open('bauvorhaben.txt', 'a')   #Schreiben auf Liste
        file_object.write(tlm+"\n")
        file_object.close()
        return{"cplz": tlm}


    def validate_dcity(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'dcity' value"""

        tlm = tracker.latest_message['text']
        print(tlm)
        file_object = open('bauvorhaben.txt', 'a')   #Schreiben auf Liste
        file_object.write(tlm+"\n")
        file_object.close()
        return{"dcity": tlm}

class ValidateSimplePVForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_pv_form"

    def validate_sales_units(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validation of 'sales_units' value"""
        print("sales_units PV")
        spellcheck = SpellChecker(language='de')
        if type(slot_value) == list:
            buffer = slot_value[0]      #temporary fix, if 2 values delivered
            if buffer.isnumeric():
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(buffer)+";PV-Modul"+"\n")
                file_object.close()
                return{"sales_units":buffer}
            else:
                print("vor Spellcheck" + buffer)
                helperone = spellcheck.correction(buffer.replace(".",""))
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(response_proc)+";PV-Modul"+"\n")
                file_object.close()
                return{"sales_units":response_proc}
        else:
            if slot_value.isnumeric():
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(slot_value)+";PV-Modul"+"\n")
                file_object.close()
                return{"sales_units":slot_value}
            else:
                print("vor Spellcheck" + slot_value)
                helperone = spellcheck.correction(slot_value.replace(".",""))
                print("nach Spellcheck:" + helperone)
                response_proc = w2n.convert(helperone)
                file_object = open('db.txt', 'a')   #Schreiben auf Liste
                file_object.write(str(response_proc)+";PV-Modul"+"\n")
                file_object.close()
                return{"sales_units":response_proc}

# Need to make this dynamic (if more than one page need & speak with pvoltec-CEO)
# class generate_PDF(Action):
# def name(self) -> Text:
#         return "action_generate_offer"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#     text = "Die Module werden laut Belegungsplan auf das Dach montiert. Kabeleinführung wird bauseitens gestellt. Alle Teile werden Korrosions- und UV-beständig ausgeführt."
#     flow_obj = []
#     tdata = [['Posi-','Menge','Einheit','Artikelbezeichnung','Einzel', 'Gesamt'],
#             ['tion','','','','-preis','-preis']]
#     counter = 0
#     with open("db.txt") as f1:
#         csvdata = csv.reader(f1, delimiter=";")
#         for row in csvdata:
#             data = []
#             counter = counter + 1
#             posnr = counter
#             menge = row[0]
#             einheit = 'Stück'
#             ANR = row [1]
#             preisjeeinheit = "1500,99 €"
#             preis = "999,99 €"
#             data.append(posnr)
#             data.append(menge)
#             data.append(einheit)
#             data.append(ANR)
#             data.append(preisjeeinheit)
#             data.append(preis)
#             print(data)
#             tdata.append(data)

#     tstyle = TableStyle([("BOX",(0,0),(-1,-1), 1, colors.black)])
#                         #("GRID", (0,0), (-1,-1),1, colors.blue)])
#     print(tdata)
#     title_of_pdf = "PV-Offer_" + dt.datetime.now().strftime("%Y_%b_%d_%H_%M_%S") +".pdf"
#     pdf = SimpleDocTemplate(title_of_pdf) 

#     t = Table(tdata)
#     t.setStyle(tstyle)
#     flow_obj.append(t)
#     pdf.build(flow_obj)
#     yourStyle = ParagraphStyle('yourtitle',
#                             fontName="Times-Bold",
#                             fontSize=12,
#                             alignment=2,
#                             spaceAfter=14)
    
#     rightAl = ParagraphStyle('right_normal',
#                             fontName="Times",
#                             fontSize=12,
#                             alignment=2,
#                             spaceAfter=6)
#     # t.setStyle(tstyle)
#     # flow_obj.append(t)
#     styles = getSampleStyleSheet()
#     flowables = [
#                 Paragraph('Angebot Photovoltaik Böckl', styles['Title'],),
#                 Spacer(1 * cm, 1* cm),
#                 Paragraph('1.11 PV-Module', styles['Heading2']),
#                 Spacer(1 * cm, 1* cm),
#                 Paragraph('1.12 Verkabelung', styles['Heading2']),
#                 Paragraph('Verkabelungen sind prinzipiell fertigverlegt und angeschlossen anzubieten. Der angebotene \nPreis inkludiert alle notwendigen Materialien, welche für eine Normgerechte Verlegung \n notwendig sind.Des Weiteren sind alle Verbindungselemente (Steckverbinder, Klemmen, \nSammelkästen) in den Preis einzurechnen.', styles['Normal']),
#                 Paragraph('1.2 Montagesystem', styles['Heading2']),
#                 Paragraph(text, styles['Normal']),
#                 Spacer(1 * cm, 1 * cm),
#                 t,
#                 Spacer(1 * cm, 1 * cm),
#                 Paragraph('Summe Netto: 20.000,00 €', rightAl),
#                 Spacer(1 * cm, 1 * cm),
#                 Paragraph('Umsatzsteuer 19,00%: 3.800,00 €', rightAl),
#                 Paragraph('Rechnungsbetrag: 23.800,00 €', yourStyle),
#                 Paragraph('1.3 Wechselrichter', styles['Heading2']),
#                 Paragraph('Der Wechselrichter wird komplett montiert und angeschlossen. Stringwechselrichter für \nNetzeinspeisung ins Niederspannungsnetz (230V/400V). Dem Angebot sind sämtliche \nNormungsnachweise und Konformitätserklärungen beizulegen.', styles['Normal']),
#                 Paragraph('Text after spacer'),

#     ]
#     def onFirstPage(canvas, document):
#         canvas.drawCenteredString(100,100, 'Text drawn with onFirstpage')
    
#     pdf.build(flowables, onFirstPage=onFirstPage)
    

class PDF(FPDF):
  def header(self):
     with open('bauvorhaben.txt') as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
     # logo changes made 0305
     self.image('UI_images/Logo_photovoltec.JPG', 112, 20, 80)
     self.set_font('times', 'I', 14)
     #Title
     self.set_text_color(0,80,180)
     self.cell(5, 20, '-Photovoltaikanlagen -Überwachung -Service', align='L')
     self.cell(5, 40, '-Monitoring -Montage -Verkauf', align='L')
     self.set_text_color(0,0,0)
     self.set_font('times', 'UB', 16)
     self.cell(0, 80, f'RECHNUNG', align='R')
     self.set_font('times', '', 14)
     today = dt.datetime.today()
     datum = today.strftime("%d.%m.%Y")
     self.cell(0,100,'Datum:       '+ datum+ '', align='R')
     self.cell(0,110,'Rechnungsnummer:                         ', align='R')
     self.cell(0,120,'Kundennummer:                         ', align='R')
     self.cell(0,130,'Placeholder:                         ', align='R')
     self.set_x(10)
     self.set_y(45)
     self.set_font('times', '', 9)
     self.cell(0,5,'Photovoltec, Schlossallee 15, 88279 Amtzell', align='L') # PLZ und Stadt
     self.set_y(55)
     self.set_font('times', '', 14)
     self.cell(0,0,lines[0], align='L') # Anschrift erste Zeile
     self.set_y(62)
     self.cell(0,0,lines[1], align='L') # Anschrift zweite Zeile
     self.set_y(65)
     self.cell(0,5,lines[2] + ' - ' + lines[3], align='L') # PLZ und Stadt
     self.set_y(70)
     self.cell(0,5,'DEUTSCHLAND', align='L') # PLZ und Stadt
     self.set_y(85)
     self.set_font('times', 'B', 14)
     self.cell(0,0,'Bauvorhaben: ' + lines[0], align='L')
     self.set_font('times', '', 14)
     self.line(10,90,200,90)
     self.set_y(89)
     self.line(10,90,200,90)
     self.set_fill_color(0,80,180)
     self.cell(0,10, 'Pos | Artikelbezeichnung                                       |Menge |   Preis je | Summe | MwSt. |  Gesamt')   #TO-DO
     # line break
     self.set_y(99)
     self.line(10,100,200,100)
     self.ln(8)
     file.close()

  def footer(self):
     self.ln(5)
     self.set_y(-70)
     self.line(5, 250, 200, 250) 
     self.set_y(-75)
     self.line(5, 250, 200, 250) 
     self.set_y(-65)
     self.set_font('times', 'I', 12)
     today = dt.datetime.today()
     datum = today.strftime("%d.%m.%Y")
     zahlungsfrist = today + dt.timedelta(days=21)
     zf = zahlungsfrist.strftime("%d.%m.%Y")
     self.cell(0,0,'Wir bitten um Rechnungsausgleich bis spätestens '+ zf + ' ohne Abzug', align='L')
     self.set_x(10)
     self.cell(0,10,'Bei den aufgeführten Leistungen handelt es sich um sonstige Leistungen EG nach §13b UStG', align='L')
     self.set_x(10)
     self.cell(0,20,'Der Leistungsempfänger schuldet die Umsatzsteuer. Es gilt die Steuerschuldnerschaft des ', align='L')
     self.set_x(10)
     self.cell(0,30,'Leistungsempfängers (Revers-Charge).', align='L')
     self.set_x(15)
     self.set_font('times', 'B', 12)
     self.ln(5)
     self.cell(0,40,f'Bankverbindung:', align='L')
     self.set_font('times','I',10)
     self.cell(0,45,'Inh. C. Schmidt', align='R')
     self.cell(0,51,'GXXXXXXXXX X4', align='R')
     self.cell(0,57,'8827X AmtXXXX', align='R')
     self.cell(0,63,'Tel: XXXX XXXXXXXX', align='R')
     self.cell(0,70, 'email: XXXX@XXXXXXXXxxx.de', align='R')
     self.cell(0,77,'Ust-IdNr:: DEXXXXXXXXXX', align='R')

     #set position of the footer
     self.set_y(-15)
     self.set_font('times', 'I', 10)
     #Page number
     self.cell(0,10,f'Seite {self.page_no()}/{{nb}}', align='R')

#  # create FPDF object
#  # Layout ('P','L')
#  # Unit ('mm','cm','in')
#  # format ('A3', 'A4' (default), 'A5')

#
#class ActionHelloWorld(Action):
#
#    def name(self) -> Text:
#        return "action_hello_world"

#    def run(self, dispatcher: CollectingDispatcher,
#            tracker: Tracker,
#            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#        dispatcher.utter_message(text="Hello World!")
#
#        return []

#class ActionFetchType(Action):
#    def name(self) -> Text:
#        return "action_fetch_type"

#    def run(self, dispatcher: CollectingDispatcher,
#            tracker: Tracker,
#            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#        dispatcher.utter_message(text="Type fetched")
#        return []