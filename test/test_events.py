import unittest
from unittest.mock import MagicMock, patch
from database.events import (
    update_db_event,
    add_db_event,
    delete_db_event,
    get_db_event,
    get_db_events,
    get_all_db_events,
)
from models import Event


class TestEvents(unittest.TestCase):
    @patch("events.DB")
    def test_update_db_event(self, mock_db):
        mock_event = Event(event_id="123", name="Test Event")
        mock_db.database.events.update_one.return_value = mock_event
        result = update_db_event("123", mock_event)
        self.assertEqual(result, mock_event)

    @patch("events.DB")
    def test_add_db_event(self, mock_db):
        mock_event = Event(event_id="123", name="Test Event")
        mock_db.database.subscriptions.find_one.return_value = {
            "_id": "123",
            "events": [],
        }
        result = add_db_event("123", mock_event)
        self.assertEqual(result, mock_event)

    @patch("events.DB")
    def test_delete_db_event(self, mock_db):
        mock_db.database.events.delete_one.return_value = MagicMock(deleted_count=1)
        result = delete_db_event("123")
        self.assertEqual(result, 1)

    @patch("events.DB")
    def test_get_db_event(self, mock_db):
        mock_event = Event(event_id="123", name="Test Event")
        mock_db.database.events.find_one.return_value = mock_event
        result = get_db_event("123")
        self.assertEqual(result, mock_event)


if __name__ == "__main__":
    unittest.main()
