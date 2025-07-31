// Находится в пакете: org.example.database.model
package org.example.database.model;

// Теперь это просто класс для хранения данных (POJO)
public class User {
    private Long telegramId;
    private String playerTag;

    // Getters & Setters
    public Long getTelegramId() { return telegramId; }
    public void setTelegramId(Long telegramId) { this.telegramId = telegramId; }
    public String getPlayerTag() { return playerTag; }
    public void setPlayerTag(String playerTag) { this.playerTag = playerTag; }
}