async def test_chatgpt_integration(mocker):
    mocker.patch('openai.OpenAI.chat.completions.create', return_value={'choices': [{'message': {'content': 'Response'}}]})
    response = await chat_with_gpt("Hello")
    assert response == "Response"
