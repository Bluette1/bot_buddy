Here's an updated README for your BotBuddy project hosted at `https://github.com/Bluette1/bot_buddy`:

```markdown
# BotBuddy

## Description

**BotBuddy** is a versatile Discord bot designed to assist users with coding inquiries, manage help requests, and foster engaging community interactions. Utilizing the capabilities of ChatGPT and MongoDB, BotBuddy can answer programming questions, maintain user profiles, and create a supportive environment for learning and collaboration.

## Features

- **User Profile Management:** Create and manage user profiles to store personal information and preferences.
- **Interactive Help Requests:** Users can submit help requests, which can be prioritized and tagged for better organization.
- **Code Assistance:** Ask coding questions and receive detailed explanations or code snippets from ChatGPT.
- **Persistent Conversations:** Maintain context in conversations and retrieve previous interactions seamlessly.
- **Fun Interactions:** Enjoy random jokes, quotes, and engaging content through simple commands.
- **Admin Tools:** Admins can manage commands, view analytics, and schedule community events.
- **Community Engagement:** Features like polls, mentorship programs, and user recognition to foster a vibrant community.

## Installation

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [MongoDB](https://www.mongodb.com/try/download/community) (local or cloud)
- [Discord Bot Token](https://discord.com/developers/applications) (create an application and get your bot token)
- [OpenAI API Key](https://platform.openai.com/signup) (for ChatGPT integration)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Bluette1/bot_buddy.git
   cd bot_buddy
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your environment variables:
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token
   MONGODB_URI=your_mongodb_uri
   OPENAI_API_KEY=your_openai_api_key
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

- Use `!ask` to start a conversation with ChatGPT.
- Manage your profile with `!profile`.
- Submit help requests using `!help`.
- Get coding assistance with `!code [your question]`.

For a full list of commands, use `!commands` to display available commands and their descriptions.

## Contributing

We welcome contributions! Please follow these steps to contribute to BotBuddy:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them.
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch.
   ```bash
   git push origin feature/YourFeature
   ```
5. Create a pull request detailing your changes.

[User Stories](https://www.notion.so/BotBuddy-117e6a4d98f28032a7bcdaa360823cfb?pvs=4)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Discord.py](https://discordpy.readthedocs.io/en/stable/) for Discord bot development.
- [OpenAI](https://openai.com/) for the ChatGPT integration.
- [MongoDB](https://www.mongodb.com/) for data storage.

## Contact

For any inquiries or support, please reach out via [your-email@example.com].
```
