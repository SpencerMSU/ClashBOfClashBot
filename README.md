# ClashBot - Clash of Clans Telegram Bot

A Java-based Telegram bot for Clash of Clans players and clans.

## Features

- **Player Management**: Link your Clash of Clans account and view player profiles
- **Clan Information**: View clan details, member lists, and statistics
- **War Tracking**: Monitor current wars, war history, and Clan War League (CWL)
- **Notifications**: Get notified about important clan events
- **Data Persistence**: SQLite database for storing user accounts and war data

## Prerequisites

- Java 11 or higher
- Maven 3.6+
- Telegram Bot Token (from @BotFather)
- Clash of Clans API Token (from https://developer.clashofclans.com)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SpencerMSU/ClashBOfClashBot.git
   cd ClashBOfClashBot
   ```

2. **Configure the application**
   ```bash
   cp src/main/resources/config.properties.template src/main/resources/config.properties
   ```
   
   Edit `src/main/resources/config.properties` and fill in your tokens:
   ```properties
   bot.token=YOUR_TELEGRAM_BOT_TOKEN_HERE
   bot.username=YOUR_BOT_USERNAME_HERE
   coc.api.token=YOUR_COC_API_TOKEN_HERE
   ```

3. **Build the project**
   ```bash
   mvn clean compile
   ```

4. **Run the bot**
   ```bash
   mvn exec:java -Dexec.mainClass="org.example.Main"
   ```

   Or build a JAR and run it:
   ```bash
   mvn package
   java -jar target/MainPr-1.0-SNAPSHOT-jar-with-dependencies.jar
   ```

## Project Structure

```
src/main/java/org/example/
├── Main.java                           # Application entry point
├── bot/                               # Telegram bot components
│   ├── ClashBot.java                  # Main bot class
│   ├── handlers/                      # Message and callback handlers
│   ├── view/                          # Message generation
│   └── ...
├── cocapi/                            # Clash of Clans API client
│   ├── CocApiClient.java              # API client implementation
│   └── dto/                           # Data transfer objects
├── config/                            # Configuration management
├── database/                          # Database services and models
└── ...
```

## Bot Commands

- `/start` - Start the bot and show main menu
- Use inline keyboards to navigate through features:
  - **Profile** - Manage player accounts and view profiles
  - **Clan** - Access clan information and war data
  - **Notifications** - Configure bot notifications

## Dependencies

- **Telegram Bots API**: `org.telegram:telegrambots:6.9.7.1`
- **HTTP Client**: `com.squareup.okhttp3:okhttp:4.12.0`
- **JSON Processing**: `com.fasterxml.jackson.core:jackson-databind:2.17.1`
- **Database**: `org.xerial:sqlite-jdbc:3.46.0.0`
- **Web Scraping**: `org.jsoup:jsoup:1.17.2`
- **Logging**: `org.slf4j:slf4j-simple:2.0.13`

## Configuration

The bot requires the following configuration in `config.properties`:

- `bot.token`: Your Telegram bot token from @BotFather
- `bot.username`: Your bot's username (without @)
- `coc.api.token`: Your Clash of Clans API token

## Database

The bot uses SQLite database (`clashbot.db`) to store:
- User account links (Telegram ID to Clash of Clans tag)
- War history and statistics
- Attack data

The database is automatically initialized on first run.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.