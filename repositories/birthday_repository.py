from typing import Optional, List
from datetime import datetime

class Birthday:
    def __init__(self, user_id: int, birthday: str):
        self.user_id = user_id
        self.birthday = birthday

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "birthday": self.birthday
        }

    @staticmethod
    def from_dict(data: dict) -> 'Birthday':
        return Birthday(
            user_id=data["user_id"],
            birthday=data["birthday"]
        )

class BirthdayRepository:
    def __init__(self, collection):
        self.collection = collection

    async def save_birthday(self, birthday: Birthday) -> None:
        self.collection.update_one(
            {"user_id": birthday.user_id},
            {"$set": birthday.to_dict()},
            upsert=True
        )

    async def get_birthday(self, user_id: int) -> Optional[Birthday]:
        data = self.collection.find_one({"user_id": user_id})
        return Birthday.from_dict(data) if data else None

    async def get_all_birthdays(self) -> List[Birthday]:
        return [Birthday.from_dict(data) for data in self.collection.find()]

    async def remove_birthday(self, user_id: int) -> None:
        self.collection.delete_one({"user_id": user_id})

    async def get_birthdays_in_range(self, start_date: datetime, end_date: datetime) -> List[Birthday]:
        birthdays = await self.get_all_birthdays()
        in_range = []
        
        for birthday in birthdays:
            bday = datetime.strptime(birthday.birthday, '%Y-%m-%d')
            # Compare only month and day
            bday = bday.replace(year=start_date.year)
            if start_date <= bday <= end_date:
                in_range.append(birthday)
            
            # Check next year if range crosses year boundary
            if start_date.year != end_date.year:
                bday = bday.replace(year=end_date.year)
                if start_date <= bday <= end_date:
                    in_range.append(birthday)
                    
        return in_range