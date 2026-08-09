from typing import Any, Dict, List, Text
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class MenuReservasiKesehatan(Action):
    def name(self) -> Text:
        return "action_menu_reservasi_kesehatan"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(response = "utter_menu_reservasi_kesehatan_ok")
        pilihan_menu = tracker.get_slot("menu_reservasi_kesehatan")
        dispatcher.utter_message(json_message={"context": "reservasi_kesehatan"})
        
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
            case "Prosedur Reservasi Kesehatan":
                if fetch_peraturan_api(tracker.sender_id, "reservasi_kesehatan_prosedur"):
                    return [SlotSet("return_value", "api_success")]
                return [SlotSet("return_value", "Prosedur Reservasi Kesehatan")]
            case "Persyaratan Reservasi Kesehatan":
                if fetch_peraturan_api(tracker.sender_id, "reservasi_kesehatan_persyaratan"):
                    return [SlotSet("return_value", "api_success")]
                return [SlotSet("return_value", "Persyaratan Reservasi Kesehatan")]
            case "Transaksi Reservasi Kesehatan":
                return [SlotSet("return_value", "Transaksi Reservasi Kesehatan")]
            case "Hasil Reservasi Kesehatan":
                if fetch_peraturan_api(tracker.sender_id, "reservasi_kesehatan_hasil"):
                    return [SlotSet("return_value", "api_success")]
                return [SlotSet("return_value", "Hasil Reservasi Kesehatan")]
            case _:
                return []
