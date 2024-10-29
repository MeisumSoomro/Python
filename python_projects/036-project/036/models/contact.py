from datetime import datetime

class Contact:
    def __init__(self, name, phone, email, address, category="General"):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.category = category
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "category": self.category,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        contact = cls(
            data["name"],
            data["phone"],
            data["email"],
            data["address"],
            data.get("category", "General")
        )
        contact.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return contact 