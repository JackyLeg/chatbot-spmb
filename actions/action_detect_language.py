from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class ActionDetectLanguage(Action):
    def name(self) -> Text:
        return "action_detect_language"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get the latest message text
        user_text = tracker.latest_message.get("text", "")
        if not user_text:
            return [SlotSet("language", "id")]

        text_lower = user_text.lower().strip()

        # Keywords for voting
        english_keywords = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening", 
            "how", "what", "is", "please", "help", "menu", "exam", "card", "agreement", 
            "payment", "finance", "withdraw", "transfer", "discount", "alumni", "health",
            "registration", "admission", "apply", "schedule", "document", "procedure", "requirements"
        ]
        indonesian_keywords = [
            "halo", "hai", "selamat", "pagi", "siang", "sore", "malam", "apa", "bagaimana",
            "tolong", "bantu", "menu", "pendaftaran", "kartu", "ujian", "hasil", "seleksi",
            "perjanjian", "pembayaran", "keuangan", "undur diri", "pindah prodi", 
            "diskon", "penyetaraan", "kesehatan", "dokumen", "jadwal", "syarat", "prosedur"
        ]

        words = text_lower.split()
        en_score = sum(1 for word in words if word in english_keywords)
        id_score = sum(1 for word in words if word in indonesian_keywords)

        # Multi-word phrases
        for kw in ["good morning", "good afternoon", "good evening", "how are you", "help me"]:
            if kw in text_lower:
                en_score += 2
        for kw in ["selamat pagi", "selamat siang", "selamat sore", "selamat malam", "apa kabar"]:
            if kw in text_lower:
                id_score += 2

        # Set slot value
        detected_lang = "en" if en_score > id_score else "id"
        
        return [SlotSet("language", detected_lang)]
