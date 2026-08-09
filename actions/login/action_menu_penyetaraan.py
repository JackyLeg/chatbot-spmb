from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuPenyetaraan(Action):
    def name(self) -> Text:
        return "action_menu_penyetaraan"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(response = "utter_menu_penyetaraan_ok")
        pilihan_menu = tracker.get_slot("menu_penyetaraan")
        dispatcher.utter_message(json_message={"context": "penyetaraan"})
        
        def fetch_peraturan_api(sender: str, context_name: str) -> bool:
            try:
                payload = {
                    "IdLogin": sender,
                    "context": context_name
                }
                response = requests.post(
                    "https://sismob.trisakti.ac.id/api/get-peraturan",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == 200 and "body" in data and "data" in data["body"] and data["body"]["data"]:
                        aturan = data["body"]["data"].get("aturan")
                        if aturan:
                            dispatcher.utter_message(text=aturan)
                            return True
            except Exception as e:
                print(f"Failed to fetch from get-peraturan API: {e}")
            return False

        match pilihan_menu:
            case "Prosedur Penyetaraan":
                if fetch_peraturan_api(tracker.sender_id, "penyetaraan_prosedur"):
                    return [SlotSet("return_value", "api_success")]
                return [SlotSet("return_value", "Prosedur Penyetaraan")]
            case "Persyaratan Penyetaraan":
                if fetch_peraturan_api(tracker.sender_id, "penyetaraan_persyaratan"):
                    return [SlotSet("return_value", "api_success")]
                return [SlotSet("return_value", "Persyaratan Penyetaraan")]
            case "Hasil Penyetaraan":
                if fetch_peraturan_api(tracker.sender_id, "penyetaraan_hasil"):
                    return [SlotSet("return_value", "api_success")]
                return [SlotSet("return_value", "Hasil Penyetaraan")]
            case _:
                return []
