async def test_conversation_history_storage(mocker):
    mock_mongo_collection = mocker.Mock()
    mocker.patch('pymongo.MongoClient', return_value=mock_mongo_collection)
    await on_message(mock_message)
    mock_mongo_collection.update_one.assert_called_with(...)
