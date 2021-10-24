# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import logging
import re
from typing import Any, Text, Dict, List

from rasa.core.actions.forms import FormAction
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormAction,FormValidationAction,REQUESTED_SLOT
from rasa_sdk.events import AllSlotsReset, SlotSet ,EventType, SessionStarted, ActionExecuted



class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Hello World!")
        return []
class ValidateLetterForm(FormValidationAction):
    def name(self)-> Text:
        return "validate_letter_form"
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        letter_type=tracker.get_slot("letter")
        if letter_type =="confirmation" or letter_type=="both":
            return slots_mapped_in_domain+["address"]
        else:
            return slots_mapped_in_domain
    async def extract_address(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Dict[Text, Any]:
        last_intent=tracker.get_intent_of_latest_message(True)
        slot_address_value=None
        if last_intent=="letter_address":
            slot_address_value=tracker.get_slot("address")
        return {"address":slot_address_value}
    def validate_fullname(self,value:Any,dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict")->Dict[Text,Any]:
        fullname_regex="[a-zA-Z]{3,}(?: [a-zA-Z]+)?(?: [a-zA-Z]+)?(?: [a-zA-Z]+)?(?: [a-zA-Z]+)"
        if  (re.search(fullname_regex,value.lower())):
            return {"fullname":value.lower()}
        else:
            dispatcher.utter_message(text="Please provide valid name")
            return {"fullname":None}
    def validate_matric_number(self,value:Any,dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict")->Dict[Text,Any]:
        matric_number_regex="\d{5,8}[/][1,2]"
        if re.search(matric_number_regex,value):
            return{"matric_number":value}
        else:
            dispatcher.utter_message(text="Please provide valid matric no such as:1729998/1")
            return {"matric_number": None}
    def validate_passport_number(self,value:Any,dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict")->Dict[Text,Any]:
        passport_number_regexes=["[A-Z]{2}[0-9]{7,12}","\d[A-Za-z0-9]{9}D[^A-Za-z0-9]","[AHKE]\d{8}\D","[A-Z]{1}[0-9]{7,12}","\d{6}\-\d{2}\-\d{4}","\d{9}\D"]
        combined = "(" + ")|(".join(passport_number_regexes) + ")"
        if re.match(combined, value):
            return {"passport_number",value}
        else:
            dispatcher.utter_message(text="Please provide valid passport number or IC")
            return {"passport_number": None}
    def validate_email(self,value:Any,dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict")->Dict[Text,Any]:
        email_regex="\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if re.fullmatch(email_regex,value):
            return {"email",value}
        else:
            dispatcher.utter_message(text="Please provide valid email")
            return {"email": None}
    def validate_address(self,value:Any,dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict")->Dict[Text,Any]:
        address_regex="(.*?)([\d]*)((?:\s[^\d,]*)*)[\s,]*(\s[\w]*)$"
        if re.match(address_regex,value):
            return {"address",value}
        else:
            dispatcher.utter_message(text="Please provide valid address")
            return {"address": None}
class SendLetter(Action):
    def name(self) -> Text:
        return "action_send_letter"
    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text=f'dear {tracker.get_slot("fullname")} your request for {tracker.get_slot("letter")} is pending \n with matric number:{tracker.get_slot("matric_number")} \n pass:{tracker.get_slot("passport_number")} ')
        return []
