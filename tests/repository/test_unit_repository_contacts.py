from datetime import date, timedelta
import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema

from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    search_contacts,
    get_birthdays,
)


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(
            id=1,
            username="test_user",
            email="test_email_1@example.com",
            password="test_password",
            confirmed=True,
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name="test_contact_1",
                last_name="contact_last_name_1",
                phone_number="123456",
                user_id=self.user,
            ),
            Contact(
                id=2,
                first_name="test_contact_2",
                last_name="contact_last_name_2",
                phone_number="456789",
                user_id=self.user,
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact(
            id=1,
            first_name="test_contact_1",
            last_name="contact_last_name_1",
            phone_number="123456",
            user_id=self.user,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(1, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactSchema(
            first_name="test_user_1",
            last_name="user_last_name_1",
            phone_number="123456",
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.user_id, self.user.id)

    async def test_update_contact(self):
        contact_id = 1
        body = ContactUpdateSchema(
            first_name="test_user_1",
            last_name="user_last_name_1",
            phone_number="123456",
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=contact_id,
            first_name="test_contact_1",
            last_name="contact_last_name_1",
            phone_number="123456",
        )
        self.session.execute.return_value = mocked_contact

        result = await update_contact(contact_id, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.phone_number, body.phone_number)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            first_name="test_contact_1",
            last_name="contact_last_name_1",
            phone_number="123456",
        )
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.assertIsInstance(result, Contact)

    async def test_search_contacts(self):
        first_name = "test_contact_1"
        last_name = "contact_last_name_1"
        email = "test_email_1@example.com"
        contacts = [
            Contact(
                id=1,
                first_name="test_contact_1",
                last_name="contact_last_name_1",
                email="test_email_1@example.com",
                phone_number="123456",
                user_id=self.user,
            ),
            Contact(
                id=2,
                first_name="test_contact_2",
                last_name="contact_last_name_2",
                email="test_email_2@example.com",
                phone_number="456789",
                user_id=self.user,
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result_first_name = await search_contacts(
            first_name, None, None, db=self.session, user=self.user
        )
        result_last_name = await search_contacts(
            None, last_name, None, db=self.session, user=self.user
        )
        result_email = await search_contacts(
            None, None, email, db=self.session, user=self.user
        )
        self.assertEqual(result_first_name, contacts)
        self.assertEqual(result_last_name, contacts)
        self.assertEqual(result_email, contacts)

    async def test_get_birthdays(self):
        today = date.today()
        upcoming_date_1 = today + timedelta(days=5)
        upcoming_date_2 = today + timedelta(days=15)
        contacts = [
            Contact(
                id=1,
                first_name="test_contact_1",
                last_name="contact_last_name_1",
                phone_number="123456",
                birthday=upcoming_date_1,
                user_id=self.user,
            ),
            Contact(
                id=2,
                first_name="test_contact_2",
                last_name="contact_last_name_2",
                birthday=upcoming_date_2,
                phone_number="456789",
                user_id=self.user,
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_birthdays(self.session, self.user)
        self.assertEqual(result[0].id, contacts[0].id)


if __name__ == "__main__":
    unittest.main()
